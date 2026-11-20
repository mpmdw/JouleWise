# Block-5 analysis care audit: what each guard buys, and what a lean pipeline costs

2026-11-06. Branch `lane/2026-11-06-b5-care-audit`, from `b5/analysis-r2` (`929fc65c9`). Reading-only audit. No
real data, restricted custody or night archive was opened. One tiny timing probe ran on a committed synthetic
fixture at `nice -n 19 taskpolicy -b` (section 2.3). Timing evidence comes from `lane/2026-11-06-b5-under-90` at
`505fd40a7` (report `docs/run_reports/2026-11-06-b5-under-90.md`, called **U90** below, and evidence tree `archive/process-traces-before-release-prune-2026-11-08:docs/run_reports/2026-11-06-b5-under-90`).

**Who rules.** The coordinator relayed that Ed has handed rulings on the preregistered rules to the block-5 lead.
So "who must rule" below is **lead (deviation log)** for anything that touches the preregistration, sealed record or
seal pins, and **lead (engineering)** for everything else. Nothing here changes a research question, hypothesis,
estimand or decision rule, so nothing is flagged for Ed.

Abbreviations:
- **PLAN** = `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md` (sealed; SHA-256 `23ef67f5…` equals
  `configs/analysis/b5/seal_pins.json`).
- **REG** = `configs/campaigns/v5_claim_25g83/registration_block5.md`.
- **DL** = `docs/decision_log.md`.
- **RS** = `RUN_STATE.md` as of `929fc65c9`. It was read, not edited.

## 0. Headline

1. **Most of the time is spent re-establishing facts that were settled earlier.** That means re-deriving
   collection-time judgments (clock anchors, pulse-calibration fits, the whole-window verdict) and re-authenticating
   the same bytes in every program. The registered arithmetic itself is a small part. On r2's dry-j profile
   (9,145 s = 152 min), about 100-115 min can be attributed to that kind of work (table 1, column c; estimates). Steps
   8, 6 and 9 (26 min) have no profile. Floats, `fmean`/`stdev`/`fsum` and t quantiles are microseconds.
2. **A block costs about two runs, not one.** PLAN §3.2 item 2 re-runs steps 1-11 after the release and requires
   every digest to equal the dry run's. So the real per-block cost is about 2 × 136-152 min, plus a full rerun for
   every tooling refusal (R3 loop, PLAN 192-193).
3. **The lean pipeline already exists, is merged and has been reviewed.** `scripts/independent_recompute_b5.py`
   (2,925 lines, standard library only, shares no code with L9) computes every registered number from the raw
   powermetrics records. `scripts/compare_b5_recompute.py` (4,076 lines) compares it with L9 against bars fixed blind
   (`configs/analysis/b5/recompute_bars.json`, 1e-6 relative). Their agreement is already block 5's registered
   release condition (RS line 64, item 37 (ii); RS line 340, item 83 ruling 1). On the full-size synthetic window it
   ran in **9 s for 316 runs** (RS line 586), against about 2 h for the heavy pipeline on the same window class.
4. **Projected lean runtime on real block-5 data.** About **5-8 min** wall on the Air with a 10-process member pool,
   or 25-65 min as the script is written today (one process). Both are estimates, dominated by one plistlib parse of
   each member's raw trace (section 2.3).
5. **For block 5 on the heavy path,** the engineering cuts alone plausibly reach **about 85-95 min**. Adding the
   deviation-log cuts gives **about 70-85 min**. Both are estimates; steps 8-11 are unprofiled. The biggest
   per-block saving is not in the heavy path at all: make the release a digest check plus the lean recompute (about
   −150 min per block). For blocks 6 onward, make the lean recompute the production path and keep the heavy pipeline
   as an audit off the critical path.

## 1. Inventory of guard and ceremony layers

Column (a) uses these short names:
- **BLIND**: blinding of outcome content.
- **FID**: fidelity to the preregistered estimators.
- **INT**: data integrity / tamper evidence.
- **REPRO**: reproducibility.
- **OPS**: operational safety.
- **NONE**: nothing concrete.

Column (c) costs are per block per run (one dry run), real-data basis r2 dry-j (U90 §5: 7 workers, nice 5, machine
shared with dry-i). **M** means measured; **E** means an estimate, made by applying a synthetic profile share (U90 §3,
`archive/process-traces-before-release-prune-2026-11-08:docs/run_reports/2026-11-06-b5-under-90/part5-head-stacks/detail.txt`, `archive/process-traces-before-release-prune-2026-11-08:docs/run_reports/2026-11-06-b5-under-90/cprofile-on-steps0-3b/report.txt`) to the real step wall.

Column (d) says what to do and whether any reported number would change. **"No number"** means that registered
numbers, decisions and refusal positions stay equal (D-188 standard, DL:12244), unless the cell says otherwise.

| # | Layer | (a) Protects | (b) Required by | (c) Wall cost / block | (d) Recommendation |
|---|---|---|---|---|---|
| 1 | **Release re-run**: steps 1-11 run again after the release; every digest must equal the dry run's | REPRO (determinism check); INT (dry-run outputs unaltered) | PLAN 194-195 (§3.2 item 2); `dry_run.py:2006-2027, 2076-2087` | **M: one whole run, 136-152 min** | **Lighten.** Re-verify the dry run's recorded output digests (seconds), then run the lean recompute and comparator (5-8 min E). Determinism is already established: D-188 calls the code deterministic (DL:12244), and candidate 1 (dry-h) compared EQUIVALENT to attempt E across inputs, decisions, registered and intermediate tiers (origin/main retrospective:26). A digest check catches any custody change. No number. Lead (deviation log), DLE-1. |
| 2 | **Strict re-validation at step 1**: `validate-bundle --strict` re-derives clock anchors (exact `Fraction` LP), pulse-fit physics, thermal-pressure environment refusals, and parses several plists per bundle | INT; FID (registered step) | PLAN 161 (§3.1 step 1); DL:4452 (D-078 rule 4, "Stored verdicts are re-derived, never trusted"), from an audit P0 (DL:4439-4441), not a field incident | **E: 15 min.** About 9 min re-derives stored anchors and fits (anchor LP is 49% of child CPU, `k.anchor` 293 of 596 s), about 5 min is strict extras beyond one reduction, about 4 min is one parse and reduce | **Lighten.** The bytes are already hash-bound to the harvest record (step 0 census). Same pinned code on the same bytes gives the same anchors, unless the 120 s deadline fires (row 9). Keep one reduction per bundle; hash-bind the anchor and fit results; keep the heavy re-derivation in the audit run. No number (deterministic code). Lead (deviation log), DLE-3. |
| 3 | **3b candidate refits**: `verify_stored_evidence_physics` refits every calibration candidate's pulses from bytes, 4 per pack, sequentially; packs share candidates but refit them anyway | INT (stored calibration evidence matches its bytes) | Not in PLAN. Frozen harvest code `calibration_bracketing.py` (seal pin4, `seal_pins.json`; REG §11 item 4, PLAN 80). Ed's ED-RULING item 6 offered (b) "checks the harvest-recorded fit by hash binding" and chose (c) **for block 5's first dry run** (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:53-63`) | **E: about 24 min** (86% of 3b worker CPU, U90 §3; 3b real 1,658 s) | **Lighten.** Either memoize per distinct capture per run and prefetch in parallel (U90 lever 2: −5 to −7.5 min), or hash-bind per ED-RULING (b) (up to −24 min, plus the refit share inside steps 4, 5 and 8). Touches a seal-pinned file. No number. Lead (deviation log), DLE-4. |
| 4 | **L4 bracket cache eligibility**: any fill that starts a thread is unstorable; `probe_custody` starts a daemon thread (exists/is_dir only), so L4 never stores | REPRO (fills must be pure). In this case it protects **NONE concrete**: the probe's hazard is already handled by `bracket.py:184-205` `_servable` ("a passed, reason-free assessment implies that every probe was positive") | Store design only: `analysis_verified_store.py:825-830` (`_mark(fills,"thread")`), `calibration_ledger.py:5554-5557`. Not in DL; D-188 permits, does not require, the store | **M/E: about 12.5 min** (U90 lever 1: steps 4 and 5 recompute brackets, 45% and 26% of their work) | **Lighten.** Whitelist the custody-probe thread in the fill recorder, or move the probe out of the fill. `bracket.py:208-216` is stale ("Today a non-servable fill is still stored"). No number. Lead (engineering). |
| 5 | **Per-read authentication**: `Path.resolve` on every read (`authentication_io.py:1187`), whole-file sha256, first-digest registry (`:1148-1178`), recursive `estimator_registration` vocabulary walk (`:637-651`) | INT (TOCTOU and symlink escape; digest stability); FID (no forged registration vocabulary) | DL:8706-8708 (D-124 amendment: "total recursive vocabulary refusal + strict duplicate-key JSON parsing at every admitted-byte entry"); DL:9792-9794. **Counterweight**, D-161 (DL:207): the in-process adversary is out of the threat model; "tamper-EVIDENT … not tamper-PROOF"; fail-closed stays only for physics, evidence and preregistration. **Incidents**: audit-constructed (FCM6-01, DL:8853-8856; recorder race 10/400 in audit, DL:9907-9931). Review HIGH on #641, a symlink to `passage/..` (retrospective, origin/main `docs/process_traces/2026-11-04-d188-retrospective/RETROSPECTIVE.md:38`). No field incident | **E: step 5 alone about 11 min** (auth reads 229 s + strict parse 160 s + `_joinrealpath` 171 s of 1,205 synthetic s, scaled to 1,426 s), plus a similar share in steps 8-11 (unprofiled) | **Lighten.** Resolve once per root or directory and read with `O_NOFOLLOW` (already `_read_nofollow_bytes`), so symlink protection stays. Authenticate each input once per run and pass digests between programs (D-188 item 2, DL:12245). Keep the vocabulary ban, with the reserved-key pre-check (U90, −25 s). No number. Lead (engineering). |
| 6 | **Strict JSON/JSONL first-parse; L7 grammar memo per process, not shipped** (`authentication_io.py:654-704, 808-885`; `SHIPPED_MEMOS` in `analysis_member_pool.py:123`) | INT (duplicate keys, NaN/Inf, non-UTF-8 are rejected) | DL:8706-8708 (strict parse); memo shipping is D-188 store design only | **E: about 2.5 min in step 5** (126 s synthetic), more in 8-11 | **Lighten.** Ship `grammar_ok` with the two memos already shipped (U90 lever 6). Keep strict parsing. No number. Lead (engineering). |
| 7 | **Whole-window verdict re-derivation in each consumer** (`k.ww.rederive`/`validate_whole_window_verdict_row`, steps 4, 5, 9, 11) | INT; FID (J1 member-level rules) | DL:4452 (D-078 rule 4); L9 cold ruling J1 (`docs/process_traces/2026-10-block5/l9-rulings/DECISIONS.md:11-15`) | **E: 5-10 min** (step 5 alone 238 of 1,110 sampled s, scaled to about 5 min; step 4 child 239 s) | **Lighten.** Re-derive once per window per run (D-078 is satisfied: the verdict is still re-derived, not trusted). Later consumers bind the result by content hash (D-188 item 2). No number. Lead (engineering). |
| 8 | **Launch-lineage re-reads**: `ordinary_present_bundle_paths` re-reads every bundle manifest on each call | INT | Code only | **E: about 3 min** (step 5, 130 s synthetic) | **Lighten.** Memoize per run by tree digest. No number. Lead (engineering). |
| 9 | **120 s refit wall deadline, converted to a tooling refusal** (`powermetrics_fiducial.py:91-94`; observer `deadline_observer.py`; `dry_run.py:2038-2062`; tripwire `:1014-1034`) | OPS (host safety of the measurement Mac at collection). The **conversion** protects REPRO and FID: an uncaught firing makes uncertainty `not_estimable` and drops envelopes, a load-dependent number | Not in PLAN. DL:10153-10180 (D-078 registry amendment, "only a host-safety backstop … `reproducible: false`"); ED-RULING item 6 (c) (`ED-RULING.md:53-79`). **Incidents**: it fired in full-size synthetic runs (`ED-RULING.md:55`; about 17 min in trace 7, "passes in 24 s in isolation", `docs/process_traces/2026-10-27-pipeline-audit/segments.json:1462`); a forced firing first slipped through with 4 keys changed (`ED-RULING.md:72-77`) | **M: about 0 on a clean run.** A firing costs a full rerun (≥ 150 min). It also forbids co-scheduling, makes 10 workers and 3b concurrency risky, and drives the cloud-only rule (row 16) | **Keep the conversion. Drop the deadline in the analysis path** (ED-RULING option (a); `docs/design/analysis_cadence_plan.md:34-37`). The cell budget at `:90` is the reproducible bound. This edits a governed estimator path (`calibration_bracketing.py:239-244`), so the identity epoch and calibration acceptance must be reissued (a real precedent: the `_r2` reissue, `ED-RULING.md:57-59`). No number when it would not have fired. Lead (deviation log), DLE-5. Moot for the critical path if the lean recompute becomes production (it does not refit). |
| 10 | **Step 11 primary-bound self-check pass**: `sensitivity_pass(..., BMax(0.0, ...))` recomputes every projection, extraction and contrast at the primary bound, then discards the result (`dry_run.py:1709`) | REPRO (sensitivity code reproduces primary at equal bound) | Not in PLAN or J6. J6(b) items 1 and 3 ask for **tests** asserting equality (`l9-rulings/RULING.md:146-149`). Added by L9 S10 (`491e1239d`) | **E: about 13 min** (about half of step 11's 1,731 s) | **Drop.** Keep the in-pass checks of the real wider pass (`sensitivity_changed_bound_independent_value`, mean and h equality) and the unit tests. The lean recompute computes the sensitivity line independently. No number (it only refuses). Lead (engineering). |
| 11 | **J6 wider-bound sensitivity pass** (b_sens = max(b_op, B_max); floors, D and outcome words re-derived) | FID (registered sensitivity line) | Sealed erratum 3 item 14 (`seal_pins.json` `erratum_3_sha256`); J6 ruling (`RULING.md:140-160`) | **E: about 13 min** in r2 (a full re-projection with strict re-validation) | **Keep the estimand; compute it leanly.** It needs only envelopes under b_sens on already-parsed traces (the recompute's `sensitivity_bound`, `independent_recompute_b5.py:2233`). Run the two pack derivations and passes concurrently (U90 lever 3, −5 to −10 min). No number. Lead (engineering). |
| 12 | **Step 10 issuer + D-173 custody reopen/replay** (`dry_run.py:1581-1601`: the issuer projects, then `open_paper_input` replays the validator and re-projects; equality is required) | INT (no caller-chosen path or value enters a paper number) | PLAN 61-62 (§1 item 3, D-173 route); DL:11242-11262 (D-173, from audit: "a fabricated number or reason could be rendered", DL:11244-11248). D-188 item 2 names the **step-10 issuer** as eligible for hash verification (DL:12245) | **E: about 5-8 min** (about half of 936 s) | **Lighten.** Keep the D-173 open route (it is the registered supplier route). Replace the second full re-projection with content-hash binding of the issuer's authenticated inputs, as D-188 item 2 allows. No number. Lead (engineering). |
| 13 | **Rehash of every registered output before each child and step** (`dry_run.py:639-648`) | INT (restricted custody unchanged during the run) | PLAN 154-155 ("each output is content-addressed … the step that reads it authenticates it") | **M: 3-4 s per step, about 1 min per run** (U90 §3) | **Keep.** Cheap. |
| 14 | **Step-0 source census** (hash every claim-run file against the harvest manifest; ledger-prefix test) | INT; REPRO | PLAN 154-155; J7 (`DECISIONS.md:25`) | **M: 85 s** (dry-j) | **Keep.** This is the binding that makes hash-independence (rows 2, 3, 7, 12) safe. |
| 15 | **Frozen-file prohibition**: seal pins (`windows.py:63-72,190`); `tests/b5_analysis/test_frozen_files.py:23-37`; `ESTIMATOR_CODE_PATHS` hashed into the calibration identity (`calibration_bracketing.py:239-244, 779-792`); `scripts/repin.py:27-32` | FID; REPRO; INT (identity epoch binds the code that produced the calibration) | REG 5297-5300 (§11 item 1(ii): gated R3 fixes only); `docs/process/freeze_by_commit.md:65-71` (rebind); D-190 authority quote (DL:12265: "treating frozen things strictly is like deadline enforcement … we should obviously fix the thing") | **0 runtime.** The cost is indirect: it blocks rows 3 and 9 and turned a 16-line `reduce.py` fix into about a 440-line mirror (`freeze_by_commit.md:28`) | **Keep the pins** (they are what make "same code, same bytes" true). **Use the rebind** (DL:12271 pattern) for rows 3 and 9 instead of engineering around them. No number. Lead (deviation log) for pinned files. |
| 16 | **Cloud-only heavy runs / one heavy job per host** | OPS (avoids firing row 9 in a live run; disk) | No codified rule. Lead practice (U90:9, 76); origin/main RS:407 ("contention fires the 120 s budget"), lifted at RS:428 except for official attempts; `ED-RULING.md:63`. **Incident**: attempt D died on ENOSPC after 18.5 h when parallel agent tests filled about 110 GB (retrospective:10, 53) | **0 per block.** Cycle-time cost: cloud hosts (3 cores, 1 h) never reach steps 8-11, so 4,220 s of r2 has no profile (U90 §5 item 7) | **Keep while row 9's deadline exists. Drop after it** (keep the disk guard and per-run TMPDIR, which address the real incident). No number. Lead (engineering). |
| 17 | **D-188 blinded comparator vs the r1 oracle** (`tools/b5_equivalence/compare_b5_results.py`; tiers P/D/R/I identical, A may differ) | REPRO; FID (rewrite equals reference) | DL:12244-12246 (D-188 items 1 and 3; "The reference stays the oracle until the block-5 release") | Tool: minutes (no recorded wall time). The real cost is the reference run (r1 attempt E took 27.1 h; dry-i was a full run) | **Keep for block 5. Retire at its release.** For later blocks the lean recompute plus `compare_b5_recompute.py` is the cross-check. No number. Lead (engineering). |
| 18 | **Serial driver phases** (packs serial by construction; steps run in number order) | FID for step order and the stop rule. Pack serialization: NONE | PLAN 154, 174-178 (order and stop rule); D-189 (DL:12251-12257) | **E: the rest of the U90 levers** (3b packs −13 min already done; step 11 passes concurrent −5 to −10; steps 1/2 and step 10 vs 5-9 have no data dependency, agent read of `dry_run.py`) | **Keep the registered order and stop rule.** Overlap the independent work and consume in order (`parallel.py` already does this). No number. Lead (engineering). |
| 19 | **Exact `Fraction` anchor LP; Decimal quantile proofs** | FID (anchor LP is the pinned reducer's registered effective clock bound); INT (the acceptance proof re-derives on every validation) | Anchor: `uncertainty_evidence.py` in `ESTIMATOR_CODE_PATHS`. Proof: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:209-220` (issuance), re-run by the frozen validator `calibration_bracketing.py:795, 1168-1183` | Anchor: inside row 2 (about 9 min). Proof: under 1 min after the U90 memo (`9f80ec2d4`) | **Keep the arithmetic.** Compute it **once** (row 2); the memo is enough for the proof. No number. Lead (engineering). |
| 20 | **VDL store** (L1-L6 leaves, keys over source and tree digests, audit hook, `BLIND_ON` on real runs, `shadow:1000` on synthetic) | REPRO (result equivalence of cached derivations) | D-188 (DL:12239-12251) permits; the design lives only in code (`analysis_verified_store.py:1-71, 209-263, 1209-1260`) | Net **saving**. Its costs are rows 4 and 6, and per-call tree re-digest (unmeasured). Shadow costs fall only on synthetic and test runs | **Keep as accelerator.** Fix rows 4 and 6. Pack pools ship the whole store (U90 lever 4): ship only the pack's roots. No number. Lead (engineering). |
| 21 | **Blinding layers**: restricted custody; structure-only public record; float-token scan on reader records (`dry_run.py:612-630`); salted step codes (`:1887-1890`); HMAC member identity (`:1856-1860`); closed-key phase logs (`phase_timing.py:11-23`); refusal registry redaction (`steps.py:121-140`) | BLIND | PLAN 186-193 (§3.2 item 1); D-188 item 3 (DL:12246). Incident: false positive at attempt A, `reader_record_not_structure_only` (RS item 95; `docs/process_traces/2026-10-29-l9-census-path/BRIEF.md:19,33`) | **About 0** | **Keep.** These are the layers that buy blinding, and they are cheap. |
| 22 | **Refusal registry and R3 loop** (`configs/analysis/b5/dry_run_refusal_classes.json`: 191 tooling codes, 2 outcome codes) | BLIND; FID (an outcome refusal is a result, a tooling refusal is a defect) | PLAN 174-178, 189-193; REG 568-570 (R3) | **0 per run.** Each tooling refusal costs a full rerun: attempts A-E, dry-h, dry-i, dry-j and dry-k so far | **Keep.** Cut rerun cost via rows 1, 9 and section 2 (a lean rerun takes minutes). No number. |
| 23 | **Kept-unit and exclusion tripwires** (≥ 5 units per stratum, member codes on kept units, `neg8.midpoint_lost` on GAMMA, `harvest_checkout_not_clean`) | FID | PLAN 83-91, 137-138; L9 Z1 (`DECISIONS.md:33-34`) | About 0 | **Keep.** |
| 24 | **Checkout and custody preflights** (`analysis_checkout` clean HEAD; origin containment at step 5, `identity_pins.py:858`; `custody_preflight`; `without_backup_roots`) | REPRO; INT; OPS | PLAN 194 (pinned commit); REG §11. Incident: attempt B had to merge before step 5 (origin/main RS item 109) | About 0 | **Keep.** |
| 25 | **Paper custody / D-173 supply map at the paper fill** | INT | DL:11242-11262; PLAN 41-43 | Outside the run | **Keep.** |
| 26 | **Results cold gate (PLAN step 12, judge + refuter)** | FID | PLAN 172 | Human days, not CPU | **Already replaced** by recompute agreement (RS line 64, item 37 (ii): "no separate cold gate"). Record that in the deviation log if it is not already there (DLE-0). |

**Honesty notes.**
- Rows 9, 16, 21 and 24 have real incidents (cited) and are not ceremony.
- Row 5's motivators are audit-constructed attacks, not field events. D-161 already rules the in-process adversary
  out of scope, which is why row 5 is "lighten", not "drop".
- Row 2's D-078 rule 4 came from an audit P0 (a stale calibration relabelled fresh). Hash binding to the harvest
  record plus one re-derivation per run still satisfies it.

## 2. Lean pipeline

### 2.1 Spec: what the preregistration actually requires per block

The plan was written so that its arithmetic "can be recomputed by hand" (PLAN 10). Its estimators are listed below.

**Inputs.** Every input below is authenticated by SHA-256 against the harvest record and seal record.
- Per window: the analysed attempt's `derived/exclusions.json` (PLAN 77-91).
- Per member: `metadata.json`, `summary_metrics.json`, `events.jsonl`, `raw/powermetrics.plist`. The anchor's
  effective clock bound m and the wall-minus-monotonic span s come from metadata.
- The calibration bracket's pre and post fiducial bounds and the recorded `b_fiducial_s` (PLAN 234).
- The NEG-8 allowance record (`derived/neg8-allowance.json`, or the re-screen bracket; PLAN 237-244).
- The two `extraction_spec.json` files and GAMMA's `analysis_manifest_v3.json` (PLAN 209-216, 366-369).
- For the sensitivity line: the acceptance and ledger prefix (J6).
- For §8.2: `withheld/meter.json` and the meter streams.

**Steps.**
1. Kept units from the exclusions (§2.2).
2. For each kept member, parse the trace once. Compute the overlap-rule phase energy (REG §0.4) and the corner
   anchor-shift envelope under b_op, under b = 0 (residual) and under b_sens (PLAN 234-246, 316).
3. §4: stratified 0.2/0.8 mean, V, t(0.975, min(n_r, n_b) − 1), B by `fsum`, endpoints, per-token value, attribution
   floor.
4. §5: D-054 point floor, guard g(n), 2ⁿ corner widening (n ≤ 10 here), D-124 comparative shared edge, worst-case
   composition.
5. §6: eight R and four R_cm, with branch A/B.
6. §7: d_k, dbar, s_d, rounded t*, D, Holm with m = 2, outcome precedence, leave-one-quad-out, L2 ceiling.
7. §7.3 and §8.1: descriptive ratio and per-token lines, the load-correlated and battery-assist sensitivity lines,
   the cross-window check, and the J6 b_sens line.
8. §8.2: whole-machine cross-check.

**Outputs.** One restricted JSON record per block with every registered field (PLAN §9 table, 701-711). Public
stdout carries structure-only codes.

### 2.2 It exists: `scripts/independent_recompute_b5.py`

- It implements exactly this. Standard library only; header at lines 1-17.
- Registered core: the overlap rule `overlap` (213), `shift_envelope` (224), `reported_estimate` (1040),
  `point_floor` / `corner_max` / `floor_estimate` (1153-1210), `contrast_stats` (1248), `holm` (1268),
  `evaluate_outcome` (1287), b_op from the bracket arithmetic with a cross-check against the record (812-850), and
  `sensitivity_bound` (2233).
- Beyond the registered core it adds the whole-machine lines, the BETA-inclusive line, the scaled-allowance line, a
  reconstruction diagnostic, and an independent re-derivation of the exclusions. These were all decided blind; RS line
  64 lists them.
- **"Input judgments"** (header line 5) are taken from stored records and are not re-derived: member selection,
  clock anchors (m, s), timing bounds, and calibration fits (b_pre, b_post). That is the whole difference from the
  heavy pipeline. The heavy pipeline re-derives those judgments from bytes, more than once.

**Rough LOC.**
- A registered-numbers-only lean pipeline is about **1,200-1,500 lines**: the recompute's lines 86-1460 plus I/O and
  sanitizing.
- The existing script is 2,925 lines.
- The comparator is 4,076 lines and is reused as is.
- A member process pool would add about 40 lines.

### 2.3 Projected runtime on the Air (estimate)

Kernel CPU, method:
- **Trace parse dominates.** The recompute parses each member's `raw/powermetrics.plist` once (`plist_records`,
  line 348).
- **Measured on this Air, during the live analysis run, at background QoS** (`nice -n 19 taskpolicy -b`, so E-cores
  under load, a lower bound): plistlib on the committed fixture
  `tests/fixtures/d117_v2_production/strict_seed_bundle/raw/powermetrics.plist` parsed 5.78 MB, 75 frames, in
  0.549 CPU-s, which is **10.5 MB per CPU-s**. A free P-core is plausibly 2-3× faster (estimate).
- **Real size (estimate).** A raw powermetrics file is about 130 MB (`docs/design/analysis_cadence_plan.md:49`).
  The recompute reads about 316 members (science plus NEG-8 references, RS line 586), so about 41 GB.
- **Everything else is small.** Envelopes are 4 corners × a few breakpoint shifts × an O(records) overlap, for about
  4 bounds × 3 phases per member. That is well under a second per member. The statistics take microseconds.
- **Estimated totals:**

  | Configuration | Estimate |
  |---|---|
  | Total parse CPU | about 1,400-3,900 CPU-s |
  | Single process (as written) | about 25-65 min |
  | 10-process member pool, 4 P + 6 E cores (about 160 MB/s aggregate) | **about 4-6 min parse, about 5-8 min end to end** with JSON and I/O |
  | Same run on synthetic full size, for scale | 9 s measured |
- **Consistency check against r2.** Real r2 step 1 averages about 24 worker-s per bundle under load
  (901 s × 7 / 262). Synthetic is 2.3 s per bundle (`archive/process-traces-before-release-prune-2026-11-08:docs/run_reports/2026-11-06-b5-under-90/part5-head-stacks/detail.txt`). That ratio fits real traces
  about 20× the fixture's size, parsed several times per bundle in r2.

### 2.4 Block 5: independent replication of r2

This is already registered; run it as registered:

1. Run r2 blind (dry-j or dry-k), then `independent_recompute_b5.py` on the same window index, outputs in restricted
   custody.
2. Run `compare_b5_recompute.py` with `configs/analysis/b5/recompute_bars.json` as the binding set, fixed blind
   (RS line 340). The rule is bar = max(1e-6 × |value|, 1e-6 absolute, half a printed unit). Counts and categorical
   words are compared exactly. A sign or threshold word is compared only when its number lies outside its bar from
   the threshold (the FS3 rule, RS lines 589-602).
3. The only public output is per-family pass/fail counts; values and differences stay restricted (RS item 87).
   Agreement on every family with 0 unmapped is the release condition (RS line 64 (ii)).
4. Do this **before** the release event, on the dry-run custody, so the release itself can be a digest check plus a
   lean re-run (DLE-1).

### 2.5 What would make the lean path production for blocks 6 onward

All of the following are decided blind, now.

1. **Block-5 agreement.** Exit 0 on the real block-5 dry-run custody, every family agreeing, 0 unmapped. Then do it
   again on the first block-6 session.
2. **Input judgments by hash.** The lean path trusts m, s, b_pre, b_post, the exclusions and the NEG-8 record because
   step 0's census binds them to the harvest record. This is D-188 item 2 (DL:12245) applied to collection-time
   judgments. It is also ED-RULING item 6 option (b) (`ED-RULING.md:57-58`).
3. **Heavy pipeline as audit.**
   - It runs once per block, after the lean result, off the critical path, with fewer workers.
   - It never gates a release unless it disagrees.
   - Disagreement rule, fixed now: any family outside its bar holds the release. A blind seat traces it
     structure-only. Which side prints is decided by the defect found, never by the value.
4. **Ties at thresholds.** Fix blind the rule for decisions whose number lies within its bar of a threshold
   (|dbar| vs floor, an interval endpoint at 0, R vs 2, the sign of a leave-one-out estimate). The FS3 rule above is
   the comparator's half. The paper's half is the lead's FS3 note (RS line 592).
5. **Engineering.** Add a member process pool. Keep the structure-only stdout (`STRUCTURE_FLAG_CODES`, recompute
   lines 70-72). Write the registered output schema the paper fill reads.
6. **Paperwork.** Block 6's registration allows changes only by a dated §17 entry with one executing refuter
   (`docs/registrations/block6_replication_DRAFT.md:19, 1171`). Block 6 keeps "block 5's registered arithmetic
   unchanged" (RS line 64), and this change keeps it: only the program changes.

## 3. Ranked cuts

Minutes are per block. "Run" means one analysis pass. Ranked by minutes saved on the critical path.

| Rank | Cut | Minutes saved | Risk to the science | Who rules |
|---:|---|---|---|---|
| 1 | Lean recompute is the production path for blocks 6+; heavy pipeline runs as audit (2.5) | **About 130-145 per run** (136-152 → 5-8 E); about 260-290 per block counting the release | Low-moderate. The lean path trusts collection-time anchors and fits by hash instead of re-deriving them; the audit run covers that. Arithmetic is unchanged and replicated within 1e-6 | Lead (deviation log), DLE-2 |
| 2 | Release = verify dry-run digests + lean recompute + comparator, instead of a second heavy run (row 1) | **About 130-150** (block 5 included) | Low. Determinism is already shown by equivalence runs. Custody tamper is caught by the digests. An independent check replaces a self-replay | Lead (deviation log), DLE-1 |
| 3 | 3b candidate refits: hash-bind the harvest-recorded fit (ED-RULING (b)); fallback is memoize plus parallel prefetch (row 3) | **About 15-24** (memo only: 5-7.5) | Low. Same pinned code on the same hash-bound bytes. Loses only a re-check that the stored fit was computed correctly at collection | Lead (deviation log), DLE-4 (seal-pinned file) |
| 4 | Drop step 11's primary-bound self-check pass (row 10) | **About 13** E | None to numbers (it can only refuse). Unit tests and the recompute cover it | Lead (engineering) |
| 5 | Make L4 storable (row 4) | **About 12.5** | None. The probe's hazard is handled by `_servable` | Lead (engineering) |
| 6 | Authenticate once per run: resolve per root, ship the L7 memo, mint pre-auth per pack, reserved-key pre-check (rows 5, 6, 8) | **About 8-14** E (step 5 about 11; 8-11 unprofiled) | Low. Symlink, digest-stability and vocabulary checks are all kept | Lead (engineering) |
| 7 | Step-1 strict validation → one reduction per bundle plus hash-bound anchors and fits (row 2) | **About 9-11** E | Low, same argument as rank 3 | Lead (deviation log), DLE-3 |
| 8 | Whole-window verdict re-derived once per window per run (row 7) | **About 5-10** E | None; D-078 rule 4 is still met | Lead (engineering) |
| 9 | Step-10 replay → content-hash binding under D-188 item 2 (row 12) | **About 5-8** E | None to numbers; D-173 route kept | Lead (engineering) |
| 10 | Step-11 passes and pack derivations concurrent (rows 11, 18) | **About 5-10** E | None | Lead (engineering) |
| 11 | Drop the 120 s deadline in the analysis path, with acceptance reissue (row 9) | **0 on a clean run.** Removes about 150-300 min per firing, and unlocks 10 workers and co-scheduling | None to numbers. A deadline firing is host-dependent and never a registered outcome | Lead (deviation log), DLE-5. Moot for the critical path after rank 1 |
| 12 | Retire the r1-oracle comparator at block-5 release; relax cloud-only after rank 11 (rows 16, 17) | Cycle time, not per-block | None | Lead (engineering) |

**Projected block-5 heavy path.** Start from U90's 136 min (7 workers). Ranks 4, 5, 6, 8, 9 and 10 (engineering
only) give about 85-95 min. Adding ranks 3 and 7 gives about 70-85 min. These overlap U90's levers 1-6 and are not
additive with its 100-105 min figure. All are estimates, and steps 8-11 still need a profile.

**Keep unchanged:** rows 13, 14, 21-25 (blinding, census, rehash, registry, tripwires, preflights) and the registered
order and stop rule. They cost about 2 min per run.

## 4. Draft deviation-log entries

Each entry below is a draft for the lead to sign.

**Signed 2026-11-06.** The lead adopted DLE-0, DLE-1 and DLE-2 and did not adopt DLE-3, DLE-4 and DLE-5 for now. The
signed entries are in `docs/analysis/b5/DEVIATION-LOG.md`, the deviation log of the block-5 analysis plan. The plan
is sealed, so it cannot link to the log itself. The DLE-1 release is `scripts/release_b5.py`; its runbook is
`docs/analysis/b5/RELEASE-RUNBOOK-lean.md`.

**Blindness (applies to every entry).** Drafted 2026-11-06 while block 5 is blinded. The real-data r2 run on this
laptop is a blind dry run, no released value exists, and this audit opened no restricted path. **The signer must
restate, at signing, that the release event has not happened and that they have seen no block-5 energy or outcome.**

**DLE-0. PLAN step 12 results cold gate.**
- **Original rule.** PLAN 172 (§3.1 step 12, "judge + refuter").
- **Change.** Replaced by the independent recompute agreeing with L9 within fixed bars, as already decided blind
  (RS line 64, item 37 (ii)).
- **Rationale.** The recompute re-derives every printed number in separate code.
- **Estimand.** Unchanged; only how the numbers are checked changes.
- **Blind.** Yes (2026-10-14, before any block-5 number).
- Record it if it is not in the log.

**DLE-1. Release run.**
- **Original rule.** PLAN 194-195 (§3.2 item 2): after the release, "re-runs steps 1-11 from identical bytes at the
  pinned commit; every output digest must equal the dry run's".
- **Change.**
  1. After the release, re-verify every output digest the dry-run record holds, against the dry-run custody and the
     pinned commit, and refuse on any mismatch (`release_digest_differs_from_dry_run`).
  2. Run the independent recompute and comparator. Their agreement is the release condition.
  3. The full heavy re-run becomes optional audit work.
- **Rationale.** The re-run tests only determinism of deterministic code (DL:12244) and custody integrity. Digests
  cover the second. The recompute is a stronger check than self-replay because it is independent code. The saving is
  one full run per block (about 2.5 h).
- **Estimand.** No change; how it is verified changes.
- **Blind.** Yes.

**DLE-2. Production program for blocks 6+.**
- **Original rule.**
  - PLAN 159-171 (§3.1 programs table) and §11 (PLAN 736-757), the L9 programs.
  - Block 6 analysed "with block 5's registered arithmetic unchanged" (RS line 64).
  - Block-6 changes only by a dated §17 entry (`block6_replication_DRAFT.md:19, 1171`).
- **Change.**
  - The registered numbers for block 6+ are produced by the standard-library recompute, with a member pool.
  - Collection-time input judgments (anchors, fits, exclusions, NEG-8 record) are bound by content hash to the
    harvest record.
  - The L9 pipeline runs once per block as an audit. Its disagreement rule is the one in 2.5 item 3.
- **Rationale.** Same arithmetic, 20-30× less wall time, separate code. Re-deriving deterministic collection-time
  judgments on every run protects against nothing that hash binding does not (D-161, DL:207: tamper-evident, not
  tamper-proof).
- **Estimand.** No change to any estimand or decision rule; only the program changes.
- **Blind.** Yes. Block-6 sessions must still be blinded at signing.

**DLE-3. Step-1 strict validation.**
- **Original rule.** PLAN 161 (§3.1 step 1, `validate-bundle --strict` per kept bundle).
- **Change.** Steps 0-2 keep the census hash binding and one reduction per bundle. The anchor LP, fit physics and
  environment refusals are bound by hash to the harvest's strict results instead of being re-derived. The full strict
  pass moves to the audit run.
- **Rationale.** Same pinned code on the same bound bytes; the cost is about 9-11 min per run.
- **Estimand.** No change.
- **Blind.** Yes.

**DLE-4. Calibration candidate verification in 3b.**
- **Original rule.** The seal-pinned harvest file `joulewise/calibration_bracketing.py` (`seal_pins.json` pin4;
  REG §11 item 4; PLAN 80). ED-RULING item 6 option (c) applied "for block 5's first dry run"
  (`ED-RULING.md:53-63`). Note that PLAN 748 (bracket replay in finalization) is kept.
- **Change.**
  1. A run-scoped memo of `verify_stored_evidence_physics` per distinct capture digest, which needs a cited rebind of
     pin4 (`freeze_by_commit.md:65-71`; precedent DL:12271).
  2. Or option (b): bind the harvest-recorded fit by hash.
- **Rationale.** Four sequential refits per pack, repeated across packs, are about 24 min of 3b.
- **Estimand.** No change.
- **Blind.** Yes.

**DLE-5. Analysis-path wall deadline.**
- **Original rule.** `powermetrics_fiducial.py:94` (`DETECTION_PROJECTION_WALL_BUDGET_S = 120.0`, frozen),
  governed through `ESTIMATOR_CODE_PATHS` (`calibration_bracketing.py:239-244`) and bound into the calibration
  identity epoch. ED-RULING item 6 chose (c); `analysis_cadence_plan.md:34-37` planned (a).
- **Change.** The analysis replay keeps the reproducible cell budget (`:90`) and does not inherit the wall deadline.
  Reissue the calibration acceptance under the new code digest.
- **Rationale.** A firing depends on host load, is never a registered outcome, and costs a full rerun. It is the
  reason for the one-heavy-job rule.
- **Estimand.** No change to any estimand. Runs that would have fired now complete with the value the cell budget
  defines.
- **Blind.** Yes.

### 4.1 Estimator choices that must NOT change after anyone has seen data

Each of these fixes what is estimated or how a decision is made. Changing it after seeing values would let the
outcome choose the analysis.

| Choice | Where | Why it is locked |
|---|---|---|
| Analysed attempt = first claim-usable attempt per pack; superseded windows never analysed | PLAN 56-60, 70-73 | Picking windows after seeing energies is outcome selection |
| Exclusions come only from `exclusions.json`; ≥ 5 kept units per stratum; nothing else excludes | PLAN 77-91, 761-764 | Post-hoc exclusion is the classic forking path |
| Stratified 0.2/0.8 weights, V, df = min(n_r, n_b) − 1, the exact t quantiles | PLAN 224-232, 765 | They change the mean and interval directly |
| B: three bound kinds, stratified averages, `fsum`; envelope method and operative b; attribution floor = largest first-kind bound, printed and not added | PLAN 233-257 | They change interval width and the disclosed floor |
| Floors: D-054 point floor, guard g(n), corner widening (cap 16), D-124 comparative, worst-case composition | PLAN 295-337 | The floor decides `effect_not_above_floor` |
| Dominance R ≥ 2, branch A/B, R_cm | PLAN 344-360 | They license the dominance sentence |
| Contrasts: d_k, se_met = 0, t* rounded to 3 places, D, two-sided test, Holm m = 2 at α = 0.05, registered positive direction, outcome precedence, leave-one-quad-out rules, L2 conditions | PLAN 387-470, 769 | They are the confirmatory decision |
| Sensitivity lines: the three load codes, battery-assist rule, J6 b_sens = max(b_op, B_max) and its scope | PLAN 526-565; `RULING.md:140-160` | They must not be chosen by which one looks better |
| NEG-8 allowance source (re-screen vs stored) and the GAMMA midpoint rule | PLAN 105-148, 237-244 | They change D and the floors |
| Recompute agreement bars and the tie rule at thresholds (2.5 item 4) | `recompute_bars.json`; RS 340, 589-602 | A bar widened after seeing values can make any disagreement pass |
| Which side prints when lean and heavy disagree | 2.5 item 3 | Choosing by value is outcome-dependent |

How the numbers are computed (programs, caching, parallelism, hash binding, verification) can change blind at any
time under D-188's equality standard, because none of it touches an estimand.

## 5. Limits

- Every **E** figure applies a synthetic profile share to a real step wall that was measured on a loaded machine
  shared with dry-i. Steps 8, 6, 9, 10 and 11 have no profile.
- The lean runtime rests on two inputs: the 130 MB per-trace figure from a design note, and one background-QoS parse
  timing. The first real recompute run will settle it.
- Agent-assisted reading: two read-only seats inventoried `authentication_io`, the VDL and custody, and the
  deadline/frozen/cloud/comparator rules. Their citations were spot-checked: DL:207, DL:4452, DL:8706-8708,
  `authentication_io.py:1187` and `analysis_verified_store.py:829`.
