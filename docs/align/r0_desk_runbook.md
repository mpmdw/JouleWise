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
60 s SMC load with **300 s idle, 900 s load, 600 s recovery** (30 min).
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

   `smc_step` configures `idle_seconds`, `load_seconds`, `recovery_seconds`;
   omitted fields default to 300/900/600. A load below 900 s refuses before
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
   The lead's W1 arm path must call
   `joulewise.align.r0_host.w1_disk_gate(validated_config)` after R0 and require
   `status == "pass"`; this is a storage gate, not an arm authorization.

3. Start the unattended desk run after model preparation.
   Use a new record directory for every attempt; budget approximately 5.5–6.5 h,
   including the 30 min SMC profile, potentially longer for long-decode retries.
   AC power, Automatic initially.

   ```sh
   RECORD="$PWD/.desk/align-r0/$(date -u +%Y%m%dT%H%M%SZ)"
   nohup "$PY" -B scripts/align_r0_checks.py --config .desk/align-r0/config.json --output "$RECORD" >"$RECORD.log" 2>&1 &
   ```

   Every check can run separately with the same command plus, for example,
   `--checks template --models D`. Available checks: `host,disk,smc,load,template,generated,ladder,long-decode,memory`.
   A subset does not complete R0. The timeout is 7,200 s per long-decode
   **attempt**, ladder **episode**, generated **turn**, or other check. D's
   38,912-token decode at 10 tok/s takes about 3,891 s per attempt; two attempts
   get separate deadlines. A slow D host can use `--timeout 14400`. Native
   calls can delay signal delivery. A timeout fails the current check while
   retaining completed attempts/rungs/turns and sampled in-flight evidence.
   JSON/Markdown are saved at each progress boundary, including memory samples.
   Census failure refuses the run; there is no force option.
   If testing High Power, switch it manually and repeat `--checks host` into
   a new output directory; R1 owns the adoption decision.

4. Read `report.md` and its full `report.json`. Exit 0 means the selected
   checks passed; **`complete_r0: true` requires every check for D**.
   Both files are updated at progress boundaries. Preserve failed/partial attempts.
   Checkpoint `required` and ladder `fallback` are valid selection outcomes;
   `decisions_pending_lead_action` must be resolved before R1. Template is
   diagnostic-only. Inconclusive results prevent R0 completion.
   Local model SHA-256 lists authenticate the observed bytes only, not an HF
   revision. The default SMC hook calls
   `scripts/align_smc_enumerate.py --output DIR --gpu-step --idle-seconds 300
   --load-seconds 900 --recovery-seconds 600`, with a 2,400 s timeout (configured
   phase total plus 600 s). Raise `--timeout` too if a longer configured profile
   would exceed the per-check deadline.
   #658 (`58525031a`) emits schema `joulewise.align_smc_r0.v1` with keys under
   `response.s_fast`/`response.s_slow`. Exit 0 alone is insufficient. R0 verifies
   its `samples.jsonl` SHA-256 and phase durations, then re-ranks from that
   journal: **S_fast tau <30 s from the first 120 s of load; S_slow tau in
   (120 s, 900 s), fitted on load and confirmed on recovery**. Recovery does
   not refit tau or require tau <600 s. #658's amplitude/noise, >=90% per-phase
   slot coverage and R2 >=0.8 diagnostic bars remain; recovery confirmation
   uses that same R2 bar against the fixed load-fit prediction.
   The adapter also checks selected keys and 1 Hz / >99% successful slots over
   at least 600 s. Missing roles or failed confirmation remain inconclusive;
   R0's own role selections and sensor locations remain PROVISIONAL pending the
   v4 sensor-policy ruling. The source #658 response is retained
   alongside the R0 ruling's response for review.

Interpretation: NLL uses the first 2,049 rendered benign SHADE IDs (2,048 next-token
targets), ≤3.0 nats/token. Synthetic rewrite tables diagnose templates; **generated**
transitions decide B7 (≥12 eligible transitions; any closed-reasoning rewind).
Insufficient transitions are inconclusive. Coherence and echo are diagnostics;
NLL is the load bar. D tries default xhigh, medium, low, stopping at the first
pass. Episodes use spam/bank, indices 91–92, ≤6 turns/16,384 tokens. Screens
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
At the default 1 Hz / 1,800 s profile, the R0 journal planning estimate is
1,800 × 16 KiB = 29,491,200 bytes. This is not a measured bound or an R0 gate:
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
