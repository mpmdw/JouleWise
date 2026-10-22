# BY-0: BYTES item H, its desk, C5 from partial data, and what the stop means for pass 1

Seat: Claude Opus 5.5, the lead's delegate (workflow item BY-0), 2026-10-21 18:29 to 19:10 PDT, interactive session
2dc9c377. Session `bytes-h-20261021T185555335572Z`, root `/Users/edr/night-bytes/h-20261021T185555Z` (written `R` below),
NON-CLAIM. Everything here is a registration candidate, not a registered value. Windows stay paused (RUN_STATE item 64).

Citation convention: `file:N` is a line in that file. JSON outputs of this item are cited by file and key. Untracked
item files are in `/Users/edr/night-archive/forward-20261021/BY-0/` (written `BY0` below). Scripts are in `BY0/scripts/`.

## Summary

- The desk ran once: `ops:h-desk` started it at 17:42:01 (pid 44586) and it finished at 18:45. It ran the h2 checkout at
  c10b6895f. `harvest_exit 0`, `gates_exit 1`, `chain_exit_code -15`. I did not run a second desk.
- Yes, this real session also fails with `decimal.ConversionSyntax`. The first field that raises is
  `runs["bytes-mac-check-soak-llama-70b-r12"].request_s = null` (`scripts/bytes_gates.py:100` → `:40`). Behind it, four
  more blockers would each stop c10b6895f's `bytes_gates.py` too (section 1.3).
- 70B soaks that count: **7 of 12** (r01, r03, r04, r06, r07, r09, r10). Thermal level 1 excludes r02, r05 and r08, agent
  presence plus thermal excludes r11, and r12 was in flight at SIGTERM. The 122B soaks: 0 of 12.
- The ops agent's fix (lane/2026-10-21-bytes-h-desk-partial at 66b330b15, pushed 18:59, after the desk) writes a C5.json on
  H's inputs (exit 2). I also wrote my own computation of every C5 line H can support (`C5-partial.json`). The two agree
  exactly on every line both compute (section 2).
- Sizing: measured module minutes are 0.85 to 1.99 times the pilot plan per model (1.16 to 1.99 per sub-pack). The
  measured science minutes for s3
  (265.8) and s4 (293.6) are above the 265-minute cap. Pass 1 needs about 32.7 h of measured session time, not counting
  the whole-window verdict, the backup or the desks.
- Disk: the measured copy factor c is 0.50 to 1.09 over the nine block-6 sessions and 0.80 for H, against the ruled c = 2.
- **Ed's MagSafe question: yes, it happened in H.** Every 70B and 122B large-workload run drew from the battery. The 70B
  request phase drew 8.9 to 27.1 J (0.29 to 0.84% of request energy). The rails boundary is unaffected. The DC-input
  boundary and "rest" miss that energy. This is flagged (`battery.assist`) but not corrected, and nothing in this item
  remedies it (section 9).
- 8B-8bit: **kept**.
- The h2 ledger has 408 rows against the committed pin of 402. Use a fresh checkout for the next prepare.

## 1. The desk (step 1)

### 1.1 Which desk produced the outputs

- Desk process: pid 44586, started Wed Oct 21 17:42:01 (from `ps -o lstart`). Its child harvest was pid 44587, whose
  working directory was the h2 checkout (`lsof -p 44587`, cwd line). Command: `python3.13 -B scripts/bytes_h_session.py
  desk --session-root R`.
- The desk ran from `/Users/edr/night-custody/measurement/JouleWise-measurement-20261021T1643Z-bytes-h2`, HEAD
  c10b6895fab0894b23b42ad439cf900c37d07c0b, with a clean tree. The harvest and gates argv go through
  `R/measurement/scripts`, which is a symlink to the h2 checkout's `scripts/` (`R/desk.json` `harvest_argv`/`gates_argv`).
- Outputs: `R/desk.json`, `R/MEASUREMENTS.json`, `R/export/bytes-mac-check/*`, and `R/staging/{harvest,gates}.{stdout,stderr}`,
  all with mtime 18:45. `desk1.out` is in the ops scratchpad (`.../scratchpad/hdesk/desk1.out`) and `desk1.err` is empty.
- `origin/lane/2026-10-21-bytes-h-desk-partial` was absent at 18:30 and present at 19:00, at 66b330b15 (committed
  18:59:26 -0700, after the desk's 18:45 outputs). It changes only `scripts/bytes_gates.py` and `tests/test_bytes_gates.py`.
  The outputs above therefore come from c10b6895f, not from the fix. No desk or harvest process was alive after 18:52
  (`pgrep -f 'bytes_h_session.py desk'` and `pgrep -f harvest_b6_session.py` found nothing).
- No second desk: the ops desk wrote its terminal outputs (`R/desk.json`), so the first of the three conditions failed.
- A later desk run from the fix branch would overwrite `R/`. The first desk's outputs are frozen, byte for byte, in
  `BY0/desk-copy/`. Hashes are in section 10.
- Night agents: `launchctl list | grep com.joulewise.night` gives rc 1 (no match), and `~/Library/LaunchAgents` holds no
  `com.joulewise.night*` plist (the only matches are `com.joulewise.b6loop.plist` and `com.joulewise.magistrate.plist`).

### 1.2 Exit codes

| Field | Value | Source |
|---|---|---|
| chain_exit_code | -15 | `R/custody/night/result.json:73`; `R/custody/night/chain.exited:3` (epoch 1792628359.85 = 17:19:19.85 PDT) |
| harvest_exit | 0 | `desk1.out:2`; `R/desk.json:976` |
| gates_exit | 1 | `desk1.out:5`; `R/desk.json:960` (`"status": "unavailable"`, `:983`) |
| gates stderr | `bytes_gates: [<class 'decimal.ConversionSyntax'>]` | `desk1.out:4`; `R/staging/gates.stderr` |
| harvest verdict | EXCLUDE, non-claim, 123 rows | `R/staging/harvest.stdout` (last line) |

### 1.3 The ConversionSyntax

Yes. This real session fails the same way the zero-run sessions did. The run below is reproduced by
`BY0/scripts/gates_traceback.py`, with output in `BY0/out/gates_traceback.txt`:

```
File ".../bytes-h2/scripts/bytes_gates.py", line 100, in calculate
    receipt[field] = number(receipt[field], run_id + "." + field, positive=True)
File ".../bytes-h2/scripts/bytes_gates.py", line 40, in number
    result = Decimal(str(value))
decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]
first raising input: bytes-mac-check-soak-llama-70b-r12.request_s = None
```

The input field is `MEASUREMENTS.json` `runs["bytes-mac-check-soak-llama-70b-r12"].request_s`, which is null. That is the
run in flight at SIGTERM. Twenty-eight planned rows carry null timing (`BY0/MEASUREMENTS.json` `flags`, 28 ×
`records.measurement_unavailable` per run field). If those rows were skipped, c10b6895f would still stop at:

1. `bytes_gates.py:106`: `cpu_contention.w_j_per_cpu_s` is null.
2. `:129`: "incomplete check/soak cannot size a candidate" (70B soak 11/12, 122B soak 0/12).
3. `:152`: `regimes.*.F_min_j` is null.
4. `:190` and `:219`: `operative_bound_s` and `sizing.fixed_desk_s` are null.

Items 1 and 3 hold for any H desk, complete or not. `bytes_h_session.py:545-546` reads `R/receipts/{regimes,cpu_contention}.json`,
and no program in the h2 checkout writes them (`grep -rn` of `scripts/` and `joulewise/` for `receipts/` and
`bytes_h_regimes`). This goes to BY-C5.

### 1.4 Expected record-only flags

| Expected | Found | Source |
|---|---|---|
| `calibration_ledger_head_uncommitted` in post-bracket-terminal-boundary.json | That file does not exist: post-calibration never ran. The code appears as the legacy code of `calibration.writer_record_flagged` on the reservation and fiducial writers ("skipped the committed-pin check"). | `R/archive/derived/flags.jsonl:348-349`; `R/custody/flags/core-reservation.jsonl:1` |
| `model.identity_unmeasured` | Raised at arm (collector timeout 55 s), then superseded by harvest checks (`records.identity_unmeasured_superseded`). Harvest emits `model.identity_mismatch` on 95 rows: the artifact sha matches, but the expected `runtime_identity_sha256` is null because the kit has no C4 pin. It also emits `model.identity_unrecorded` on 28 rows. Neither code is in the EXCLUDE lists. | `flags.jsonl:367`, `:5`; sidecar `flag_counts` |
| `agent.presence`, `agent.presence_overlap` from 17:17:43 | The presence interval runs from wall 1792628263.726 (17:17:43.726 PDT) to 1792628359.848 (17:19:19.848). First sighting at 17:18:13.730: `claude` pid 18442, then `npm`, `node` and `codex`. | `flags.jsonl:345`, `:209`; `R/custody/collection/agent_presence.jsonl:1-3` |

Other excluding codes in the sidecar (`EXCLUDE_WINDOW`, irrelevant to a non-claim kit): `structure.chain_crashed`,
`calibration.bracket_incomplete`, `code.number_bearing_unreviewed`, `cell.below_minimum`. Sidecar:
`R/export/bytes-mac-check/bytes-h-20261021T185555335572Z-calibration.session.json`, `flag_counts`.

### 1.5 Agent presence and the 70B soak count

Both `agent.presence` and `agent.presence_overlap` are EXCLUDE_MEMBER (`docs/registrations/bytes_pack_v1.md` at
91b20d7c2, line 342).

| Run | Export line (runs.csv) | Agent codes | Other excluding codes |
|---|---|---|---|
| soak-llama-70b-r11 (17:14:41.5 to 17:19:06.4) | 96 | agent.presence, agent.presence_overlap | thermal.os_level_nonzero |
| soak-llama-70b-r12 (in flight) | 97 | agent.presence | member.status_not_succeeded, member.bytes_missing |
| 26 unrun rows: soak-qwen35-122b r01-r12, test7 ends ×12, neg8-window-end r1-r3 | 98-124 (minus 97) | agent.presence | member.status_not_succeeded, member.bytes_missing |

Run spans are from `R/custody/collection/run_clock.jsonl`, the last two rows for r11.

**70B soaks that count: 7** (r01, r03, r04, r06, r07, r09, r10). Thermal excludes r02, r05 and r08 (runs.csv lines 87, 90,
93). Agent presence plus thermal excludes r11 (line 96). r12 failed (line 97). The 70B checks count 4 of 5, because r02
(line 76) is thermal. The `completeness` lines of `C5-partial.json` carry these counts in `counted_after_exclude_member`.

### 1.6 The export

- `R/export/bytes-mac-check/bytes-h-20261021T185555335572Z-calibration.runs.csv`, 123 rows (95 succeeded, 28 failed), sha256
  `b4f773153759bf06ce520f202c783ffcb4b06eb0d12f02f44834f898a3eb1bfb`. Frozen copy: `BY0/desk-copy/export/` (same hash).
- Its sidecar (same stem, `.session.json`) has sha256 `9f41df5ab461e4ca204a183c85942361dbefd33acdc341b38ff6cf8124e0d369`.

## 2. MEASUREMENTS.json and C5 (step 2)

### 2.1 MEASUREMENTS.json

- `BY0/scripts/build_measurements.py` builds it by calling the h2 checkout's own extractor
  (`bytes_h_session.measurements`, c10b6895f) on the session's native records. The result is `BY0/MEASUREMENTS.json`, sha256
  `17a8ad0671cbface743b741b0dd62ec1e4e649f4c23310b6ccd5eda2b6dea44d`, byte-identical to the desk's `R/MEASUREMENTS.json`.
- Independent check: `BY0/scripts/indep_measure.py` shares no code with the harvest. It re-derives four fields for all
  95 timed runs from the raw bundles and journals: `request_s` (events.jsonl sampling_started/stopped), `member_wall_s`
  (run_clock pair), `stream_s` (metadata clock stamps) and `thermal_level` (thermal journal overlap). All 380 values are
  bit-identical, and so are the 28 nulls (`BY0/out/build_measurements.log`: 492 fields checked, 0 differences). Bit identity
  is the right property because both sides subtract the same stored floats.
- Fields that stay null:
  - the 28 unrun rows;
  - all `regimes.*` (no floor, census or bound receipt; sidecar `operative_bound_s: null`, `.session.json:70`);
  - `cpu_contention.{w_j_per_cpu_s,c_q_cpu_s}`;
  - `sizing.{fixed_desk_s,collection_stage_overhead_s}`, because stages are missing (`bytes_h_session.py:708-709`).
- Clock values: `rate_ppm` 0.018668 (`MEASUREMENTS.json:6`), the worst per-member fit; its fit span is 128.05 s with n =
  129 and modelled SE 0.341 ppm. `frequency_word_ppm` is 0.0 (`:3`).

### 2.2 The three C5 computations

| Program | Inputs | Result |
|---|---|---|
| `bytes_gates.py` at c10b6895f (h2) | frozen export, `BY0/MEASUREMENTS.json`, kit plan | exit 1, no C5.json; stderr sha256 `1a76ca33…1d46`, identical to the desk's |
| `bytes_gates.py` at 66b330b15 (fix; tree extracted with `git archive` to `BY0/tree-66b330b15`) | same | **`BY0/C5.json`**, exit 2, sha256 `2219d5906e2424c286149f64097d80bb620e6979e0b8e5f74d0aeb9dfa51901b`; two runs gave the same hash |
| `BY0/scripts/c5_partial.py` (this item; imports c10b6895f's `clock_line`, `RESERVE_BYTES`, `SETTLE_S`) | same, plus `BY0/out/fixed_inputs.json` (measured sizing terms) | **`BY0/C5-partial.json`**, sha256 `9f0340ddbe72a92b7272541ab72b3255f44bd46f2ce4a70c2a6c1c7586c18b40`; two runs gave the same hash |

Cross-check (an executing review of 66b330b15). Both programs compute these quantities, and they agree with exact
equality, which is the right property because the arithmetic is the same on the same inputs:

- the margin, 0.03325233382759357;
- the list of 28 unmeasured rows;
- for every model: member-wall mean, request mean, est_minutes, T_stream_max and bytes_per_member;
- every completeness, clock, thermal and disk line;
- the projected footprint of all 12 pass sessions.

Two lines differ in how they are labelled, not in any number:

- 66b330b15 marks `sizing:*` "unavailable" because the two sizing receipts are null. C5-partial fills them from measured
  journals (section 8).
- `calibration_T10:*`: 66b330b15 prints `flag_only`, because the registered T10 is absent and that check comes first;
  C5-partial says the operative bound needs a complete bracket.

### 2.3 Per-gate table

| Gate family (count) | Status on H | Computable now or needs remainder | Source (C5.json / C5-partial.json `gates`) |
|---|---|---|---|
| completeness:<model>:check (10) | pass, 5/5 succeeded for every model; counted after EXCLUDE_MEMBER: 70B 4/5, others 5/5 | computable now | `completeness:*:check` |
| completeness:llama-70b:soak | fail: 11/12 succeeded, 7 counted | **needs remainder** | `completeness:llama-70b:soak` |
| completeness:qwen35-122b:soak | fail: 0/12 | **needs remainder** | `completeness:qwen35-122b:soak` |
| spread groups → margin | 10 check groups complete; 70B soak n = 11; 122B soak absent | checks now; soaks **need remainder** | `spread_groups`, `margin_missing_groups` |
| clock:session | pass: \|0.018668\| ≤ 5000/201.498 − 0.25 = 24.564 ppm | computable now (the 28 unrun rows repeat configurations already measured) | `clock:session` |
| clock:<model> (10) | pass, all; the tightest is 70B at 24.564 ppm | computable now (70B, 122B and Next-80B partial: test-7 ends absent) | `clock:*` |
| thermal | **fail**: maximum level 1 on 5 runs, all 70B | computable now | `thermal` |
| contention:<model> (10) | unavailable; T_max computed (e.g. 70B 57.44 s decode, 1.7B 2.34 s) | **needs receipt** (F_min_j, census_resolution_w, outside_power_w), not Mac time | `contention:*` |
| cpu_contention:<model> (10) | unavailable; per-run C and k computed | **needs receipt** (w, c_q) | `cpu_contention:*` |
| resolvability:<model> (10) | unavailable (F_min); min/max check decode J computed | **needs receipt** | `resolvability:*` |
| calibration_T10:<model> (10) | flag_only (registered T10 absent); operative bound null | needs a complete bracket (any full session) | `calibration_T10:*` |
| disk:kit | fail with the 150 GiB reserve, pass without it | computable now | `disk:kit` |
| disk:bytes-sN-pM (12) | fail with the reserve, pass without it (projected 26.5 to 45.2 GB against 108.6 GB free) | computable now | `disk:bytes-*` |
| sizing:bytes-sN-pM (12) | 66b330b15: unavailable; C5-partial: computed, margin incomplete | computable now with measured terms; the 122B soak spread **needs remainder** | `sizing:bytes-*`, `sessions` |

Disk note: `retained_bytes` counts the raw bundle plus its archive copy by `st_blocks`
(`bytes_h_session.py:643`). The archive is an APFS clone, so each run is counted twice: for example
`check-llama-70b-r01` shows 437,141,504 B, against 218,570,752 B for its raw bundle (`BY0/out/indep_runs.json`). The
measured physical drawdown in section 4 confirms that the clone allocated nothing.

### 2.4 Options for the lead, in Mac hours

Source: `BY0/out/options.json`, from `BY0/scripts/options.py`.

**(a) C5 from H as it stands.** It costs 0 Mac h; only desk compute, which is done. Slots that must be flagged:

- The margin comes from incomplete groups: 70B soak n = 11, and r11 is agent-contaminated; the 122B soak is absent.
- Test 7 has starts only, so no regime has passed test 7. The kit README says that "absent a passed test 7 the ruled scaled
  drift allowance still applies" (`configs/campaigns/bytes_mac_check/README.md:110-111`, c10b6895f). This holds for 70B,
  122B and Next-80B.
- The operative bound is absent. This is moot while the registered T10 is absent.
- The fixed desk time is a lower bound: the verdict and backup are unmeasured.
- 70B counts 4/5 checks and 7/12 soaks (thermal and agent).

**(b) A remainder session, BY-H2.** The table covers the stages H never ran, plus the fixed frame any session needs.
Test-7 starts must be in the same bracket as the ends.

| Term | Minutes | Basis |
|---|---|---|
| Frame: reservation 0.02, pre-cal 3.78, bound collection 40.70, bound derivation 11.98, ref-start 6.62, midpoint 2.13 (H) + ref-end 6.63, post-cal 3.97 (block-6 medians) | 75.83 | `BY0/out/fixed_stages.json` |
| Test-7 starts, 3 regimes | 34.23 | H stage spans 13.45 + 10.82 + 9.97 (`chain-stages.jsonl:10-12`) |
| Test-7 ends, 3 regimes | 34.23 | same configurations |
| Soak 70B ×12 | 53.43 | 12 × 263.43 s mean member wall + 44.4 s collection overhead |
| Soak 122B ×12 | 37.41 | 12 × 183.37 s + 44.4 s |
| Settles, 13 × 60 s | 13.00 | registered `SETTLE_S` |
| **Total** | **248.14 = 4.14 h** | plus 7 min prepare lead (`DEFAULT_LEAD_S` 420 s) and about 1.05 h desk (H: 17:42 to 18:45); verdict and backup unmeasured |
| Soaks only, no test 7 (variant) | 173.67 = 2.89 h | frame + both soaks + 7 settles |
| Optional known-bytes probe `scripts/bytes_stream_test.py` | about 60 | design R8 item 6, "known-bytes stream test (1 h)" (`docs/design/bytes_pack_design.md`@298a292a7:156) |

The trade-off:

- (b) costs about 5.3 h of Mac time before pass 1 can be registered with complete C5. It fills the 122B soak spread
  and test 7.
- Neither option produces the contention, CPU or resolvability receipts. Those need BY-C5 code, plus floors that only floor
  modules give.
- The 70B thermal exclusions will recur in (b): 5 of the 16 70B check and soak runs were at level 1 (section 7).

## 3. Sizing (step 3)

Pilot minutes come from `configs/b6/packs/bytes-sN-p1/registration.json`:300 and `:312` (c10b6895f). Measured minutes are
`C5-partial.json` `models.*.est_minutes` = 50 × mean member wall × (1 + margin) / 60, the formula of `bytes_gates.py`
(README `## C5 measured receipts`, lines 42-75). The table gives the tool's margin, 0.033252 (70B soak; max/min − 1 = 84.346 /
81.632 − 1, where the maximum is r11). It also gives an alternative margin, 0.019158: drop r11 for
agent.presence_overlap and the largest spread becomes the Next-80B checks (`BY0/out/options.json` `alt_margin`).

| Sub-pack | Model | Pilot est_minutes (line) | Measured mean member wall (s) | Measured est_minutes (tool margin) | No margin | Ratio measured/pilot |
|---|---|---|---|---|---|---|
| s1 | qwen3-1p7b | 65.546 (:300) | 129.13 (n 5) | 111.18 | 107.61 | 1.70 |
| s1 | qwen3-4b | 68.610 (:312) | 134.25 (n 5) | 115.60 | 111.88 | 1.68 |
| s2 | qwen3-8b | 73.384 (:300) | 141.44 (n 5) | 121.78 | 117.86 | 1.66 |
| s2 | qwen3-30b-a3b | 70.055 (:312) | 141.07 (n 5) | 121.47 | 117.56 | 1.73 |
| s3 | qwen3-14b | 80.681 (:300) | 153.52 (n 5) | 132.18 | 127.93 | 1.64 |
| s3 | qwen3-next-80b | 72.526 (:312) | 155.20 (n 5) | 133.64 | 129.33 | 1.84 |
| s4 | qwen3-32b | 103.617 (:300) | 192.81 (n 5) | 166.02 | 160.68 | 1.60 |
| s4 | qwen3-8b-8bit | 150.000 (:312) | 148.22 (n 5) | 127.62 | 123.52 | 0.85 |
| s5 | llama-70b | 151.580 (:300) | 263.43 (n 16) | 226.83 | 219.53 | 1.50 |
| s6 | qwen35-122b | 79.513 (:300) | 183.37 (n 5) | 157.89 | 152.81 | 1.99 |

| Sub-pack | Pilot total | Measured science (tool margin) | Alt margin | Over 265? | Measured session span, min (`sessions.*.est_minutes`) |
|---|---|---|---|---|---|
| s1 | 134.2 | 226.78 | 223.69 | no | 319.4 |
| s2 | 143.4 | 243.25 | 239.93 | no | 335.9 |
| s3 | 153.2 | **265.82** | 262.19 | **yes with the tool margin; no if r11 is dropped** | 358.4 |
| s4 | 253.6 | **293.64** | **289.64** | **yes** (28.6 min over; the plan had 11.4 min of headroom) | 386.3 |
| s5 | 151.6 | 226.83 | 223.73 | no | 314.2 |
| s6 | 79.5 | 157.89 | 155.73 | no | 245.3 |

- The pass-1 total is 1,959.5 min (32.66 h), not counting verdict, backup and desks.
- Pass 2 is identical in shape: `sessions.bytes-sN-p2` equals p1.
- Why measured exceeds pilot: the pilot priced a run as largest request + 57.6 s idle + 5.0 s settle, × 1.2
  (`docs/registrations/bytes_pack_v1.md`@91b20d7c2:90). The measured member wall also includes load, warm-up,
  cooldown, reduction and sampler wind-down. For 1.7B that is 129.1 s against the 65.5 s the pilot implied.
- Cap authority conflict, for the lead:
  - The brief says the pass sub-packs do not bypass the 265-minute cap.
  - Design Addendum 5 item 5 (`docs/design/bytes_pack_design.md`@298a292a7:266) says "fixed packs bypass the 265-minute
    science cap, and s4's planned 254 min leaves 11 min". Every draft registration repeats this
    (`configs/b6/packs/bytes-s*-p1/registration.json:24`), and so does the kit README (`:103`).
  - I flagged the cap as the brief asks. The texts treat it as a planning reference, not a refusal.

## 4. Disk (step 4)

- D = free_at_arm − free_at_desk_start.
- Arm: the minimum `free_bytes` over arm.json disk targets on the session device (`custody/hazards/arm.json`
  `hazards.disk[].measurement.values.targets[]`).
- Desk start for block 6: `archive.desk/compression-summary.json` `free_bytes_before`, line 1.
- Desk start for H: `desk1.out:1` (`free_at_desk_start_bytes`).
- One raw copy: block 6 uses the logical bytes of the `runs` files the desk compressed (`compression.jsonl`, rows with
  `root == "runs"`); this is a lower bound on the copy, so c is an upper bound. H uses the whole `runs-parent` tree.
- c_implied = D / one raw copy. D is a whole-volume drawdown: every writer on the volume, and any purge, enters it.
- Scripts: `BY0/scripts/disk_c_b6.py`, `BY0/scripts/disk_h.py`.

| Session | free_at_arm (B) | free_at_desk_start (B) | D (B) | One raw copy (B) | c_implied | Ruled c |
|---|---|---|---|---|---|---|
| r1-alpha | 174,331,416,576 | 162,829,508,608 | 11,501,907,968 | 20,055,016,087 | 0.574 | 2 |
| r1-beta | 169,934,139,392 | 158,655,823,872 | 11,278,315,520 | 20,447,426,571 | 0.552 | 2 |
| r1-gamma | 166,263,980,032 | 156,454,031,360 | 9,809,948,672 | 17,299,704,879 | 0.567 | 2 |
| r2-beta | 162,810,486,784 | 152,628,854,784 | 10,181,632,000 | 20,546,600,800 | 0.496 | 2 |
| r2-gamma | 159,616,585,728 | 150,028,029,952 | 9,588,555,776 | 17,391,012,615 | 0.551 | 2 |
| r3-alpha | 151,146,446,848 | 140,108,296,192 | 11,038,150,656 | 20,047,779,056 | 0.551 | 2 |
| r3-beta | 147,161,776,128 | 124,931,256,320 | 22,230,519,808 | 20,493,154,726 | 1.085 | 2 |
| r3-gamma | 154,232,840,192 | 144,652,926,976 | 9,579,913,216 | 17,307,433,044 | 0.554 | 2 |
| r4-alpha | 133,102,612,480 | 113,618,456,576 | 19,484,155,904 | 20,108,842,246 | 0.969 | 2 |
| **H** | 108,612,526,080 | 95,109,353,472 | 13,503,172,608 | 16,827,897,228 | 0.802 | 2 (`R/desk.json` `disk.peak_copies`) |

- r3-beta's D reproduces Sol's 22,230,519,808 B (`H-DISK-RULING.md:33`).
- No session exceeds c = 2, so the ruling's P stays conservative (ruling item 6, `H-DISK-RULING.md:36-39`).
- H's archive tree reports 17,387,397,120 B of st_blocks, yet D is smaller than the raw tree alone. This confirms that the
  APFS clone allocates nothing (`H-DISK-RULING.md:24`).

Per-model byte rates for BY-C5 (`BY0/out/disk_h.json` `per_model`):

- Bytes are the raw bundle's logical bytes, one copy.
- Stream rate is bytes / stream_s, and wall rate is bytes / member_wall_s, both from MEASUREMENTS.json.
- The maximum is taken over the model's timed runs, test-7 large runs included under the model.
- Reference = the corpus, window and test-7 reference runs.

| Model | n | Max stream rate (B/s) | Max wall rate (B/s) | Largest bundle (B) |
|---|---|---|---|---|
| reference | 28 | 1,804,717 | 1,285,174 | 161,258,849 |
| qwen3-1p7b | 5 | 1,765,389 | 1,259,496 | 162,353,765 |
| qwen3-4b | 5 | 1,712,552 | 1,229,284 | 164,392,290 |
| qwen3-30b-a3b | 5 | 1,702,395 | 1,175,865 | 164,886,672 |
| qwen3-next-80b | 5 (+2 test 7) | 1,667,324 | 1,074,350 | 166,448,056 |
| qwen3-8b | 5 | 1,647,340 | 1,189,692 | 167,127,192 |
| qwen3-8b-8bit | 5 | 1,599,209 | 1,146,843 | 170,008,455 |
| qwen35-122b | 5 (+2 test 7) | 1,560,317 | 950,974 | 171,857,043 |
| qwen3-14b | 5 | 1,555,674 | 1,131,363 | 172,689,325 |
| qwen3-32b | 5 | 1,322,761 | 982,811 | 188,477,464 |
| llama-70b | 16 (+2 test 7) | 1,098,577 | 833,842 | 219,530,249 |

The stream rate is not model-blind in H: it falls from 1.80 MB/s for the reference to 1.10 MB/s for 70B, so the longest
streams write the fewest bytes per second. The maximum still lies inside the block-6 range the ruling cites, 1,751,608 to
1,846,209 B/s (`H-DISK-RULING.md:11`).

## 5. Ledger (step 5)

- The h2 checkout's `runs/calibration_observation_ledger.jsonl` has **408 rows**. The committed pin
  `configs/calibration/calibration_ledger_head.json:2-3` says `"sequence": 402` with `head_digest 3ce1676c…0c08`.
- Row 402 is the last row whose receipt digest matches the pin (`receipt_digest 3ce1676c5304…`).
- Rows 403-408 are H's:
  - 403, 405 and 407 are append-intents;
  - 404 is `bracket-session-open` for plan `bytes-mac-check`;
  - 406 and 408 are the slot claim and finalization for `bytes-h-20261021T185555335572Z-cal-pre`.
- The bracket is open: no cal-post row exists, because post-calibration never ran.
- **Recommendation:** run the next prepare (BY-H2 or any pass session) from a fresh checkout. Its `runs/` ledger should be
  the 402-row committed state: `JouleWise-measurement-20261021T1548Z-bytes-h/runs/calibration_observation_ledger.jsonl`
  has 402 rows and tail digest 3ce1676c5304, equal to the pin. Check that rows = 402 and the tail digest equals the
  pin's `head_digest` before prepare.
- Reusing h2 carries the 6 uncommitted rows and the open `bytes-mac-check` bracket into the next session. Keeping them
  needs a deliberate pin advance to 408, the lead's call.

## 6. Qwen3-8B-8bit (step 6)

Rule text:

- Design R1 (`docs/design/bytes_pack_design.md`@298a292a7:31): "If it fails the resolvability check (R8 item 5) it is
  dropped before registration and the quantization sentence is deleted." Item 5 there is the download, so the check is
  R8 item 6, `:156`: "one non-claim resolvability, thermal and timing session (5 runs each …), reading structure only".
- Registration (`docs/registrations/bytes_pack_v1.md`@91b20d7c2:53): "It is kept only if it passes the resolvability
  check of R8 item 6 (a 3 to 5 run check that its decode phase is resolvable: block-6 design §14)".
- Block-6 design §14 (`docs/design/block6_collection_draft.md`@072ec6b8d:553): "New packs choose a prompt long enough that
  prefill and decode are both resolvable from the same runs … A 3 to 5 run resolvability check precedes each new
  configuration's registration."
- Kit README (c10b6895f, line 109): "no invented SNR cut drops 8B-8bit".

No numeric cut is registered, so I applied the rule as written: is the decode phase resolvable from the runs? In all 5 runs:

- status succeeded and not excluded (runs.csv lines 70-74);
- `measurement_quality.phase_identifiability.decode = "identifiable"`, `energy_uncertainty_status = "bounded"`, decode
  precheck `eligible: true` (`runs-parent/runs_bytes_mac_check/bytes-mac-check-check-qwen3-8b-8bit-r0N/summary_metrics.json:131`);
- decode energy 342.31 / 343.59 / 344.81 / 345.30 / 344.52 J;
- anchor-shift envelope half-widths 0.89 to 1.38 J (≤ 0.40% of the phase);
- decode duration 12.02 to 12.04 s;
- 512 tokens emitted.

For scale only, not as a cut: the smallest decode energy is about 340 times the attribution limit of about 1 J (design
@298a292a7:306). **Verdict: kept.** The `resolvability:qwen3-8b-8bit` C5 line stays "unavailable" until an F_min receipt
exists.

## 7. Thermal, contention and battery per stage (step 7)

- Stage spans come from `custody/night/chain-stages.jsonl:1-23`. The soak stage wrote no row; its span runs from the first
  soak start (`run_clock.jsonl`) to `chain.exited`.
- Journals: `custody/hazards/monitor/{thermal,contention,battery}.jsonl`. Script `BY0/scripts/stage_hazards.py`, output
  `BY0/out/stage_hazards.json`.
- "Over" counts the 10-s census intervals in which an outside process exceeded the registered 0.05 CPU-s/s limit
  (`monitor/config.json` `cpu_limit_s_per_s`). The monitor recorded these as flags and refused nothing.
- B0AC is the SMC battery current in mA; negative means discharging. PSTR and PDTR are the SMC power keys in W.

| Stage | Min | Thermal max (nonzero/readings) | Contention over / intervals | Max outside CPU s/s | Battery discharge readings / SMC | Min B0AC mA | Max PSTR W | Max PDTR W |
|---|---|---|---|---|---|---|---|---|
| bracket-reservation | 0.02 | none (0/0) | 0/0 | 0.00 | 0/2 | 0 | 7.1 | 14.4 |
| pre-calibration | 3.58 | 0 (0/43) | 7/21 | 1.35 | 51/220 | -20 | 108.9 | 108.7 |
| pre-cal window verdict | 0.20 | 0 (0/2) | 0/1 | 0.02 | 0/12 | 0 | 15.5 | 15.5 |
| bound-collection | 40.70 | 0 (0/489) | 19/245 | 0.51 | 0/2484 | 0 | 78.4 | 78.4 |
| bound-derivation.corpus | 5.93 | 0 (0/71) | 4/35 | 0.40 | 0/362 | 0 | 16.8 | 16.8 |
| bound-derivation | 6.05 | 0 (0/73) | 5/37 | 0.55 | 0/369 | 0 | 17.2 | 17.2 |
| reference-start | 6.62 | 0 (0/80) | 5/40 | 0.74 | 0/405 | 0 | 75.3 | 75.3 |
| test7-llama-70b-start | 13.45 | 0 (0/161) | 2/81 | 0.25 | 45/821 | -466 | 136.5 | 130.6 |
| test7-qwen35-122b-start | 10.82 | 0 (0/130) | 4/65 | 0.31 | 10/661 | -41 | 116.9 | 116.4 |
| test7-qwen3-next-80b-start | 9.97 | 0 (0/120) | 2/60 | 0.25 | 0/609 | 0 | 108.7 | 108.7 |
| check-qwen3-1p7b | 11.57 | 0 (0/139) | 6/69 | 0.37 | 0/706 | 0 | 89.7 | 89.7 |
| check-qwen3-4b | 11.77 | 0 (0/142) | 13/71 | 0.51 | 0/719 | 0 | 106.2 | 106.2 |
| check-qwen3-8b | 12.35 | 0 (0/148) | 9/74 | 0.42 | 0/754 | 0 | 109.0 | 109.0 |
| check-qwen3-30b-a3b | 12.45 | 0 (0/149) | 4/74 | 0.85 | 0/761 | 0 | 113.2 | 113.2 |
| check-qwen3-14b | 14.20 | 0 (0/171) | 19/86 | 1.23 | 0/867 | 0 | 113.5 | 113.5 |
| check-qwen3-next-80b | 13.77 | 0 (0/165) | 11/82 | 0.82 | 1/841 | -11 | 111.3 | 111.3 |
| check-qwen3-32b | 16.63 | 0 (0/200) | 5/100 | 0.38 | 0/1016 | 0 | 118.0 | 118.0 |
| check-qwen3-8b-8bit | 13.05 | 0 (0/157) | 15/78 | 1.20 | 0/798 | 0 | 114.0 | 114.0 |
| check-llama-70b | 22.65 | **1 (4/272)** | 14/136 | 0.57 | 108/1382 | -497 | 137.1 | 130.8 |
| check-qwen35-122b | 15.85 | 0 (0/190) | 10/95 | 0.64 | 24/968 | -76 | 117.0 | 116.5 |
| reference-midpoint | 2.13 | 0 (0/26) | 2/13 | 0.27 | 0/131 | 0 | 66.1 | 66.1 |
| soak-llama-70b (interrupted) | 49.90 | **1 (18/599)** | 31/299 | 1.63 | 244/3045 | -496 | 136.8 | 130.8 |

Run-level flags in the export (runs.csv, per stage):

- `contention.request_overlap` on 22 runs and `idle.busy_fraction_exceeded` on 24 runs. Both are disclosed only; neither is
  in the line-342 list.
- `thermal.os_level_nonzero` on 5 runs, all 70B: check r02 and soak r02, r05, r08 and r11 (runs.csv lines 76, 87, 90, 93,
  96).

The 70B soak shows a period-3 pattern (export rows and MEASUREMENTS, in run order). Each level-1 run (r02, r05, r08)
is followed by a run (r03, r06, r09) that differs from the other soaks (r01, r02, r04, r05, r07, r08, r10, r11) in
three ways:

| Quantity | Run after a level-1 run | Other soaks |
|---|---|---|
| Request | 81.6-81.7 s | 82.6-82.9 s (r11 is 84.3 s, agent present) |
| Request energy | 3,208-3,242 J (about 6% more) | 3,016-3,117 J |
| Battery assist | 24.6-27.1 J (about twice as much) | 8.9-12.4 J |

The checks repeat it after r02: r03 ran 81.5 s, used 3,266 J and drew 25.2 J from the battery. s5 (70B, 50 runs)
should expect about 5 of every 16 check and soak runs to be thermal-excluded, and a structured run-to-run swing. This
is non-claim and n = 16. Soak r11 also carries 55.37 outside CPU-s against 2.4-8.8 s for the other soaks
(`MEASUREMENTS.json` `runs.*.outside_cpu_s`): that is Ed's interactive session.

## 8. Fixed-stage minutes (step 8)

H's measured non-science stages are from `R/custody/night/chain-stages.jsonl` (integer-second stamps). For the stages H
never ran, the table gives the median of the nine block-6 sessions (`BY0/out/fixed_stages.json`; the block-6 range is in
brackets).

| Stage | H minutes | Lines | Block-6 median [min, max], n |
|---|---|---|---|
| bracket reservation | 0.02 | 1 | 0.02 [0.02, 0.03], 9 |
| pre-calibration (+screen +window verdict) | 3.78 (3.58 + 0.00 + 0.20) | 2-4 | 3.82 [3.78, 3.85], 9 |
| bound collection (+retry decision) | 40.70 | 5-6 | 40.62 [40.18, 41.90], 9 |
| bound derivation (corpus + derivation) | 11.98 (5.93 + 6.05) | 7-8 | 12.02 [11.48, 12.40], 9 |
| reference-start | 6.62 | 9 | 6.68 [6.60, 6.88], 9 |
| reference-midpoint | 2.13 | 23 | 2.12 [2.10, 2.17], 6 (gamma has none) |
| reference-end | not run | — | 6.63 [6.62, 6.70], 9 |
| post-calibration (+session status) | not run | — | 3.97 [3.93, 3.98], 9 |
| whole-window verdict, backup | not run | — | not timed in any chain journal on disk (block-6 chains end at post-calibration.session-status, 0.3-1.6 s before `chain.exited`) |
| settles | 60 s before pre-cal and before each collection (17.02 min over H's 23 rows) | gaps between rows | 11.0 min per block-6 session |

- Fixed non-science per session = 65.23 (H) + 6.63 + 3.97 = **75.83 min**.
- Add settles: 11 min for s1-s4 (10 collections) and 8 min for s5/s6 (7 collections). That gives **1.45 h / 1.40 h**
  per session, against the 3.6 h planning estimate.
- In C5 terms: `fixed_desk_s` = 1,185 s is a lower bound (H's reservation, pre-cal and derivation, plus the block-6
  post-cal median), and the collection overhead is 44.45 s (the mean over H's 16 completed collection stages; overhead =
  stage span − union of member walls). Both are in `BY0/out/fixed_inputs.json`.

## 9. Battery assist: Ed's MagSafe question

Ed asked whether the workload ever exceeded what the MagSafe supply provides, so that the machine ran partly on battery.
**It did in H, on every 70B and 122B large-workload run.** Sources:

- `R/archive/withheld/battery-assist.json`: harvest-integrated discharge, SMC B0AC × B0AV over discharge holds.
  Copied to `BY0/desk-copy/`, summarized in `BY0/out/battery_assist.json`.
- The monitor journal `custody/hazards/monitor/battery.jsonl`.

| Runs | Request-phase battery energy (J) | Share of request energy | Pre-request (load and warm-up) J |
|---|---|---|---|
| 70B: 5 checks, 11 soaks, 2 test-7 large | 8.85 to 27.05 | 0.29% to 0.84% (of 3,016 to 3,302 J) | 28.4 to 50.9 |
| 122B: 5 checks, 2 test-7 large | 0.80 to 1.43 | 0.16% to 0.28% (of 505 to 510 J) | 0.37 to 1.03 |
| Next-80B check r03 | 0.14 | 0.06% | 0 |

The mechanism is measured, not inferred:

- During the 70B stages the SMC system power key PSTR peaks at 137.1 W, while PDTR stays at or below 130.8 W.
- B0AC reaches −497 mA. At B0AV ≈ 12.8 V (12,785 mV at session start) that is about 6.4 W, close to the 6.3 W gap
  between PSTR and PDTR.
- The adapter reports 140 W (ioreg `adapter_watts`). The pack stayed at 100% charge with external power connected and
  never charging (`current_capacity_pct` minimum 100; `external_connected` false 0 times; section 7 table).
- So the battery floats at full charge and covers short peaks above what the supply delivers.

What it affects:

- **Rails** (powermetrics CPU+GPU+ANE): nothing. Rail energy does not depend on the source (ruling of 2026-10-06,
  `docs/process_traces/2026-10-07-block5-seal/RULING_STAGE1.md:383`).
- **DC input** (KM003C after the adapter) misses the battery's share. For 70B that is 9-27 J per request, 9-27 times the
  ~1 J attribution limit. **Rest** = DC input − rails inherits the same deficit.
- 122B's 0.8-1.4 J is at the attribution limit. Next-80B's is below it.

Current handling:

- `battery.assist` and `meter.battery_activity` are disclosed on 26 runs, and `battery.accumulator_activity` on 16.
- None of these is EXCLUDE_MEMBER (`bytes_pack_v1.md`@91b20d7c2:342 lists only `battery.accumulator_excursion`,
  `battery.capture_pair_failed`, `battery.member_span` and `battery.unmeasured`).
- Block-6 design §13 item 5 (`block6_collection_draft.md`@072ec6b8d:519) keeps the battery term at request level and flags
  the phase.

**Not remedied by this item**: nothing in its write scope touches code or registration. Candidates for the lead or BY-C5:

1. Add the SMC-integrated discharge energy (already in `withheld/battery-assist.json`) to the DC-input term of flagged
   phases, with its own 1-s-cadence uncertainty.
2. Or print 70B's (and 122B's) DC-input and rest lines with battery-assisted phases as a labelled line.

Either needs a registration line before s5. Rails-based lines are unaffected.

## 10. Reproduce (for the lead) and files

The commands use the h2 venv (`/Users/edr/night-custody/measurement/JouleWise-measurement-20261021T1643Z-bytes-h2/.venv/bin/python`,
written `PY` below) and the frozen inputs:

```
E=BY0/desk-copy/export/bytes-h-20261021T185555335572Z-calibration.runs.csv
PY -B <h2>/scripts/bytes_gates.py --runs $E --measurements BY0/MEASUREMENTS.json --kit-plan BY0/desk-copy/collection_plan.json --out /tmp/x.json   # exit 1, stderr sha 1a76ca33…
PY -B BY0/tree-66b330b15/scripts/bytes_gates.py --runs $E --measurements BY0/MEASUREMENTS.json --kit-plan BY0/desk-copy/collection_plan.json --out C5.json   # exit 2, sha256 2219d590…901b
PY -B BY0/scripts/c5_partial.py <h2> $E BY0/MEASUREMENTS.json BY0/desk-copy/collection_plan.json C5-partial.json BY0/out/fixed_inputs.json   # sha256 9f0340dd…8b40 (output path is not hashed into the file)
```

| File | sha256 |
|---|---|
| export runs.csv | b4f773153759bf06ce520f202c783ffcb4b06eb0d12f02f44834f898a3eb1bfb |
| export session.json | 9f41df5ab461e4ca204a183c85942361dbefd33acdc341b38ff6cf8124e0d369 |
| kit collection_plan.json (c10b6895f = 66b330b15) | 73569187bb332cc5aaeab3633716117f25dd7c53e6deb67dd38db51aa7faac49 |
| MEASUREMENTS.json (desk = BY-0) | 17a8ad0671cbface743b741b0dd62ec1e4e649f4c23310b6ccd5eda2b6dea44d |
| C5.json (66b330b15) | 2219d5906e2424c286149f64097d80bb620e6979e0b8e5f74d0aeb9dfa51901b |
| C5-partial.json | 9f0340ddbe72a92b7272541ab72b3255f44bd46f2ce4a70c2a6c1c7586c18b40 |
| fixed_inputs.json | c0d537a2831598795ca5bc2f83496f5fe5c490ab52a24ce65335517f0313bc31 |
| desk.json | cde72b7016a9a23fdfb24ec933eea09099bc0e73833c4e9c907319a2afee4a4f |
| battery-assist.json | 68e0ed440fcb785a82f4971e22ce0c6bf67a0ef9649c4cfa7465508356c1f0dd |

Non-claim tables and scripts: JouleWise-data branch `analysis/bytes-h-desk-20261022` at 8db1b40, directory
`bytes-h-desk-20261022/`.
Item processes: none left running. Disk at the end: 91 GiB free (`df -g /Users/edr`), above the 10 GiB stop line.
