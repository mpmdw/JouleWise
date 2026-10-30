# Magistrate activation 4e748ac1 (Opus 5.5, headless, 2026-10-30 from 11:26 PDT)

Launched by the watchdog at 11:26:49 (attempt 1240, last exit class `usage_exhausted`). Pending notices: none. Gmail `from:claude2.glaring610@passmail.net is:unread`: none. Open directives: #587, #422, #421, #417, #416, #408, #405, none new.

## State at launch
- BYTES loop: `r2-bytes-s1-p2` (the last pass-2 session) at SESSION_DESK since 11:26:26 (chain rc 0, no physics stop; t0 05:46 PDT). The loop's desk harvest is running. Its measurement HEAD is `f1a55bb40` (pin-only, ledger seq 530, bracket session `r2-bytes-s2-p2-calibration`; tree `feac5c057`), from `custody/night_plan.json` `measurement_head`; the smoke fingerprint's `code_commit` agrees, OS 25G83.
- Canonical root fast-forwarded `4c26b2e2c` to `3b0ad9b5a` (24 commits: #609, #611, #612). Checked first: no `com.joulewise.night*` label loaded and no such plist on disk (only `com.joulewise.b6loop`, its wake label and the magistrate).
- Disk: 161 GiB free.

## Cloud seats from activation a7d07c32, read and dispositioned
All three had finished by 03:49 PDT; none had been read.

**KB-V2 Opus delta of round 8** (JouleWise-data `claude/kb-v2-delta-opus-5` `b9352203`): ACCEPT_WITH_FIXES.
- MAJOR 1 (pre-existing): cross-leaf producer invariants are not checked. A receipt whose `repeats` disagrees with `bytes_read`, or a `knee found` scan whose sizes are not the producer's functions of K, prints RESOLVED with smaller half-widths (doubling `repeats` halves every printed half-width). Reproduced at `156f03110` too.
- MINOR 2: `knee found` with failed arm checks or a `reason` is read as found.
- MINOR 3: the DC gate tests the half-width before K1's finite-positive check, so a non-positive DC half-width does not block the other classes (no input found that reaches it).
- K1-K4 confirmed; 62,046-case fault walk with 0 crashes; worked output bit-identical; bars unchanged.
- Disposition (lead): the item-150 pointer admitted the rule only with no MAJOR, so a small round 9 (rulings L1-L4) instead. It is a new mechanism (cross-leaf), not the third appearance of a single-leaf class, so it is a fix round, not a consult. Sol's MINOR 1 (5,001-digit integer) stays unfixed and recorded: the producer never writes it and no number is at stake. After round 9 the lead re-executes the Opus `p8_*` repros and admits the rule if each ends reasoned; no further blind round unless a repro still prints a smaller bound.

**BY-THERM-LINES Fable consult** (JouleWise-data `claude/by-therm-consult` `0858773e`): one structural trust rule. Root cause: trust was decided per consumed field by whatever the consumer checked, never per source by the producer's contract. Rule: every source goes through one validator with three parts: whole-document strict JSON lexing; exact types on consumed fields; producer invariants (nested spans, pack tree named by the roster's `pack_id`, journal replay reproduces the registered hull decision, exclusion rows name roster members). Prototype (213 insertions, script only) closes every reviewer cell and a generated 684-cell matrix (baseline 237 failures in 52 kinds), and marks no real-harvest member untrusted.
- Disposition (lead): adopted as rulings X1-X12 (the consult's 1-12), including ruling 6 without the no-`pack_id` fixture allowance and the consult's journal-replay condition over the lead's weaker "one usable reading" candidate (the consult showed the weaker bar still restores a member). Not adopted: nothing. Fix round 5 then one blind delta round (Sol plus Opus).

**BY-EXT-2 Opus executing review** (JouleWise-data `claude/byext2-rev-opus` `5642afec`): ACCEPT_WITH_FIXES. Part A (dense Qwen3.5 manifest support) is correct: an independent census equals W 27,228,623,168 B and R 28,579,478,528 B. Three MAJORs in the non-claim kit tooling: the extension merge guard protects only the frozen manifest path (hard link, registered records and identity pins can be overwritten); the checker accepts a decode phase longer than its request; an export missing planned members passes. MINORs: bool/string sizing operands; the frozen original kit's generator digest drift.
- Disposition (lead): fix round with rulings E1-E5; Opus 5 recorded, not fixed (historical kit); Opus 6 one README line; Opus 7 a comment. The Mac kit run waits for this fix, because the fix may regenerate the extension kit tree.

## Seats launched (Codex Cloud, gpt-6.1-sol, model and effort read back)
The Mac is at a desk now and runs the BY-EXT kit after it, so Sol runs in the cloud.
- KB-V2 round 9, high: thread `01a18e14-5fdd-764c-8c44-46be46d80014`; brief `~/night-archive/seats-4e748ac1/kbv2-fix9/brief.md`.
- BY-THERM-LINES fix round 5, xhigh: thread `01a18e14-605d-7371-8e3c-e1784bf8703a`; brief `~/night-archive/seats-4e748ac1/by-therm-fix5/brief.md`.
- BY-EXT-2 fix round, high: thread `01a18e14-5fa4-72c1-bc48-89149aff5035`; brief `~/night-archive/seats-4e748ac1/byext2-fix/brief.md`.

## BY-EXT-2 fix round (seat finished 11:4x)
- Head `ee439ce19` on `desk/2026-10-29-byext-slots`: E1-E5 implemented; only the two scripts, their tests, the extension kit's README and plan tree, and the report changed; registered BYTES files and the original kit unchanged. Part A census unchanged (W 27,228,623,168 B; R 28,579,478,528 B). Seat ran 81 tests OK and `repin --check` PASS.
- Lead re-execution: the Opus `checker_faults.py` at `ee439ce19` gives OK on every case (decode 60 s against a 50 s request and 1e12 s now fail; the missing midpoint and five-rows-only exports fail with the missing run ids; bool and string sizing fail). Log `~/night-archive/seats-4e748ac1/byext2-fix/lead/checker_faults_ee439ce.log`. The merge-guard repro is Linux-path bound; it was rerun by the seat, and the new manifest tests cover each case.
- PR #608 had become unmergeable against main (no CI on the new head). It now targets `ci/2026-10-30-byext-base` = `4119e14bf`, the lane's own base, so CI runs the lane's tree.

## Mac path scout (Sol high, Codex Cloud `01a18e1e-9a8e-734e-9429-f72ee2d9802c`; report `.codex-report/MAC-PATH-SCOUT.md` on `codex/2026-10-30-mac-path-scout` `c2b19b234`)
Neither Mac run has an executable recipe today.
- **KB-V2 stream test:** the probe, `scan` and `read` exist, but nothing runs the test unattended under one continuous capture, and no harvest step builds the reader's input from a capture (the rule's "Capture and harvest" paragraph; KB-V2 report). This is on the path to BYTES stage 1 (registration §1 and §19: after collection, before stage-1 unblinding).
- **Extension kit:** `scripts/bytes_h_session.py` hard-codes the original kit; a kit selector alone fails at `registration.load_sizing` (no extension registration directory exists). It also needs extension-local registration, sizing and pin inputs, the extension roster in the identity mapping, and checker dispatch at the desk. The kit's own sizing does not exist yet, and S cannot be used for it.

## Lead decisions
- **KB capture lane launched:** KB-CAP-1 (Sol xhigh, design then build; brief `~/night-archive/seats-4e748ac1/kb-cap1/brief.md`; branch `codex/2026-10-30-kb-capture` from the KB-V2 branch). Preferred vehicle: one non-claim night window through the existing driver, with one new stage kind and a harvest producer that calls the pass-1 integrators unchanged, run end to end on production-shaped synthetic data.
- **BYTES extension (Qwen3.8-27B-8bit) dropped under its registered rule**, "dropped first if time runs short" (`docs/registrations/bytes_extension_models_2026-10-27.md`; item 77 (0c)). Here is what remains before its last allowed t0 (2026-11-05 00:00 PDT):
  - a runner lane;
  - extension registration and sizing inputs;
  - the kit run (quiet Mac, no agent alive);
  - sizing, regeneration, a refuter gate and C4 pins;
  - an s7-p1 smoke and session of about six hours.
  The KB test needs the same quiet Mac before stage 1, and it is registered while the extension is not. The BY-EXT-2 code (manifest support and the kit, fixed and verified) stays on `desk/2026-10-29-byext-slots` for a later block. Ed is told in the s1-p2 verdict email and may overrule.

## KB-CAP-1 round 1 (Sol xhigh, Codex Cloud `01a18e26-8fa1-7392-80c7-75256c151002`; `7978d95e9`, draft PR #613 into the KB-V2 branch)
- Vehicle: the existing night driver and installer (hazard arm, agent census, network-time OFF, instrument checks, meter supervision). The graph is reservation, pre calibration, a new `bytes_stream_capture` stage, then post calibration. The stage holds one `powermetrics` capture and one meter stream across the scan and the eight calls. It uses a fresh test-only ledger with a genesis pin, and no claim ledger is copied.
- Producer `scripts/bytes_stream_harvest.py`: every INPUT field is mapped to its source function. The integrators are the existing ones, unchanged. The meter-edge and battery-edge fields adapt `meter_decode`'s edge prescription, because `meter_decode` refuses gap-bearing spans. That is new number-bearing code, so it goes to the executing review.
- End to end on synthetic data through the real driver, chain, stage, probe, harvest and reader: the knee was found and all 8 records were written. DC was RESOLVED. Rails, GPU and rest stayed UNDETERMINED because the fake calibration supplied no fiducials, so the anchor-shift path never ran.
- Report error: it gives the agreement bars as 5.7e-8 J/GB and 4.5e-9 GB/s. The correct bars are 5.7e-6 J/GB and 4.5e-7 GB/s.
- Round 2 launched (Sol high; brief `~/night-archive/seats-4e748ac1/kb-cap2/brief.md`). It has five parts:
  - Y1: production-shaped calibration fiducials, so every number path runs end to end.
  - Y2: an independent recompute of one call's integrals, with a 1%-of-half-width bar.
  - Y3: correct the bar text.
  - Y4: derive the disk input from recorded byte rates, and the adapter rating from where the repo records it.
  - Y5: run the slow stream module to completion.
- Then a blind executing review by Opus and Fable. KB fills a registration claim slot (§1), so cold passes come before the live run.
- PR #608: retargeting did not start `ci.yml`, because `edited` is not one of its trigger types. Closing and reopening the PR started it.

## KB-CAP-1 round 2 (Sol high, `01a18e47-295c-7019-845e-2fc3da1a103f`; head `c2b850860`)
- Y1: synthetic pre/post calibration now carries authenticated fiducials, and the real `read_own_capture` and `calibration.evaluate` run. The whole chain ends with rails 7.000 ± 0.014, GPU 7.000 ± 0.014, DC 14.08 ± 0.10 and rest 7.077 ± 0.094 J/GB, share 0.4973 ± 0.0046, all RESOLVED from computed bounds. The missing-fiducial chain stays reasoned UNDETERMINED (DC still RESOLVED).
- Y2: an independent first-call recompute agrees within 5.7e-6 J/GB × 4883.38 GB = 0.0278 J (rails 41118.84 J, meter 82186.93 J, both edge arrays). The missing-sample count matches exactly.
- Y4: adapter 140 W from `bytes_pack_v1.md:176`. Disk `2*ceil(rate*10390)+4046531103 = 56,028,277,617` B from `sizing_b5.json` `/packs/bytes-s1-p1/disk_derivation`.
- Y5: `tests.test_bytes_stream_test` 49 OK (894.6 s); new modules 12 OK; registries 28 OK.
- Cold executing passes launched, blind to each other: Opus 5.5 `session_01JActAcJs7nY7T1hiBnqf4T` (JouleWise-data `claude/kb-cap-cold-opus`) and Fable 5.1 `session_01JActAaXwrUjxrXHGpzBuet` (`claude/kb-cap-cold-fable`). Briefs are in `~/night-archive/seats-4e748ac1/kb-cap-cold/`.

## s1-p2 desk (about 13:20): BYTES collection complete
- **r2-bytes-s1-p2 counts:** COLLECTED, acceptance ACCEPT, counting, no session-excluding reason, no structural defect. 125/125 planned runs succeeded (absolute 10+10, quads 40+40, NEG-8 18, references 3+1+3); `excluding` is empty (no member exclusions). NEG-8: corpus clean n 12, survivors start 3/3, mid 1/1, end 3/3, screen passed. Cells: `bytes-qwen3-4b-decode` and `bytes-qwen3-1p7b-decode` both 10/10 quads and 10/10 repeats. Member-hull line: 0 of 100 excluded, 0 undetermined. No unreviewed code, no model mismatch. Minutes: chain 324, harvest 92, desk 100.
- All twelve sub-packs have a counting session; loop state DONE (round 2). `com.joulewise.b6loop` and its wake label stay loaded and idle.
- Measurement line: pin-only `1aca17e27` (seq 540) after the desk; `records/bytes-pass2-heads` fast-forwarded `da20a8324` → `1aca17e27`; `2649fad54..1aca17e27` changes only the ledger head file. BYTES addendum §5 appended on this records branch.
- Verdict email: Gmail `1a18e7d872dd7507` (thread `1a174cad9022cac9`). It also tells Ed the extension was dropped and how to overrule it. No pending notices, so no acknowledgement was written.

## KB-V2 round 9 (seat stalled at 45 min on the client side, but finished: `559197821`) and the rule admitted
- L1-L4 implemented: 127 tests OK; worked output bit-identical; both leaf walks give 62,046 cases with 0 crashes.
- Lead re-execution at `559197821`: the fixture was rebuilt with opus-4's `e2e_nonneg.py` through `run_with_clock.py`, then Opus 5's `p8_major_cli.py` and `p8_grid.py` were run. Every inconsistent-receipt and inconsistent-scan shape, plus `knee found` with failed arm checks or with a reason, now ends UNDETERMINED with its reason and no interval. The baseline is unchanged (rails 0.06672 ± 0.00057 … share 0.3458 ± 0.0075). Logs are in `~/night-archive/seats-4e748ac1/kbv2-fix9/lead/`.
- **Rule admitted** (pointer item 150 (1b): no MAJOR left). Status paragraph updated on `codex/2026-10-28-kb-v2` at `a3226e87f`.

## BY-THERM-LINES round 5 (stalled client-side, finished: report `3ee2b83f3`, code `5a91ce575`)
- X1-X12 implemented. Tests: `tests.test_bytes_thermal_lines` 45 OK (1132 s; within 1.5x of round 4); p2-thermal-window plus harvest 198 OK with 177-file byte identity. Matrices: consult 684/684 (baseline 237 failures), Opus 324/324, Sol 80/80 and 360/360. Real chain 44/44, with zero untrusted members and zero replay disagreements. Census: s2 and s5, both passes, source rows equal output rows. Pinned hashes unchanged.
- Blind delta round launched: Opus 5.5 `session_01JActAbTbhJD2mA3d5qztYq` (JouleWise-data `claude/by-therm-lines-delta-opus-4`) and Sol high (Codex Cloud; `codex/2026-10-30-by-therm-lines-rev-sol-5`). Briefs are in `~/night-archive/seats-4e748ac1/by-therm-delta5/`.

## KB-CAP-1 Opus cold pass (`claude/kb-cap-cold-opus` `e7acfcd2f`): ACCEPT_WITH_FIXES
- The number path is correct. An independent recompute with no joulewise imports agrees on calls 0, 3 and 7 for every field (largest energy difference 2.9e-11 J against bars of 5.95e-4 to 2.78e-2 J). `meter_fields` matches pass-1 `meter_decode` in all 8 worlds wherever pass-1 accepts the call. The 7 s offset is not added twice. No refusal yields a smaller bound.
- MINORs:
  1. A truncated receipt or SCAN/STAGE JSON crashes harvest. A SIGTERM mid-write makes this reachable.
  2. A non-object thermal-journal line crashes harvest.
  3. Harvest follows symlinks out of the archive (hash only).
  4. STAGE.json's specific failure reason is not carried into the diagnostics.
  5. A native-capture failure drops `capture_stack`.
  6. The 140 W adapter citation is wrong (it is §6 Battery assist, not §7/R5) and is not a nameplate.
- NITs: SIGKILL grace is missing from the span (worst case about 150 s against 50 s of slack); a dead `started` flag; an incomplete battery tail nulls both edges; the archive copy step runs on even when the target exists.
- Disposition waits for the Fable pass, so both reports go into one fix round.

## KB-CAP-1 Fable cold pass (`claude/kb-cap-cold-fable-v646v6` `acc3337ff`): ACCEPT_WITH_FIXES
- Independent recompute on all eight calls: the worst difference is 5.6e-6 of the bar (anchor shift); every other field is bit-identical. `meter_fields` equals `meter_decode` in 5 worlds; the offset is consumed once (adding it twice would be off by 140 J). Refusals are reasoned, and nothing is opened outside the archive.
- MAJOR 1: `t_stream_max_s = CALL_S['S']` (500 s) has no derivation. The threshold is defined as the longest sampler stream (`hazards/clock.py:74`), and the sampler stream here is the one continuous capture, about 4630 s. Under the pass-1 formula the admitted rate drops from 2.35 ppm to 0.031 ppm. No printed number depends on it, but it gates the night.
- MINORs: the stage module needs a `sys.path` insertion when executed by path; the adapter citation is secondary (the supply's own record is `docs/phase_2/window_c_operator_checklist.md:32`); an absent calibration capture prints `diagnostics: []`. NITs: an existing `--out` gives a traceback; the `started` flag; the scan allowances are upper bounds.
- Both passes agree the number path is right. Disposition: round 3 (Sol high, brief `~/night-archive/seats-4e748ac1/kb-cap3/brief.md`), rulings Z1-Z8. Z1 sets `t_stream_max_s` to the continuous capture's planned length (the threshold's own definition) and replays the resulting bound against every recorded arm clock-rate measurement before it is used. If it would refuse clean sessions, the numbers come back as NEEDS_RULING (doctrine rule 9). Opus 9 and Fable 7 are not changed (conservative; allowances).

## KB-CAP-1 round 3 (`a6c68c408`)
- Z2-Z8 done. Harvest now writes a reasoned INPUT.json on malformed JSON instead of crashing; outside symlinks are skipped and diagnosed; stage and calibration reasons reach the diagnostics; `capture_stack` is kept. The adapter source cites `docs/phase_2/window_c_operator_checklist.md:32`. The span now includes the SIGKILL grace: 10510 s (disk 56,628,644,275 B; `window_max_s` 13860). Path execution works; `--out` refuses with one line. Tests: 30 OK for the new modules; chain plus registries 53 OK. The reader's printed output equals round 2's, and the cold-pass repros end reasoned.
- **Z1 NEEDS_RULING (doctrine rule 9 replay):** `t_stream_max_s` = 4629.6 s (the continuous capture) admits |rate| ≤ 0.0308 ppm. All three recorded arm rates on this Mac are 2.718 ppm (BETA a5 and a6, GAMMA a1; a6 and a1 claim-usable), so the gate refuses 3 of 3 (bound 17.44 ms against 5 ms). The round-1 500 s value would also refuse them (it admits 2.35 ppm).
- Science question, so a two-seat blind council: Opus 5.5 `session_01JActAZwBL8rX9DwjtuhJvR` (JouleWise-data `claude/kb-clock-consult-opus`) and Sol high (`codex/2026-10-30-kb-clock-consult-sol`). Brief `~/night-archive/seats-4e748ac1/clock-council/`. The question: where the anchor-versus-RAW rate actually enters this pipeline's numbers (one anchored point plus `elapsed_ns` accumulation, or wall dates), the error in joules per call at 2.718 ppm against the 1% bar and the reader's own timing terms, and one recommended gate with its replay.

## BY-THERM-LINES Sol delta 5 (`codex/2026-10-30-by-therm-lines-rev-sol-5`): ACCEPT_WITH_FIXES
- X1-X12 hold. The lexer matches `json.loads` with duplicate-key rejection on 40,000 mutations. A fresh real-harvest archive kept all six members trusted. The census passes, `tests.test_bytes_thermal_lines` 45 OK, and the pinned hashes are unchanged.
- MAJOR (inherited): a string `session_id` such as `../../../escape` builds a withheld export path outside the output and overwrote a sibling file. It does not change which members count; the fix is a containment check.
- MINOR (inherited): a sealed level of `10**1000` raises `OverflowError` in the production helper (exit 1, no record).
- The disposition waits for the Opus delta.

## BY-THERM-LINES Opus delta 4 (`claude/by-therm-lines-delta-opus-4` `e1b61a4d7`): REJECT
- BLOCKER 1: the journal is not read the way the production parser reads it (consult §2 row 7). The production reader accepts four kinds of sealed line that the L1 writer never emits: a repeated key, NaN, a lone surrogate, a BOM. The lexer drops them as malformed. The tool then computes the request-end line on a different set of readings and restores a member (4 of 4 cases). Exposure on real L1 data is nil: on a fresh real harvest the tool's and production's readings agree, 103/103.
- MAJOR 2: repeated roster `run_id`s are accepted, so one member is evaluated twice and duplicate rows are written.
- MINOR 3: the replay-disagrees notice is emitted when no replay was possible. NITs 4-5.
- Held: the lexer equals strict `json.loads` on 200,000 fuzzed documents (lone surrogates aside); every validator held; no wrong refusal on a new production-shaped harvest; pass identity, verify roots and export cases all held; both modules pass.
- Lead disposition: fix round 6 (Sol high; brief `~/night-archive/seats-4e748ac1/by-therm-fix6/brief.md`), rulings A1-A5 (Opus 1-3, Sol 1-2); Opus 4-5 unchanged.
  - Why a round and not a consult: the class appeared again, but each instance is a departure from the adopted consult's own rule (row 7 says the production parser's readings; X7/X8 say producer-possible identities), not a gap in the rule. Each fix is local and fully specified. A second consult would re-derive the same rule.
  - After round 6, the lead re-executes Opus's `probe_journal_divergence.py` and `misc_probes.py` and Sol's two repros. Another blind round follows only if a probe still changes which members count.

## Clock-gate council (two blind seats)
- **Sol** (`codex/2026-10-30-kb-clock-consult-sol` `16373533b`): (a) keep the strict 4629.6 s gate for the code as written. The production ACTIVE anchor method `CLOCK_METHOD_V3` refuses a capture whose wall-minus-RAW span exceeds 5 ms (`uncertainty_evidence.py:40, :1090-1125, :1374-1381`). At 2.718 ppm × 4629.6 s that span is 12.58 ms, so a live run would lose rails and GPU even with the gate removed. The synthetic capture seam supplies its anchor directly and hid this. Sol warns that naive re-anchoring at receipt or stdout time is unsound.
- **Opus** (`claude/kb-clock-consult-opus`): (d) then the carried gate.
  - Where the wall-vs-RAW rate enters a joule as coded: only a rigid ≤ 40.8 µs pairing offset, which `anchor_shift_j` already covers about 265 times over.
  - Where it decides admission: the V3 cap. Executed: unknown at 2.718 ppm over 4629.6 s.
  - Fix: the unchanged V3 estimator over a ≤ 123 s prefix, closed by an in-stream epoch/RAW stamp, plus an end-of-capture check. Executed: a constant ~115 µs error from first record to last.
  - Then `t_stream_max_s` = 335 s, which refuses 0 of 3 recorded arms (4.694 ms, the value they printed).
- Both agree that the rate does not reach the numbers once an anchor is resolved, and that the strict gate is correct for the code as written. They disagree on whether the prefix re-anchor is sound, which is a science question, so it goes to a **cold Fable 5.1 judge**: `session_01JActAYZjhhpgNjte13zbFk` (JouleWise-data `claude/kb-clock-judge`; brief `~/night-archive/seats-4e748ac1/clock-judge/brief.md`).
- Consequence: the KB test is not armed in this activation. As coded it would collect no rails or GPU numbers on this Mac. The KB lane waits for the judge's ruling and then a build round with its own cold passes. BYTES stage 1 is planned for 12 Nov, so there is room.

## Cold Fable judge on the clock question (`claude/kb-clock-judge-qenisv`), and the ruling
- **Judgment: OTHER, which in practice means keep the strict gate with a word-0 precondition.**
  - Opus's prefix anchor is a valid V3 use. Mid-capture stamps constrain only the clock line; latency, a record boundary at the stamp and a blocked sampler change nothing.
  - Its end check certifies nothing. A 55 ms interior misplacement passed it with a 6 ms reading (S7), and its resolution is about 5 ms. A check that does certify is the whole-capture V3 arithmetic again.
  - Sol's latency objection does not apply to that anchor. Sol is right that the joint whole-capture β is what certifies `elapsed_ns` ≡ RAW (to about 0.1 ppm over 4629.6 s).
- **What both seats missed:** the 2.718 ppm on the three 10-11 arms is the kernel frequency-correction word at that time, not oscillator physics. Block 6's M3 measurement (2026-10-17, word 0.0 ppm, boot `ea2d3ec8`) found r = −4.67e-7 ppm over 51,514 s. At word 0 the pinned code works as written: the V3 anchor resolves over 4629.6 s, and the strict gate passes (3.7 + (4.67e-7 + 0.25) × 4.6296 = 4.857 ms ≤ 5 ms).
- **Lead check, executed now:** `kernel_clock.read_kernel_frequency()` gives `raw_word 0`, `ppm 0.0`, `call_status 5`. `kern.bootsessionuuid` is `EA2D3EC8-…`, the M3 boot and the boot every BYTES session ran on.
- **Ruling (lead):**
  - The judge's primary is adopted. `t_stream_max_s` stays 4629.6 s (the threshold's own definition, the longest sampler stream), with h 3.7 ms, 0.25 ppm and 5 ms unchanged. No code change.
  - Preconditions for the KB night:
    - (1) the kernel frequency word is 0 at arm, read and recorded by the lead before prepare;
    - (2) the arm's measured |r| ≤ 0.0308 ppm is the hold, as coded;
    - (3) the capture's V3 anchor must come back bounded, or rails and GPU are null, as coded.
  - At a hold the remedy is the registered redraw of the word (block-6 S-7), not a retry.
  - Replay under doctrine rule 9: the three 10-11 arms are held (3 of 3), correctly for their word. The M3 state passes. The replay is not of known-good sessions under this test, because none exists at a nonzero word that this code could use.
  - Recorded as the path not taken, for a nonzero word: the judge's §4 RAW-consumer anchor identity (V3 arithmetic with the 5 ms cap on placement only, a pairing term, the capture bound joined into the operative bound, a new method identity). Build it only if a night is ever held by the word.
- PR #613 CI: shard 5 failed on `tests.test_bytes_stream_capture` `test_prepare_authors_isolated_night_plan_without_default_ledger`. The fixture's `git commit` had no identity on CI (exit 128). Fixed by the lead on the branch (`e91946490`), test-only, using the pattern of `tests/test_repin.py`.

## BY-THERM-LINES round 6 (Sol high, `01a18e99-bc3d-7399-aa7b-87c932b5c000`; head `4e29114ea`). The tool is admitted.
- A1-A5 are implemented. A line that the production reader accepts but the strict lexer rejects now makes the journal untrusted; only lines that both readers reject keep the malformed-skip. Repeated roster ids are a W4 global fault. Export session ids must be safe, and destinations must stay inside the output. Level-conversion failures are contained. The replay notice is emitted only when a replay ran.
- Lead re-execution at `4e29114ea` (log `~/night-archive/seats-4e748ac1/by-therm-fix6/lead/lead-probes-4e29114ea.log`):
  - Opus `probe_journal_divergence.py`: in all four divergence cases, member `a` is `not defined (journal line not producer output)`, nothing is restored, and its codes are kept. The clean case stays equal. The probe's own direct call of `journal_readings` was wrapped, because that function now raises by design.
  - `misc_probes.py`: a duplicate roster id, and a run listed as both science and reference, give `not defined (roster repeated run_id)` with no changes.
  - Sol `session_path.py`: `not defined (unsafe export session_id)`, and the sibling file is preserved. TMPDIR was set to a resolved path, because on macOS `/tmp` resolves to `/private/tmp`.
  - Sol `large_level.py`: exit 0 with a record written. The baseline still raises.
- **Admitted by the lead.** No probe changes which members count. The three reported instances of the class are closed by the consult's rule as implemented. Next: run it on the real pass-1 and pass-2 archives locally (blinded data stays local) before the pass-2 analysis.
