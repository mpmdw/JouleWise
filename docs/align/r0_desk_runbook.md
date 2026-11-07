# ALIGN R0 daytime desk runbook

Run **on the measurement Mac only**, with no armed/active chain and all agent
apps/CLI sessions closed. This is selection data, not R1, thermal validation or
an arm authorization. Authority: council `219fb1515`, FINAL-DESIGN §§2.1, 2.2,
2.8 plus Amendment 1: **D only**; Qwen3-Next is dropped and Flash-Next is later.
Keep the pinned stack: Python measurement venv, mlx 0.31.2, mlx-lm 0.31.3,
transformers 5.12.1. Stage-1 B1/B2 from `d01288e25` is imported in this fix round;
reasoning effort uses `chat_template_kwargs={"reasoning_effort": ...}` on the
production endpoint and is included in its hashed template policy. Review the
integration before live R0. Do not run these commands from an
agent session. Full Amendment 1 was verified at `6eb1ff5be` in local Git objects.
The [2026-11-05 laptop-lead ruling](r0_step_test_ruling.md) replaces Amendment 1's
60 s SMC load with **300–1,200 s adaptive idle, 900 s load, 600 s recovery** (30–45 min),
as updated by the 2026-11-07 D1–D6 reconciled sensor decision.
The integrated #658 capture source is `58525031a`.
The v4 headless LaunchAgent and watchdog fence are WP10/WP11 integration work;
the Terminal launch example below does not satisfy that headless gate.

1. In Terminal at the integrated checkout, set the interpreter and config.
   The paths below are **examples to edit**, never auto-discovered. Model
   sources must be complete local directories; revision pins are built in.
   Materialized mirrors and HF hub `models--*/snapshots/<revision>` roots are
   supported. Snapshot file links must resolve to regular `models--*/blobs/*`
   targets inside the same hub root; directory links and escapes refuse.
   Prepare/download/hash the pinned mirrors separately;
   this script never downloads. SHADE must already have its pinned cache.

   Set `anchor_source` to the 30B anchor mirror or HF snapshot at revision
   `d388dead1515f5e085ef7a0431dd8fadf0886c57`; it is inventoried alongside D.

   Set `measurement_hw_model` to the lead-verified measurement Mac's exact
   `sysctl -n hw.model` value. The placeholder refuses model work. Every model
   subset requires this identity plus at least 128 GiB physical RAM before load.

   `smc_step` configures `idle_seconds`, `idle_max_seconds`, `load_seconds`,
   `recovery_seconds`; omitted fields default to 300/1200/900/600. Idle extends
   until every temperature key passing D1(a) and the stale rule,
   with trailing residual SD ≤0.15 °C, has absolute
   trailing-60 s OLS slope ≤0.2 °C/min for ten consecutive one-second
   evaluations. At the cap, capture proceeds with per-key baseline flags.
   The noise limit follows 3×0.447×0.15 ≈0.2 °C/min over 60 one-Hz samples.
   The idle phase records its actual length, `settle_keys` and whether it settled.
   No qualifying keys means `settle_keys: 0`, `settled: null`; idle ends only
   after ten consecutive empty evaluations, with the minimum still enforced.
   Erratum 4 removes the idle half-range test because it rejects stationary
   noise; the 0.15 °C noise limit already removes flicker. Fast-role keys
   with noise in (0.15, 1/3] °C are not waited on: the slope test is undecidable
   at three sigma, and rank retains their `baseline_unsettled` flags.
   A load below 900 s refuses before
   host/model/capture work with `smc_step.load_below_tau_upper_bound`. The fixed
   slow tau upper bound is 900 s; equality is allowed for load duration only.

   ```sh
   PY="$PWD/.venv/bin/python"
   mkdir -p .desk/align-r0
   cp docs/align/r0_desk.example.json .desk/align-r0/config.json
   nano .desk/align-r0/config.json
   ```

   Set the local D model source, SHADE cache parent, the measurement filesystem
   `disk_path` and any **additional measurement custody parents**. R0 needs no
   offloads (`offloads: []`); configured offload labels apply only to the separate
   W1 arm gate. `disk_path` must be on the measurement volume, not
   the offload volume. D revision is `815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9`.

   The real shared custody parent is `$JOULEWISE_CUSTODY_PARENT`, defaulting to
   `~/night-custody`; `JOULEWISE_ADDITIONAL_CUSTODY_PARENTS` (JSON array) is also
   always included. `custody_parents: []` in the example means no further extras.
   All resolved roots must exist as directories; missing/typo roots refuse the
   run and are recorded. Do not point this command at blinded study data.

2. For W1 only, before an independently managed offload, save each source inventory to
   its configured inventory path. Set the four variables to the actual paths.
   Retain these JSON files outside the roots being offloaded. Offload/copy and
   any deletion remain the lead's verified-offload workflow.

   ```sh
   "$PY" -B scripts/align_r0_checks.py --config .desk/align-r0/config.json --inventory "$PILOT8_SOURCE" --output "$PILOT8_INVENTORY"
   "$PY" -B scripts/align_r0_checks.py --config .desk/align-r0/config.json --inventory "$PILOT9_SOURCE" --output "$PILOT9_INVENTORY"
   ```

   Configure each W1 receipt as `{"label": "pilot10", "inventory": "/absolute/manifest.json",
   "destination": "/absolute/offload"}` in `offloads`. Labels are unique nonempty
   strings supplied by config; every configured receipt must match at W1 arm.
   The W1 arm path calls
   `joulewise.align.r0_host.w1_disk_gate(validated_config)` after R0 and requires
   `status == "pass"`: `scripts/align_v4_session.py install --session-root S
   --w1-disk-config .desk/align-r0/config.json` validates this config, runs the
   gate before the installer, refuses on anything but pass and keeps the receipt
   as `S/staging/w1_disk_gate.json`. This is a storage gate, not an arm
   authorization. R0's own disk row reports the same requirement (`w1_requirement`:
   bytes required, whether free space would pass now, offload labels re-hashed at arm).

3. Start the unattended desk run after model preparation.
   Use a new record directory for every attempt; expect approximately **3–4 h
   when all checks pass**, including the 30 min SMC profile. This is a planning
   estimate, not a measured guarantee. A worst-case token-budget estimate at
   10 decode tok/s is **about 7.3 h plus prefill, inventory and setup overhead**:
   12 generated turns × 4,096 tokens, six ladder episodes × 16,384, two long
   decodes × 38,912, memory's 6,144 and load's three × 4,096, plus 30 min SMC.
   This assumes every rung fails and both decode attempts run. Slower hosts or
   raised timeouts can take longer; native signal delivery can also delay a
   deadline. There is no fixed total-run deadline.
   AC power, Automatic initially.

   ```sh
   RECORD="$PWD/.desk/align-r0/$(date -u +%Y%m%dT%H%M%SZ)"
   nohup "$PY" -B scripts/align_r0_checks.py --config .desk/align-r0/config.json --output "$RECORD" >"$RECORD.log" 2>&1 &
   ```

   Every check can run separately with the same command plus, for example,
   `--checks template --models D`. Available checks, in execution order:
   `smc,host,disk,load,template,generated,memory,ladder,long-decode`.
   The host identity and model-load gates precede model checks. A comma-separated
   subset always follows this order. SMC runs before the disk weights hash and before any model load,
   independently of the `CHECKS` declaration or requested subset order.
   It needs no model. A failed check stops the run after saving its report; use
   `--keep-going` for diagnostic continuation. Prerequisite failures still block
   dependent checks, and census refusals always stop. Diagnostic template/disk
   results, checkpoint `required` and ladder `fallback` do not trigger a stop;
   an SMC `inconclusive` is recorded and host, disk and model checks continue.
   It records `smc_selection_missing: true` and `complete_r0: false`;
   completing R0 requires SMC `pass` (Erratum 4).
   Other inconclusive checks and SMC `fail` still stop the run.
   A subset does not complete R0. The timeout is 7,200 s per long-decode
   **attempt**, ladder **episode**, generated **turn**, or other check. D's
   38,912-token decode at 10 tok/s takes about 3,891 s per attempt; two attempts
   get separate deadlines. The default runs one attempt and retries with metadata
   evaluation only after a failed verdict; `--long-decode-attempts 1` disables
   that retry (`2` is the default maximum). Exceptions and timeouts fail the
   check immediately, retaining the existing behavior. A slow D host can use
   `--timeout 14400`. Native
   calls can delay signal delivery. A timeout fails the current check while
   retaining completed attempts/rungs/turns and sampled in-flight evidence.
   JSON/Markdown are saved at each progress boundary, including memory samples.
   Census failure refuses the run; there is no force option.
   If testing High Power, switch it manually and repeat `--checks host` into
   a new output directory; R1 owns the adoption decision.

4. Read `report.md` and its full `report.json`. Exit 0 means the selected
   checks passed; **`complete_r0: true` requires every check for D**.
   Both files are updated at progress boundaries, with each phase's measured
   `check_seconds` and the run's `total_seconds` (also shown in Markdown).
   Preserve failed/partial attempts.
   Checkpoint `required` and ladder `fallback` are valid selection outcomes;
   `decisions_pending_lead_action` must be resolved before R1. Template is
   diagnostic-only. Inconclusive results prevent R0 completion.
   Local model SHA-256 lists authenticate the observed bytes only, not an HF
   revision. The default SMC hook calls
   `scripts/align_smc_enumerate.py --output DIR --gpu-step --idle-seconds 300
   --idle-max-seconds 1200 --load-seconds 900 --recovery-seconds 600`, with a
   3,300 s timeout (maximum phase total 2,700 s plus the existing 600 s margin).
   Raise `--timeout` too if a longer maximum profile exceeds the per-check
   deadline. #658 (`58525031a`) emits `joulewise.align_smc_r0.v1` with keys
   under `response.s_fast`/`response.s_slow`. Exit 0 alone is insufficient.
   R0 verifies the journal SHA-256 and finite, ordered phase bounds, then applies
   the [D1–D6 rule](smc_temperature.md#r1-planning-turn-classification).
   Fast is largest rise with cooling tau ≤60 s and noise ≤1/3 °C. Slow has
   60 < tau ≤300 s, noise ≤0.15 °C, and the longest band hold ≤300 s.
   Both require ≥3.0 °C rise, a positive resolved early rise, and band return
   within 300 s. Below-ambient placeholders, unresolved jumps, and any key
   with a valid reading above 125 °C cannot count (D1(c), Erratum 1: silicon's
   absolute-maximum junction rating; the derived TVH3 reached 137 °C).
   Erratum 2 D1(d), qualified by Erratum 3 and rebuilt by Erratum 4, uses
   resolving D1(a)–(c) keys with class tau ≤60 s, noise ≤1/3 °C and no clamp.
   Reference cooling time is the first baseline + load-tail rise/e crossing,
   timed from actual load end. Take the largest rise among qualifiers within
   1 s of the shortest stable cooling time (1 Hz crossing resolution), lexical
   ties. Exclude rises more than 1.0 °C above that reference rise: a conduction
   path cannot heat more than its source, and 1.0 °C is the gate band floor
   resolving inter-sensor gain/offset spread. Class tau is unchanged and
   printed beside stable reference cooling time. D1(b)'s half-rise test
   applies only to positive rises.
   Erratum 5 adds flags only: `recovery_onset_gap_s` records the first in-grid
   recovery read's start minus actual load end. Each row's
   `reference_crossing_censored` marks an index-zero stable crossing without
   two valid bracketing readings. `heat_ordering_indeterminate` marks any
   censored Erratum 3 qualifier, or a gap exceeding the shortest qualifier's
   stable cooling time. `heat_ordering_wide_exclusion` marks more than one
   D1(d) exclusion, with `heat_ordering_exclusion_count` printed beside it.
   Receipt and summary retain these diagnostics without changing picks or
   refusal. The real capture has a roughly 0.17 s gap and indeterminate false.
   D5 remains sensitive to the first
   recovery read: at delays of 2 s or more the replay's slow pick flips to
   TMVR. Stable-time band hold remains deferred to R1.
   Clamp keys are flagged and excluded from picks only.
   The receipt reads selected classifier rows: per-phase coverage ≥99% at
   500 ms one-cell tolerance, per-phase read errors <1%, and no two consecutive
   empty one-second cells within a phase (`phase_max_empty_cells < 2`). One
   missed cell is admitted by the 99% bar; two lose U1(c)'s two-second reader
   window. Rank excludes unreadable keys before picking a replacement.
   Cells end at the configured deadline (the ending evaluation for adaptive
   idle); handshake and exit-overrun time are outside those grids. Phase-duration
   deviations >1 s (one sampling period) outside the configured length or
   adaptive idle range are flags, not refusals. Capture-wide coverage and the old
   exponential fit are diagnostics. `summary.md` prints these receipt inputs,
   baseline flags/slopes, actual idle duration, D1(d)'s reference, reference rise
   and excluded keys, each pick's exact-duplicate
   aliases (report only), and alternative slow picks. `design_literal` means
   longest tau with band hold ≤300 s (G1/H's cap).
   R0's role selections and sensor locations remain PROVISIONAL; the first
   settled R0 informs the slow-rule choice and R1 owns thermal qualification.

Interpretation: the `load` bar has two parts (protocol change 2026-11-06,
`docs/align/v4/R0-LOAD-REFERENCE-NOTE.md`; it replaces the absolute ≤3.0 nats/token bar).
(1) **NLL reference equivalence.** Teacher-forced NLL on the first 2,049 rendered benign
SHADE IDs (2,048 next-token targets) is compared with the pinned per-model entry in
`configs/align/v4/r0_nll_reference.json`, keyed by (artifact revision, fixture sha256).
Mode `reference` (D): pass iff |mean − reference| ≤ 0.10 nats/token and every 256-target
bin is within 0.5 of the reference bin; the reference is HF transformers 5.22.1 fp32 on the
upstream bf16 weights (11.064 for D: D does not model its own system/tool block, so an
absolute bar cannot apply). Mode `absolute` (30B anchor): ≤3.0. A model or fixture with
no entry fails closed (`no_reference`); a malformed table fails (`invalid_reference_config`).
This tier catches gross faults only, not subtle numeric ones (see the note). Every run also
records the loss profile (`nll_loss_profile`: per-token loss digest, mean, bins, stack
versions) and its sha. **Exact reproduction:** once an entry carries a `reproduce` pin (a
previously qualified R0 report's profile and sha), the run must reproduce it within 1e-3
on the mean and 1e-2 per bin; a different revision, fixture or stack is `not_comparable`
and fails. Without a pin the tier reports `not_pinned`, which is not a fail.
(2) **Generation.** Greedy decode (no sampler; `enable_thinking=True`) of the real SHADE
system+tools prompt plus a one-line user turn asking for one call to the listed tool with
the fewest required parameters, capped at 4,096 tokens, at effort `low` (lead ruling
2026-11-06: the check tests tool-call validity, not reasoning length). If that greedy turn
hits the cap or leaves reasoning unclosed, it is retried exactly once on the production
sampler at seed 96 and the retry decides; other failures are not retried; both turns are
recorded under `generation.attempts`. Pass iff reasoning closes, the cap is not hit,
and the reply holds exactly one well-formed envelope calling **the requested tool** with
schema-valid arguments (another listed tool, e.g. `end_task`, fails as `wrong_tool`). Tokens, seconds and the call are recorded under
`generation`. Either part failing fails `load` (`reasons` lists which).
Synthetic rewrite tables diagnose templates; **generated**
transitions decide B7 (≥12 eligible transitions; any closed-reasoning rewind).
Insufficient transitions are inconclusive. Coherence and echo are diagnostics;
NLL equivalence and the generation call are the load bar. D tries default xhigh, medium, low, stopping at the first
pass; skipped rungs record "not run: higher rung passed". Episodes use spam/bank,
indices 91–92, ≤6 turns/16,384 tokens. Screens
admit only full-cap turns that fit this total. D envelopes must parse ≥95%
with no unsupported-format flags. Reasoning quotes are excluded, capped
incomplete envelopes are reported separately, and tool replies/errors are saved.

Long decode reaches 40,960 positions, calling `mx.synchronize()` before active
memory samples every 256 tokens. Growth uses the median of slopes over sample
pairs at least 10k positions apart, excluding the pre-prefill baseline. Actual
KV-array allocation growth is reported alongside total active-memory growth;
raw samples remain in JSON. Failure retries metadata evaluation at simulated
4,096-token boundaries and decode end. `metadata_absent_single_stream` records
the pinned stack's usual absence of batched metadata. A passing retry that
evaluated no arrays is inconclusive; it cannot set `metadata_eval_required`.
Even evaluated-array success needs Stage-3/R1 production-boundary qualification.

Memory uses full context, D floor budget 6,144, guess bar 45 decimal GB, no swap
growth. The R0 disk check is **report-only**: 66 decimal GB free and no offloads
do not block completion. It still hashes the present D and anchor files, and
does not read configured W1 offload receipts or destinations. W1 separately
requires ≥80 decimal GB free **after R0** and all configured offload hash matches.
At the default maximum 1 Hz / 2,700 s profile, the R0 journal planning estimate is
2,700 × 53,038 = 143,202,600 bytes (about 143 MB). The per-slot estimate is
ceil(95,467,641 measured journal bytes /1,800 one-Hz samples) =53,038 bytes.
This is a planning estimate, not a bound or an R0 gate:
check actual journal size after enumeration. Configured durations scale the
estimate and capture time in the R0 disk receipt and the runner's `smc_step_budget`.
Amendment 1 estimates 37.4 GB for two W1 copies and 52.9 GB for D windows.
The current whole-download total is not a pinned weight-file manifest; the
lead must authenticate the revision before live qualification.
R1 must freeze actual budgets and other slots. The lead
reviews/commits the live record and handles B7, fallbacks, or a stack ruling
before R1; no live gate is claimed by this implementation lane.
Amendment 1 A3.6 separately requires #657's recorded native exactness/admission
before enabling D's checkpoint safety path. Until then use the rebuild fallback;
this runner's rewrite decision does not waive that gate.
