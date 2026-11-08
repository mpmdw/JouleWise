# Opus cold review: readiness gate and guard replay (RUN_STATE 221)

Reviewer: Opus 5.5 subagent on the M4 Air, laptop lead session 1544c617, 2026-11-08 about 01:50 PST.
This is a cross-family review: Sol 6.1 built both tools. Nothing was run on the MBP. No restricted,
custody or night directory was read.

| Tool | Branch @ head | Verdict |
|---|---|---|
| Readiness gate (221.1) | `ops/2026-11-08-readiness-gate` @ `418caef39` | **ADMIT_WITH_FIXES**. Merge as an advisory check now. The "may not schedule while RED" rule binds only after F-R1 to F-R4 land. As built, it can never show W1 GREEN. |
| Guard replay (221.2) | `ops/2026-11-08-guard-replay` @ `5ed8ec672` | **ADMIT_WITH_FIXES** for the replay library, corpus and doc. **HOLD** for the trace recorder: it is a spec only, and must not be started until F-G5 lands. |

Manifest update: `configs/readiness/next_steps.json` was stale, because it still treated R1 as unarmed. It
is rewritten to the current state and pushed to `ops/2026-11-08-readiness-gate` as
`348d2412f` (see section 1.6).

One finding falls outside both tools, and the guard-replay work is what exposed it. It is in section 3.

---

## 1. Readiness gate (`scripts/readiness_next2.py`, `configs/readiness/next_steps.json`)

### 1.1 Tests

`python3.13 -B -m unittest tests.test_readiness_next2`: **17 OK, 15.9 s**. The module ran in its own
process.

The tests cover these cases:
- the arm-route RED;
- an opt-in skip counted as RED;
- a refused record with exit 0;
- a missing branch;
- a pinned commit;
- PREQUAL subsets;
- budget expiry;
- fetching from a local remote;
- the alarm arithmetic;
- the CLI.

No test covers an accepted expected failure, a step with no opt-in tests, or cross-step commit
consistency. These are the gaps that F-R1, F-R2 and F-R5 below fall into.

### 1.2 Would it have flagged R1's missing arm route days early?

**Yes, but only as a forcing function, not as a detector.**

Suppose the manifest had listed `[R0, R1]` from 11-06:
- The R1 row is RED, `no arm route`, because `arm.live_command` and `arm.synthetic` would have been
  null (`readiness_next2.py:206-207`).
- `critical_path_alarm` is on, because R1's earliest hour is R0's lower bound, which is under 24 h.
- That is about two days before item 218 (11-07 23:48 PST).

Two caveats:
1. **The gate cannot see that a route is absent.** It sees only that the lead has not entered a seam. A
   seam that is weak but passes, such as a `--help` probe with an `assert_json` that the seam writes
   itself, turns the row GREEN. The real detector now exists elsewhere: `--w1-next r1|w1` in the merged
   smoke kit (`joulewise/align/w1_prequal.py`). Its `arm-route` check reads `configs/align/v4/arm_routes.json`
   (`r1: status none` fails at the r1 gate), and its `arm-cli` check runs the production `install` against
   a fake host in 12 cases. The updated manifest uses that command as the synthetic seam for both steps.
   **Recommendation:** make `--w1-next <step>` the required seam for every ALIGN step, and keep only one
   copy of the readiness logic (CANONICAL rule).
2. **Alarm fatigue would have hidden it.** On 11-06 the R1 row would also have been RED for its kit
   fields, R1 slots and plan, all of which R1 itself produces (see F-R3). A real "no route" RED looks the
   same as an expected "waiting for upstream" RED, and the alarm is on in both cases. The lead would
   have seen a wall of RED with the alarm permanently on.

### 1.3 The current state (R1 armed, W1 next)

The manifest was stale. Its first step was R1, on `lane/2026-11-08-r1-arm` (the unfixed `5c0b79d31`, not the
armed `20e9edbc4`). R1 is now armed (items 225 and 227), so it is no longer a candidate step. The rewritten
manifest has two steps:
1. **W1 smoke**: `align/2026-11-08-w1-smoke-merged` pinned at `1d73b7f1d`.
2. **W1**: `align/2026-11-08-v4-r11` pinned at `8d0dabc73`.

C1 is a placeholder third entry. `mbp_available_at` is R1's earliest possible end, 2026-11-09T03:59Z
(t0 09:17Z plus the 67,371 s no-redo floor). It is not R1's expected end.

The run on the Air (offline, cached refs, budget raised to 3,000 s so that nothing is cut off) gave:

**RED, alarm on, both steps at +18.6 h** (689 s wall, contended Air: 335 s user + 238 s sys, 294 MB peak RSS; status JSON kept in the reviewer's scratchpad, not committed).

| Step @ commit | Row | Result | Class |
|---|---|---|---|
| W1 smoke @ `1d73b7f1d` | arm/launch (`--w1-next w1`, 204 s) | FAIL: `triage-staleness`, `triage-edited-bytes` (G1/G1b), `r1-w1-chain` (G2), `km003c-crash-radius` (G3), `kit-ready`, `receipt`, `w1-window-max`, `series-manifest`, `deadline` | G1-G3: **true** (fixed on v4-r11 `9891d679b` *after* the smoke merge); the rest pending-upstream |
| both | `kit:R0.reasoning_effort` and `kit --check` | RED: "R0.reasoning_effort stays a placeholder" | **TRUE, new catch** (below) |
| both | `kit:R1.*`, PREQUAL `kit`/`w1-plan`, `w1_plan.json`, `sizing_b5.json` | RED | pending-upstream (R1 output) |
| both | `r1_slots.json` | **GREEN** | **false GREEN**: the file is the `"source": "PENDING_R1_REHEARSAL"` template (F-R9) |
| both | R14/R15/R16 agreements | RED (absent from tree) | true |
| W1 @ `8d0dabc73` | arm/launch | RED: `w1_prequal.py`, `arm_routes.json` absent | **true**: smoke kit not on the W1 commit |
| W1 | `tests.align.test_w1_prequal` | RED (module absent) | true, same cause |
| both | `tests.align.test_v4_prequal` (36 tests) | RED: 3 skips "needs mlx_lm, SHADE deps and JW_PREQUAL_HF" | environment: the gate deletes every `JW_*` variable (F-R12) |
| both | `tests.align.test_v4_w1_synthetic` + `JW_WP22_FULL=1` (20 tests, 133 s) | RED: 1 expected failure | **false RED** (F-R1) |
| smoke | `test_w1_smoke` (24 s), `test_w1_prequal` (116 s), `test_v4_kit`, `test_v4_w1_plan`, PREQUAL `r0-config`, `d-pin-verifier` | GREEN | — |

**New true catch: the R0 and R1-runtime fills are not on the W1 line.** `5d9b66dd4` (`R0.reasoning_effort = "medium"`, item 218) and `d9d1098c6` (`r1_runtime.json` sensors) are ancestors of R1's `20e9edbc4` but **not** of `align/2026-11-08-v4-r11` or `-w1-smoke-merged`. Run the R1->W1 chain on the v4-r11 line as it stands and `kit-ready` keeps failing on `R0.reasoning_effort` even after every R1 field is filled. **Lead action before R1 ends (about 18 h):** merge `lane/2026-11-07-r1-kit-r0fill` (or the R1 line) into v4-r11. In the same integration, also merge the smoke kit forward and bring in #699 (section 3). Pin the result for both steps.

What the reds show:
- **True RED (useful):** the W1 commit `8d0dabc73` does not contain the smoke kit. `v4-r11` moved two
  commits (`9891d679b`, `8d0dabc73`) after the smoke kit was merged onto `2cce80ede`. So the smoke on
  `1d73b7f1d` does not exercise the code W1 will arm. W1-SMOKE.md Part B requires a `--w1-next w1` PASS
  at the exact HEAD the MBP runs. **Action (lead):** merge `v4-r11` into the smoke kit, or the reverse,
  so that a single commit carries both. Then pin that commit for both steps.
- **True RED (useful):** none of the R14, R15 or R16 agreement documents is in either tree. They live on
  `align/2026-11-08-w1-blockers-opus`, `-dct-series-merged`/`-opus` and `-condition-waits-opus`. Whether
  their implementations reached the W1 code is not established. One example is R15's
  `bytes_h_session.measurement_view` `neg8_reference` bug.
- **Expected RED (pending upstream):** `w1_plan.json` and `sizing_b5.json` (`r1_slots.json` is a false GREEN; see F-R9); the kit
  `R1.*` fields; the PREQUAL `kit` and `w1-plan` checks. None of these can exist until R1 ends.
- **False RED:** the WP22 accepted divergence (F-R1).

### 1.4 Findings

| ID | Sev | Where | Finding | Fix |
|---|---|---|---|---|
| F-R1 | **HIGH** (false RED, permanent) | `readiness_next2.py:305`; `TEST_RUNNER` `:42-43` | Every `expectedFailure` is RED. `tests.align.test_v4_w1_synthetic.InjectedWindowTests.test_collector_death_is_x4_and_episode_continues` is a documented **accepted** divergence (WP22 F3, against WP8 F2 `8ef3c30f4`). So the W1 rows can never be GREEN. Under READINESS.md's "may not be scheduled while RED", this would refuse W1 forever: the spurious refusal that 221 forbids. | Add a per-test `accepted_expected_failures: [{test, ruling}]`. Only exact listed ids pass. Any other expected failure stays RED, and so does an unexpected success, which means the divergence was fixed and the list is stale. Add a test for this. |
| F-R2 | **HIGH** (false RED, latent) | `:294-295` | A step must list at least one opt-in (`env`) selector, or it is RED. Rule 221.4 sets out to remove opt-ins, so the better the repo gets, the more steps fail this check. | Require only that `tests` is non-empty. To keep the intent, cross-check against the opt-in audit ledger (`docs/perf/2026-11-08-optin-audit-results.json`): any ledger entry that names this step's modules must be listed. |
| F-R3 | **HIGH** (alarm fatigue) | `:356`, `:360`, evidence `:250-265`, kit `:238-245` | There is no "produced by an earlier step" state. Artefacts that R1 produces are RED, with the alarm on, for the whole of R1. The same happened for R0's outputs on the R1 row. A real missing route can't be told apart from "waiting for upstream". | Add `produced_by: <step id or 'R1'>` to evidence and kit fields. When the producer is earlier in the queue or running, the row is `PENDING_UPSTREAM`: it does not count as RED for the alarm and is shown separately. The step's synthetic seam must still pass using synthetic stand-ins; the `--w1-next` kit-ready, chain and WP22 probes already do this. Re-check the real artefact once the producer ends. The same applies to inputs that exist only at arm time, for example `--deadline-projection` from the installed plan and `--series-projection`: run the seam with a synthetic projection, or pass `--waive` with the pending reason. |
| F-R4 | MEDIUM (false RED) | `:154-160`, `:406` | When the shared budget runs out, the remaining required checks are RED, and the alarm fires. The default of 1,200 s is below the measured cost of two ALIGN steps (measured on the Air, below: 689 s wall for two steps). | When the budget runs out, mark the row UNKNOWN with `budget_exhausted`, never RED. Set the default from the measured runtime. Memoise per F-R7. |
| F-R5 | MEDIUM (false GREEN) | absent | Nothing checks that the smoke step and the long block share one commit. Rule 221.3 says "native smoke before every long block **after any code change**", but the gate would show both steps GREEN on different commits. That is exactly the situation today (section 1.3). | Add an optional `same_tree_as: "<step id>"` (or `smoke_for`) that requires equal commits, or tree equality outside `docs/`. A mismatch is RED. |
| F-R6 | MEDIUM (CI false RED) | `.github/workflows/readiness.yml:26-35` | Unlike `ci.yml:29-36` and `:165-170`, the workflow does not install `/bin/zsh`. The `arm_routes.json` installer probe and the zsh-driven tests need it, so they would fail on Ubuntu. It also has no `setup-python` and runs the runner image's python3 (3.12), while the repo runs 3.11 and 3.13. | Copy ci.yml's zsh step and use `actions/setup-python@v6` with 3.13. Then check one run with `workflow_dispatch` before trusting the 3-hourly status. |
| F-R7 | MEDIUM (cost/noise) | `readiness.yml:7-12`; `readiness-air.plist.md:29` | The push triggers on `lane/**`, `align/**` and `fix/**` (117 such refs on 11-07/08) start a run of about 15-20 min that tests the **manifest's** branches, not the pushed commit. So almost every run is redundant, and every lane commit gets a red ✗, which teaches people to ignore red. Minutes cost nothing because the repo is public. The Air job runs the same full pass every hour, at about 9.5 CPU-min per run (335 s user + 238 s sys, 294 MB peak RSS), about 16 % of one core-hour, every hour. | Drop the lane, align and fix push triggers. Keep `schedule`, `workflow_dispatch` and `push: main` filtered to `configs/readiness/**`. Memoise on the key (manifest sha256, resolved commits, gate sha). If the key is unchanged and the last result is under 3 h old, re-emit it with `cached: true`. Then hourly on the Air costs seconds. |
| F-R8 | LOW (guard) | absent | Nothing stops the gate itself from running on the MBP. | Exit 3 when `sysctl hw.model` is `Mac15,9`, or when `$M` or `~/night-align` exists. Compare the paths as strings only; never list them. |
| F-R9 | MEDIUM (false GREEN, observed) | `:254-263` | Evidence passes if the file merely exists. In the run, `r1_slots.json` was GREEN on both steps, but it is the `"source": "PENDING_R1_REHEARSAL"`, `"slots": null` template. A ruling that says HOLD would be GREEN too. | For `.json` evidence, apply the kit's `pending()` to the parsed file. Give every ruling entry a `contains` binding, for example the `RULING: ADMIT` line or the ruling id. |
| F-R12 | MEDIUM (false RED on the Air) | `:142-144` | `environment()` deletes every `JW_*` variable, including `JW_PREQUAL_HF`. The provisioned split tests can therefore never run, even on the Air where the lead has the D non-weight files. `test_v4_prequal`'s three `TokenizerTier` tests skip, which counts as RED. | Add a per-test `env_passthrough` allow-list, used only by the Air job. In CI, list such tests under a ruled `accepted_skips`, using the same mechanism as F-R1. |
| F-R10 | LOW | `:142-150` | The environment scrub removes `JW_`, `HF_`, `AWS_` and `GOOGLE_` but not `GITHUB_TOKEN`, `GH_TOKEN`, `OPENAI_*`, `ANTHROPIC_*` or `CODEX_*`. Lane code runs in children. | Change the scrub to allow-list only `PATH`, `LANG` and `LC_*`. |
| F-R11 | LOW | `:91-113` | If the gate is killed during a step, the temporary worktree stays registered in the clone. | Run `git worktree prune` at start-up. |

**Secrets:** none. The workflow has `permissions: contents: read` and reads no secrets. Its token stays in
the checkout's `.git/config`, where branch code run by the gate can read it. The repo is public, so the
risk is negligible. Still, set `persist-credentials: false`; `--fetch` needs no credentials on a public
repo. The status artefacts are public on a public repo. They hold synthetic test output only.

**MBP and sealed paths: none.** The gate runs only on the Air or in CI:
- children get `HOME`, `TMPDIR` and the caches set inside the scratch directory;
- `confined()` refuses absolute, traversal, `restricted/` and symlinked receipt paths;
- the `--w1-next` seam uses a fake host;
- the smoke kit compares `production_roots` as strings and never opens them.

F-R8 adds the missing refusal on the host itself.

### 1.5 To turn it on

1. **Builder (Sol or Opus seat), before merge:** F-R1 to F-R4 and F-R6, each with a test. F-R5 and F-R7
   are strongly recommended in the same PR.
2. **Merge target: `main`.** Use a PR with the gate ledger. Keep the check non-required (READINESS.md
   already says so). Merge the updated manifest at the same time.
3. **Lead:**
   - keep `next_steps.json` current at every ruling, pin or lane change, as part of the same change;
   - before R1 ends, do one integration onto v4-r11: the R0 and R1-runtime fills (`lane/2026-11-07-r1-kit-r0fill`), the smoke kit and #699. Then pin that one commit for both the W1 smoke and W1 (sections 1.3 and 3);
   - add `contains` bindings for the rulings;
   - add CW-1 as a step once it is scheduled.
4. **Air:** install the launchd template from `docs/ops/readiness-air.plist.md` in a dedicated clone under
   `~/code/CapstoneProject/jw-wt/` (not `~`). Only the lead does this, and only after F-R7: run every
   3 h, or hourly with memoisation.
5. **Magistrate:** nothing to install. Before arming a step, confirm that the gate's status names the
   exact commit being armed, is under 4 h old and is GREEN, or is RED only on rows the lead has ruled
   PENDING_UPSTREAM. Until F-R1 to F-R3 land, treat the gate as advisory only: the existing `--w1-next`
   PASS rule (W1-SMOKE.md) stays the binding check.
6. **Ed:** nothing.

### 1.6 Manifest update (pushed)

`ops/2026-11-08-readiness-gate` @ `348d2412f` (fast-forward on `418caef39`; only `next_steps.json`):
- **Steps:** W1 smoke (pinned `1d73b7f1d`), then W1 (pinned `8d0dabc73`), then C1 as a placeholder.
- **Synthetic seam for both:** `scripts/align_v4_prequal.py --w1-next w1`, asserting
  `prequal-w1.json` `status == PASS` and `next == w1`.
- **Evidence:** the smoke agreement, the R1→W1 chain runbook, the R14-R16 agreements (expected inside the
  W1 tree), the R1-produced artefacts, the signed registration receipt, and the native smoke PASS
  receipt for W1.
- **`mbp_available_at`:** 2026-11-09T03:59Z.
- **Notes:** the planning note records the smoke/W1 commit split and CW-1.

---

## 2. Guard replay (`joulewise/guard_replay*.py`, `scripts/guard_replay.py`, `docs/process/GUARD-REPLAY.md`)

### 2.1 Tests and reproduction

- `python3.13 -B -m unittest tests.test_guard_replay`: **34 OK, 3.9 s**, in its own process.
- `scripts/guard_replay.py collect` reproduces `docs/process/guard_replay/corpus.json` **byte for byte**
  (2.0 s).
- `run … --run-seconds 23400` reproduces `recorded-report.json` byte for byte (2.6 s). `run` on the
  synthetic fixture reproduces `synthetic-report.json` byte for byte.
- `run --require-qualified` exits 2, as the doc says it should.

The historical pins all check out:
- `165e12872` is the kit lane before #691.
- `5f817856b` is the first parent of the #699 merge `9c40e4e5d`.
- `9c40e4e5d` is #699, R0-L3.

### 2.2 Is the replay faithful to the real guard code?

**Mostly yes. It executes the real code, and nothing is re-implemented.** There are three qualifications.

- **Real code, executed.**
  - The historical adapters `exec` the original class and function ASTs from the pinned git blobs:
    `QuietGuard`, `Refused`, `CpuQuietProbe`, `require_quiet`, `NotQuiet`, `Ruling8Quiet` and
    `ContentionRedo` (`guard_replay.py:215-251`). Samplers are injected, and any uninjected I/O raises.
  - The dependencies `contention.py` and `prewindow.py` must match the clone's executable AST
    (`:66-77`).
  - The current adapters import `joulewise.hazards.contention`, `environment_admission` and
    `hazards.thermal` directly.
  - None of this is a copy of a predicate.
- **Q1: some replays only replay the recorded verdict (circular).**
  - For `quiet-prel3` and `quiet-l3`, the adapter replaces `QuietGuard._cpu_interval` with the busy list
    recorded in the receipt (`:270-276`). The CPU predicate itself (cumulative TIME over ≥30 s, the 0.05
    bar) **is not executed**; only the latch and decision code runs.
  - For `smc-pre691` and `smc-prel3` on receipts, the probe returns the recorded CPU dictionary
    (`:332`). The historical `require_quiet` refuses on `cpu.get("clean") is not True`, so the recorded
    `clean: false` decides the outcome.
  - Those replays reproduce the original outcome by construction. The doc admits this in general terms
    ("Receipt summaries can replay a decision but cannot revalidate its original sampler",
    GUARD-REPLAY.md:78-79), but its regression table (`:167-172`) still presents those rows as proof.
  - **Only `quiet-pre691` re-evaluates a predicate on recorded inputs:** named contaminant with ps
    `%CPU > 5` on the projected rows. The `snapshot`-channel paths, which run the real `CpuQuietProbe` and
    `contention.interval/Dwell/judge` on raw counters, are exercised only on the synthetic fixture.
- **Q2: the current adapters bind to the clone's tree, not to the commit the MBP runs** (`:482-486`).
  - The branch is cut from `main`.
  - `joulewise/environment_admission.py` and `joulewise/hazards/base.py` on `main` differ in executable
    AST from both R1's `20e9edbc4` and W1's `8d0dabc73`.
  - `contention.py` and `thermal.py` match in AST.
  - So the `display` adapter replays `main`'s predicate, not the one W1 runs.
  - The historical eras are hard-coded in `PINS` (`:32-34`), so a **candidate** guard can't be replayed
    without editing code.
- **Q3: the CPU-only adapters neutralise every other census.** The doc says so. A census-path refusal is
  therefore not covered: an agent, custody, launchd or process-census-unavailable refusal on routine
  macOS activity is out of scope.

### 2.3 The regression proof

The claim to check: would the pre-#691 QuietGuard and the pre-R0-L3 rules have been flagged?

- **Pre-#691 QuietGuard: shown, and the evidence is real.** The original predicate refuses both benign
  incidents, rerun3 (photoanalysisd) and rerun4 (mdworker). It also refuses reruns 5 and 6, which are
  labelled `unknown`. The input rows were already filtered to over-limit rows, which can only lower the
  refusal count, so 2 of 5 benign is a lower bound. The flag is robust.
- **Pre-R0-L3 SMC admission: reproduced, not demonstrated.** The 3 of 3 benign refusals (reruns 8, 9 and
  10, plus reruns 5 and 6 as unknown) come from replaying `clean: false` verdicts (Q1). That shows the
  receipts refused, which was already known. It does not show the predicate misfiring on idle input.
  The synthetic fixture shows the mechanism, but it is synthetic.
- **Ex ante, the replay would not have shown ABOVE_BOUND for the pre-L3 rule.** When the #691/#692 SMC
  rule shipped, the corpus held only reruns 1-4. For that rule those give `UNSUPPORTED` or `missing
  channel`, so the screen result is INSUFFICIENT.
  - Under rule 221.2, INSUFFICIENT means no gating without a lead ruling. **That requirement, not the
    replay itself, is what would have saved reruns 5, 6, 8, 9 and 10.**
  - Write the doc's claim that way. The next real lever is the recorder corpus (section 2.5).
- **Label policy undercounts (F-G3).** Only the five incidents named in Ed's brief are `benign`. Every
  other R0 attempt is `unknown` (`guard_replay_corpus.py:88-91`, `:115-117`). Refusals on runs labelled
  `unknown` never reach `ABOVE_BOUND` (`guard_replay.py:521-525`). Reruns 5 and 6 were protocol-idle
  real attempts on a quiet Mac, with no injected load and no agent. Under the doc's own rule (labels come
  from the operator schedule, not from the guard), they are benign.

### 2.4 Is the false-refusal bound sensible?

The bound is 5% per declared run, with the two-sided 95% Wilson upper endpoint at or below 5% on
complete, representative, independent benign runs. That needs 73 clean runs.

- **The direction is right.** Per run, not per sample, is correct. Treating selected incidents as
  refuting only, never licensing, is correct. Showing positive controls is correct.
- **As written it cannot be met.**
  - 73 runs × 23,400 s is about 475 h of idle MBP trace. Under item 213 (back-to-back windows) the MBP
    has short gaps, not days.
  - Slices of one long trace are correlated: the daily softwareupdated, trustkit and routined schedules.
  - So every guard change would default to a lead ruling, and the bound becomes ceremony.
- **Recommended (lead ruling):**
  1. **Size exposure per guard.** For an arm-time guard the exposure is its decision horizon, not the
     run: hazard arm has a 2,700 s cap, so 73 × 2,700 s is about 55 h, which is reachable. For a guard
     that runs inside the run, use the run length.
  2. **Shadow mode is the default route to qualification.** A new or changed refusing predicate first
     ships as **flag-only** on real runs. It records `would_refuse` with its inputs, and is promoted to
     refusing after N clean real runs (say 10) plus a replay on the recorder corpus, or by ruling. This
     builds a representative corpus from the windows themselves and costs zero MBP idle.
  3. **Keep the asymmetric block.** Any benign refusal on a recorded trace blocks, as now, but count
     protocol-idle real runs as benign (F-G3).
  4. **Use a one-sided 95% upper endpoint** (rule of three: 59 runs at zero refusals). This is minor.

### 2.5 Trace recorder: is the cost bound safe, and does it ever run during a window?

The spec is in GUARD-REPLAY.md:224-268. It is a spec only: nothing was installed. The proposed budget is
≤0.01 busy core averaged over 30 min, ≤64 MiB RSS and ≤256 MiB/day. Doing `ps -Ao …args` every 5 s,
`top -l 2` every 30 s and an `ioreg`/`pmset` pass every 60 s is plausibly about 0.005-0.012 core. That is
**at** the bar. The spec rightly requires a measured on/off check before use.

**It is not yet safe against running in a window. HOLD until F-G5:**
- "Stop the recorder itself on … window-start breach" (`:257-258`) names no mechanism.
- At about 0.005 core spread over its own processes, a leaked recorder is **below every contention
  flag** (0.05 CPU-s/s). Nothing would notice it inside a window. It would add a constant load to every
  DC-in reading, including the reference idles, the most sensitive rows.
- The existing between-window battery logger (`scripts/align_v4_battery_log.py`, "NO sampler during a
  window") relies on the same manual `stop --pidfile` runbook step and has no interlock either.

**Blinding.** The rule for this tool is process and timing fields only. The spec goes past that: SMC
**B0AC at 1 Hz**, `pmset -g batt`, and AppleSmartBattery current and ExternalConnected (`:237`, `:240`).
Battery current between windows is not outcome-bearing, so this is not a blinding breach. But it
duplicates the battery logger, and it widens the scope beyond what was asked. Drop it.

### 2.6 Findings

| ID | Sev | Where | Finding | Fix |
|---|---|---|---|---|
| F-G1 | MEDIUM (doc accuracy) | GUARD-REPLAY.md:167-181 | The regression table presents verdict replays as proof (Q1). The pre-L3 claim is reproduced, not demonstrated, and ex ante it would have been INSUFFICIENT. | Restate as in section 2.3. Mark each row "predicate re-evaluated" or "recorded verdict replayed". |
| F-G2 | **HIGH** (fidelity) | `guard_replay.py:32-34`, `:482-486` | The tool can't replay the **candidate** or **live** guard. Eras are hard-coded, and the current adapters read the clone's `main` tree. On `main`, `environment_admission.py` and `hazards/base.py` differ from R1 and W1. | Add `--rev <commit>` for every adapter, loading the module source by AST from that commit as `historical()` already does. The report binds that commit. The readiness gate can then run `guard_replay run --rev <step commit>` as a step test. |
| F-G3 | MEDIUM (false negative) | `guard_replay_corpus.py:88-91`, `:115-117`; `guard_replay.py:521-525` | Protocol-idle real attempts are labelled `unknown`, so their refusals never count. | Label by protocol: no injected load and a clean agent census at arm gives `benign_protocol`, counted in the false-refusal rate. Keep `unknown` only where the protocol itself is in doubt. |
| F-G4 | MEDIUM (policy) | GUARD-REPLAY.md:17-37 | The bound needs 73 run-length traces, which is unreachable under item 213. | Size exposure per guard, make shadow mode the default qualification, and use a one-sided bound (section 2.4). This is a lead ruling, not a code change. |
| F-G5 | **HIGH** (window safety, recorder) | GUARD-REPLAY.md:224-268 | There is no hard interlock against running in a window, the cool-down or the arm dwell. | (a) Each 5 s `ps` pass already lists processes. Exit immediately if any of these is present: `run_night.py`, `chain.zsh`, `hazard_monitor.py`, `km003c_monitor.py`, `launch_align_r0`, `align_v4_w1_smoke`, or a loaded `com.joulewise.night*` label (checked every 60 s). (b) A hard maximum lifetime, for example 4 h, then exit. (c) The pre-arm runbook step stops it idempotently, together with the battery logger, **before the R16 P1 cool-down floor starts**, not at t0. The arm path stops it rather than refusing, so no new refusing guard is added. (d) Its pidfile and journal live under a lead-chosen unrestricted directory outside `~`. |
| F-G6 | LOW (scope) | GUARD-REPLAY.md:237, `:240` | It records battery current, B0AC and ExternalConnected. | Drop these. The recorder is process, timing, thermal level and display state only. Battery guards replay from the existing battery-log JSONL. |
| F-G7 | LOW | `guard_replay.py:66-77` | Any executable change to `main`'s `contention.py` or `prewindow.py` makes every historical adapter fail. That is loud, which is good, but brittle. | Once F-G2 exists, load the dependencies from the pin as well. |
| F-G8 | INFO | inventory GUARD-REPLAY.md:97-135 | Most guards that gate R1 and W1 have no adapter: night_gate C3 (HID, power, battery, displaysleep, CPU_Speed_Limit), the quiet_admission v4 bind, the R1 ruling-8 redo, and the external-volume census. Those are the families most likely to refuse on routine macOS activity next. | Write adapters in this order: night_gate C3, then quiet_admission v4 bind. The recorder must capture exactly their inputs. |

**Blinding: clean.** Every frame key in `corpus.json` is a process, CPU or timing field, plus the fixture's
OS thermal level. Process commands are three `/System/...` daemon paths. There is no power, energy, NLL,
score or custody path. Numbers stay opaque until they are selected. **MBP and sealed paths: none.** `collect`
reads committed `origin/records/*` blobs through `git show`. `local_read` refuses `restricted`,
`night-*`, `jw-b5-*` and symlinks before it opens anything.

### 2.7 To turn it on

1. **Builder:** F-G1 and F-G2 (`--rev`), each with a test. F-G3 needs a lead label ruling first.
2. **Merge target: `main`.** The library, CLI, corpus, reports and doc are offline and touch nothing live.
3. **Lead rulings:** the bound restated per F-G4 (exposure per guard, shadow mode, one-sided bound),
   and the label policy (F-G3). Record them as a RUN_STATE item. Rule 221.2 then binds every PR that
   changes a refusing predicate.
4. **Recorder:** HOLD. A seat builds it to the F-G5 and F-G6 spec. After that:
   - the magistrate runs the 30 min on/off overhead check on the MBP **only in a between-window gap**:
     after R1 has finished and the post-R1 runbook steps are done, and before the P1 cool-down for the
     next arm;
   - it must never overlap an armed plan; item 227 (1) forbids any agent or extra work while R1 is armed.
   
   It turns on only if it is within budget.
5. **Ed:** nothing.

---

## 3. Finding outside both tools: R0-L3 is not on the R1 or W1 code line (MEDIUM, latent)

R0-L3 (#699, `9c40e4e5d`) makes the CPU checks a flag (QuietGuard) or a ruling-8 redo (SMC
`Ruling8Quiet`) instead of a refusal. It exists only on `lane/2026-11-05-align-pilot10-benign`.

It is **not an ancestor** of:
- R1's armed `20e9edbc4`;
- `align/2026-11-08-v4-r11` (`8d0dabc73`);
- `align/2026-11-08-w1-smoke-merged` (`1d73b7f1d`).

All three carry the **pre-L3** code:
- `r0_host.QuietGuard` raises `Refused("contaminating CPU contention: …")`;
- `smc_enumeration` has no `Ruling8Quiet` or `ContentionRedo`.

The guard-replay corpus shows this exact rule refusing benign incidents 3 of 3 times.

**Impact today: none on R1 or W1.** Those guards are used only by `r0_runner.py` and
`scripts/align_smc_enumerate.py`. R1's runtime imports only `host_snapshot`, and W1 uses neither.

**Risk:** any future R0 re-run from the v4 code line would bring back the refusals behind five lost
attempts. One trigger would be a new host epoch after an OS update. Another would be v5.

**Fix:** merge `9c40e4e5d` (or the lane) into `align/2026-11-08-v4-r11`. Add a readiness test
that pins it: `tests.align.test_r0_host`, run on the W1 commit, should assert flag-not-refuse. The two tools
together would catch this once F-G2 lands: `guard_replay run --rev <W1 commit> --guard quiet` gives
ABOVE_BOUND.

---

## Reproduce

```sh
# readiness (Air, offline)
python3.13 -B -m unittest tests.test_readiness_next2
python3.13 -B scripts/readiness_next2.py --budget-seconds 3000 --output /private/tmp/jw-readiness/status.json
# guard replay
python3.13 -B -m unittest tests.test_guard_replay
python3.13 -B scripts/guard_replay.py collect | cmp - docs/process/guard_replay/corpus.json
python3.13 -B scripts/guard_replay.py run docs/process/guard_replay/corpus.json --run-seconds 23400 | cmp - docs/process/guard_replay/recorded-report.json
# R0-L3 ancestry
git merge-base --is-ancestor 9c40e4e5d 20e9edbc4 || echo "L3 not in R1"
```
