# Harvest off the MBP: Opus build

- **Seat:** Opus 5.5, independent build. A Sol build runs separately on `align/2026-11-08-harvest-off-sol`. Ed's rule (RUN_STATE 220): both build, then agree.
- **Date:** 2026-11-08. **Base:** `origin/align/2026-11-08-v4-r11` @ `05b6d04cb`. **Branch:** `align/2026-11-08-harvest-off-opus`.
- **Scope:** engineering of the between-window loop. No estimand, threshold or exclusion rule changes. One registration-text clarification is proposed for the lead (section 5.3).
- **Data:** synthetic only. No real record, `night-*` or restricted path was read.

## 1. Summary

**What dominates.** The harvest is almost all plist parsing.
- On a synthetic window, `members` (per-member strict validation, re-reduction, anchor recompute) is 97% of harvest wall time.
- Inside it, `plistlib.loads` is 98%.
- Each member's raw powermetrics plists are parsed **18 times**.
- Hashing, cloning, archiving, flags and exclusions together take about 3% of the time.

**The ALIGN desk runs the harvest with one worker.** `align_pilot_session.desk` never passes `--workers`, so `harvest_b6_session.py` assesses members serially.

**Four changes, each proven equal on synthetic data:**
1. **Dedupe.** One member's raw plist is parsed once, not 18 times. A scoped memo keyed on the SHA-256 of the input bytes. Measured 2.6-4.3× on the members step.
2. **Parallel.** `--harvest-workers N` reaches the existing order-preserving pool. Dedupe plus 6 workers: 7.7-10.5× on the members step, 5.3-6.5× on the whole harvest.
3. **Reduce once (section 10).** A targeted extractor, proven equal to `plistlib` on all 1,735 fixture documents, runs 5.4-6.5× faster. It writes digest-bound columnar files about 960× smaller than the XML, at about 1-2 min per window on the Air.
4. **Off the MBP.** A verified, compressed raw copy is restored on the Air at the same absolute path. The Air's harvest output then equals the MBP's byte for byte (with the clock and boot seams pinned). With real clocks, it differs only in five declared provenance fields.

**MBP minutes saved per window:** about **95-102 min**.
- The MBP keeps finalize, a 1-3 min pack/offload, cool-down, pre-arm and dwell.
- The light triage runs on the Air during cool-down.
- **New between-window turnaround: about 33-63 min**, against about 133-163 min today, inside RUN_STATE 213's 30-45 min target at its low end.
- **Exception:** after W1 or a code/config change, the MBP waits for the Air's full desk.
  - Air full desk: about 12-34 min, or 60-75 min if the whole-window desk-verdict child runs (section 3.4, scenario B).
  - Turnaround in that case: 33-63 or 75-115 min.

**Two blockers before first use** (section 6):
- **P1:** the Air has 24 GiB free and needs about 70 GB.
- **P5:** the full desk cannot currently reach PASS, because `v4_B_bar` is always False. Pre-existing; needs a lead ruling.

## 2. Profile (step 1)

### 2.1 Method

- **Harvest under test:** the real `joulewise.b5.harvest.harvest` on `tests/test_harvest_b5_window.Window`:
  - 6 strict real-format members built from the d117 production seed bundle;
  - 10.9 MB of plist per member (main 5.8 MB, idle 2.3 MB, idle_post 2.8 MB);
  - a real ledger, journals, catalog and L4 exclusions;
  - `prepare_desk=True`.
- **Timing:** each `_Harvest.step` was timed; cProfile was used for call counts.
- **Primitives:** plist parse, SHA-256 and zstd were timed separately on a 231 MB real-format plist made of 40 concatenated seed frames.
- **Host:** Air M4 (4P+6E, 24 GB), Python 3.13.18. The host was heavily loaded by other agents (load average 15-47), so absolute numbers are pessimistic. Ratios were measured A/B back to back.
- **Scripts:** in the seat scratchpad, not committed. The committed tests reproduce the equality claims.

### 2.2 Stage breakdown (6-member synthetic window, one worker, cProfile on)

| Step | s | share | per-byte work |
|---|---:|---:|---|
| `members` (assess: strict validate, re-reduce, anchor, battery pair, identity) | 133.4 | 97.4% | 18 plist parses per member |
| `calibration` | 1.4 | 1.0% | brackets; small |
| `monitor` (hazard journal joins) | 0.6 | 0.4% | journals |
| `archive` (clone + 2 inventories per source) | 0.4 | 0.3% | SHA-256 + `cp -c` |
| `sources_unchanged` (re-inventory) | 0.2 | 0.1% | SHA-256 |
| everything else (25 steps: roster, flags, identity, lineage, meter, NEG-8, g10, exclusions, finish) | < 0.2 | < 0.2% | none |
| **total** | **137.0** | | |

Where the 18 parses per member come from (cProfile callers of `_powermetrics_documents`):

| Caller | Parses | cum s / member |
|---|---:|---:|
| `environment_admission._window_thermal_pressure_refusals` | 6 | 15.2 |
| `cli._strict_uncertainty_evidence_problems` | 3 | 5.5 |
| `reduce._derive_anchor_context` | 2 | 6.1 |
| `idle_dependence.derive_idle_mean_uncertainty` | 2 | 2.4 |
| `samples_from_raw_powermetrics` | 1 | 3.8 |
| `harvest.recompute_anchor_status` | 1 | 2.8 |
| `decode_rich_telemetry` | 3 | 7.1 |

### 2.3 Primitives (Air, loaded)

| Primitive | Measured | Real-window implication (18.6-26.4 GB, about 89% plist) |
|---|---|---|
| plist document parse | **10.4 MB/s** single core | one pass over 16.5-23.5 GB of plist = about 26-38 min per core |
| SHA-256 | 1.52 GB/s | 5 tree inventories ≈ 65-90 s total |
| `cp -c` clone (APFS) | ~0 | archive copy is free on the same volume |
| zstd `-3 -T0` | compress 1.7-3.4 GB/s; decompress about 1 GB/s | pack ≈ 0.5-2 min; restore ≈ 0.5-1 min |
| zstd ratio, real plists | 70× (83 MB non-claim rehearsal plist, `docs/design/block6_collection_draft.md:341`); 169-394× on the seed fixtures | 18.6-26.4 GB → about 0.3-0.4 GB on the wire; even at 10× only 2.6 GB |
| resident memory of parsed documents | **about 8× the plist bytes** (231 MB → 1.86 GB peak); memo pickle 0.26× | a 1 GB member plist ≈ 7-8 GB per worker. This is pre-existing, not new |

### 2.4 Wall time without the profiler (A/B, same minutes, two rounds)

| Configuration | members step s | harvest total s |
|---|---:|---:|
| 1 worker, no dedupe (today) | 28.5 / 30.5 | 31.2 / 32.1 |
| 1 worker, dedupe | 6.7 / 11.9 | 8.8 / 14.0 |
| 6 workers, no dedupe | 9.1 / 10.9 | 11.2 / 13.3 |
| 6 workers, dedupe | 2.9 / 3.7 | 4.8 / 6.0 |

The cross-check against the record agrees.
- Measured B6/BYTES harvests: 88-109 min for about 43 GiB sessions.
- The ALIGN desk: 98-103 min for 18.6-26.4 GB windows.
- Both mean the MBP spends about 0.12-0.3 s per MB. That fits about 18 parse passes at 60-150 MB/s of effective parse throughput on an unloaded M-series core, against 10.4 MB/s on this overloaded Air.

### 2.5 MBP-bound versus anywhere (from a verified raw copy)

| Stage | Where | Why |
|---|---|---|
| finalize, hash, commit, push the record | **MBP** | custody of the original bytes (B2) |
| pack: hash every file once plus zstd, ledger appended | **MBP** | reads the original; about 1-3 min |
| `readiness` (terminal record; chain process group gone) | MBP at pack time; repeated on the Air | the Air's `killpg(pgid, 0)` probes an unrelated pid space (P4) |
| desk-verdict child (`run_campaign --whole-window-verdict`) | anywhere | reads and writes only the copied runs root, ledger and pin |
| archive, roster, members, flags, monitor/meter joins, identity, NEG-8, g10, exclusions | **anywhere** | pure functions of the copied bytes, the measurement checkout at the same commit and path, and the seams |
| `harvest_checkout`, `boot_session_uuid`, clock seams | anywhere, but host provenance | declared provenance fields (section 4.2) |
| accept_archive, export (`harvest_b6_session.py`) | anywhere | read the archive |
| desk extraction (episode summaries, thermal desk, km003c) | anywhere | read bundles and custody |
| cool-down, pre-arm, dwell | **MBP** | physics / host state |

Nothing in the harvest needs the MBP's hardware. It needs the same bytes at the same paths, and the same code and interpreter.

## 3. Hand-off design (step 2)

### 3.1 Timeline per window

```
MBP:  terminal ─ finalize/hash/push ─ PACK (1-3 min) ─ cool-down (15-25, physics) ─ pre-arm ─ dwell ─ ARM next
                                         │ offload (pull, ~0.3-2.6 GB)
Air:                                     └─ UNPACK+verify (1-3) ─ LIGHT TRIAGE (3-8) ─► packet before arm
                                                             ├─ REDUCE once (1-2 min, section 10)
                                                             └─ FULL DESK: harvest + desk (12-34 min*) ─ FINAL rows
                                                                (in parallel with the next window, unless B2 requires it before the arm)
```
\* 60-75 min in scenario B (section 3.4).

### 3.2 MBP

1. **Finalize** as today. Unchanged.
2. **`scripts/align_v4_harvest_off.py pack --session-root S --out O`**
   - It refuses unless `custody/night/result.json` exists.
   - It walks the session root without following links. Each regular file is read once, hashed with SHA-256 and streamed into `payload.tar.zst` with its mode. Symlinks are kept literally (the measurement view's absolute links). Any other file type refuses.
   - The plan's calibration ledger (outside the session, appended by the window) travels as an append-only external file.
   - `MANIFEST.json` records the absolute source root, every entry, and the payload digest.
   - `IDENTITY.json` records the measurement checkout. It uses the same git probes as `harvest.harvest_checkout`, plus the `.venv` interpreter version and a digest of its installed package set.
3. **Cool-down, pre-arm, dwell.** The pack runs before the quiet clock. Whether it lengthens cool-down measurably is native item N6.

The light triage could run on the MBP as a fallback: the same command on the original session root takes about 2-8 min of MBP CPU. Running it on the Air is better, for two reasons:
- the registration text already says checks "that summarize the previous window are computed off the MBP from the committed record";
- `quiet_start_state` forbids desk traffic on the MBP.

### 3.3 Air

1. **`unpack --offload O`** works in this order:
   - It refuses unless the Air's measurement-checkout mirror (same absolute path) has the same head, a clean status including untracked files, and the same interpreter and package digest.
   - It checks the payload digest.
   - It extracts into `<root>.restoring`, writing files exclusively (an existing file refuses) and verifying every entry against the manifest. Any missing, extra or changed entry refuses and removes the staging directory.
   - The ledger is placed only if it is absent, identical, or a byte-prefix extension of the current copy.
   - Finally it renames the staging directory to **the recorded absolute root**. A different path refuses, because absolute paths are embedded in harvest output.
2. **`triage --session-root S --window-id W`** (light, section 5). It prints `thermal_escalation`, provisional `member_eligibility` and a provisional `calibration_stop` row. The packet is built from this.
3. **`desk --session-root S --workers N`** runs the **unchanged** v4 desk (`align_v4_session.py desk --harvest-workers N`): harvest, acceptance, export and the full desk. The wall time is recorded outside the session. N is 2-3 on the 24 GB Air (memory: section 2.3). Measure before using 3.
4. **`final --session-root S --window-id W`** reads the full desk's `PILOT.json` and `desk.json`. It refuses unless the harvest completed. It prints the **final** eligibility and calibration row, plus `PILOT.json`'s SHA-256 for the packet basis.

### 3.4 How the B2 and B3 rules stay intact

- **The B2 full-desk rule is unchanged.** `next_arm_triage` still refuses `full_desk_gate: deferred` when the previous window is W1 or any code or config changed. In those cases the arm waits for the Air's `desk` and `final`. The packet basis cites the `PILOT.json` SHA-256 printed by `final`.
  - This also closes the eng-desk review's M1.1 gap, provided the triage tooling requires that digest. That enforcement is not built here; it is recommended.
- **Exclusions are final before B3 counts are used.** Rows from `triage` carry `status: provisional`. Only `final` writes `status: final`. `calibration_stop` already returns `pending_final_eligibility` at 8 counted windows while any row is provisional, so no count is used before the Air's harvest has finalized it.
  - Before 8 windows, the decision reads only how many windows were counted, from `captured_members`. That is identical in light and full (proved in section 5).
- **A desk-only finding** on the window already running costs at most that window, as the registration text already accepts.
- **Scenario B (to confirm natively, N1).**
  - If the ALIGN harvest's desk-verdict child actually runs (whole-window verdict absent and the head pin advanced), it strict-validates every bundle serially without dedupe. The source comment says 34.5 s per bundle on block 5.
  - It runs concurrently with `members_early`. After this speed-up it becomes the harvest's critical path: about 0.65 of today's member time.
  - The fix is follow-up F1: open `document_memo()` around each bundle in that child. It is not built here.
  - If `withheld/desk-verdict-run.json` is absent from ALIGN archives (a structure-only probe), scenario A holds.

## 4. Byte identity: MBP versus Air (step 2, required proof)

### 4.1 Claim and proof

**Claim:** given the same bytes at the same absolute paths, the same measurement checkout and the same interpreter, the Air harvest's archive is byte-identical to the MBP's. This holds with or without dedupe and at any worker count.

**Proof:** `tests/align/test_harvest_off.py::SamePathHarvestEqualityTests::test_air_harvest_from_verified_copy_is_byte_identical`.
- The window is packed before harvest.
- **"MBP":** today's path, one worker, dedupe disabled, on the live tree.
- The tree is moved away and the offload restored at the same path.
- **"Air":** 3 workers, dedupe on.
- **Result:** the same `harvest.json` record and the same SHA-256 for every one of the archive's 177 files (file set included).
- **Mutation check:** altering one pooled member result makes the test fail.

### 4.2 Provenance

With unpinned clocks and different boot sessions (`test_unpinned_runs_differ_only_in_declared_provenance`), exactly three files differ:
- `derived/flags.jsonl`: `emitted` only;
- `derived/window_flags.json`: `window.boot_session_uuid`;
- `harvest.json`: the digests of those two files.

`harvest_offload.PROVENANCE_FIELDS` declares these, plus two that appear only when a collector errors or the desk-verdict child runs: `elapsed_s`, `heartbeats`. `archive_projection()` removes exactly those fields, and the projected archives are equal. Use this same function for the native confirmation (N2). Flag ids, exclusions, numbers and verdicts never differ.

### 4.3 Wall-time-dependent decisions

There is one, and only on the Air: the desk-verdict child's budget, max(1,800 s, 90 s per bundle). A loaded Air could time it out and emit `whole_window.producer_failed` where the MBP would not. So:
- run the Air harvest with the Air otherwise quiet (no Sol seats; renice others);
- treat `timed_out: true` as a re-run, not a result.

## 5. Light triage (step 2)

### 5.1 What it computes

It computes exactly the full desk's thermal section, without the harvest.

`powermode_desk_check` builds a thermal record per plan member from the bundle bytes. Its only harvest input is the step now named `light_triage.apply_harvest_codes`, moved verbatim:
- `battery.member_span` codes append a flag;
- `excluded = bool(codes) or bool(calibration_exclusions)`.

The light triage calls the same `powermode_desk_check` with `members=[]`, so no codes are applied. It then reads:

- **`thermal_escalation`:**
  - per model/window U1, U2 and U3 from the same `window_report`;
  - `escalation_required` if any of them fails;
  - the same `v4_<model>_U<n>` booleans the desk adds to its checks;
  - status `pass` unless a U1-U3 failed and the registered ladder step is not yet recorded.
- **`member_eligibility`:**
  - per plan member: captured (bundle present), eligible, and reasons;
  - eligible means captured and no calibration exclusions (X1-X4, deadman, malformed tool calls, runtime failure, energy evidence);
  - the full desk additionally removes harvest-excluded members;
  - X5 and U3 pair verdicts come from the same `window_report`;
  - status `pass` when every plan member is classified.
- **`calibration_row`:** the fixed-8 row (`status: provisional`, `captured_members`, `eligible_benign` per pair). The calibrator predicate defaults to role D, benign, spam or bank, and is injectable for the D series manifest.

No score, alarm or residual enters any of these.

### 5.2 Proof that it matches the full desk (`LightTriageTests`, 40 seeded synthetic windows)

Each window has 22 members with random X1-X4 flags, energy-evidence loss, an X5 token mismatch, and random harvest codes including `battery.member_span`.
- **U1-U3 are identical**, every field, with and without `apply_harvest_codes`. So `thermal_escalation` and the U checks are identical.
  - The reason: `window_report` reads `excluded` only in the contrast (`deciding_experiment`), and `battery.member_span` only in the B printout. Neither enters U1-U3.
- **Eligibility.** Full eligible ⊆ provisional eligible, and some seed produces a strict subset. `status` and `captured_members` are identical. With no harvest exclusions, the eligible sets are equal.
- **`calibration_stop`.** It gives the same decision and count from provisional or final rows for 1-7 windows. With 8 windows and one provisional row, it returns `pending_final_eligibility`.
- **Production wiring.** `powermode_desk_check` routes its harvest step and its U checks through `light_triage`, so the proof covers production code.

### 5.3 Ruling needed: what `member_eligibility` means at the arm

The frozen triage text says `member_eligibility` is the "final eligibility adjudication" and gates every arm. B3 says "counts are provisional until it passes; provisional counts schedule windows 1-7". Read literally, the two together require the harvest before every arm, and then nothing can be provisional.

**Proposed clarification (v4 not yet registered; the lead owns it):** at the arm, `member_eligibility` passes on the **provisional** adjudication, meaning every member is classified with X5, U3 pairs and calibration exclusions. The harvest's exclusions finalize the counts off the MBP, and `calibration_stop` refuses at 8 until then.

This is sound for two reasons:
- under fixed 8, no roster or plan for windows 2-8 depends on the counts;
- the harvest can only remove eligibility.

Also resolve the conflict with RUN_STATE 216, which says "from window 6 on, final eligibility pending blocks the next arm". That was written for the count stop that 217 replaced. Under fixed 8, only the arm after C8 needs final counts.

## 6. Preconditions and risks

- **P1 Air disk (BLOCKER).**
  - The Air has 24 GiB free.
  - A restored window is 18.6-26.4 GB plain. The APFS clone in the archive is free. Add the offload, harvest outputs, and the 40 G disk-guard margin: the Air needs about 70 GB free.
  - Keep one restored window at a time. Delete it after `final` passes, once the MBP original and its second custody copy are in place.
- **P2 Air measurement mirror.**
  - The MBP measurement checkout must exist on the Air at the same absolute path and the same head, clean including untracked files, with a `.venv` of the same Python and package set (`unpack` checks all of this).
  - The session root is restored at its MBP path. If that is under `/Users/edr`, this is a deliberate, pruned exception to keep-home-clean.
- **P3 Air quiet during the harvest** (section 4.3). Batching: n/a. No harvest, desk, offload or triage stage runs model inference.
- **P4 pgid collision.** `readiness` probes the MBP chain's pgid with `killpg` on the Air. A collision (about 1% at 1k processes) refuses with `NotReady` (exit 3), never wrong bytes. Re-run.
- **P5 The full desk cannot PASS today (pre-existing, not introduced here).**
  - `powermode_desk_check` sets `v4_B_bar = all(w['bar_pass'] ...)`, and `desk_diagnostics` sets every `bar_pass` to `None` ("PENDING lead window consequence"). So `pilot_status` is always `instrument_incomplete` and the desk exits 2.
  - `full_desk_gate: pass` therefore cannot be earned. That blocks the arm after W1 under B2. The lead must rule (for example, `v4_B_bar` reported but not gating until its bar is set).
  - Also pre-existing on the base: `tests.align.test_v4_powermode_record` fails `test_desk_check_passes_only_when_every_bundle_matches` (`v4_registration_evidence: False`), identically before and after this branch.
- **Memory.** About 8× the plist bytes per worker (pre-existing). Use 2 workers on the Air, or 3 after measuring peak RSS (N4).
- **Cache rule (toolbox §6).**
  - The dedupe keeps parsed plist content, not a decision. A refusal is never kept: each call re-parses and raises its own error (tested).
  - It is keyed by the SHA-256 of the exact bytes, scoped to one member's assessment in one process, and returns fresh unpickled objects, so callers never share state (tested).
  - The scope is shorter than the process, so the key trivially covers the code as loaded.
  - This goes beyond "content digests at most". Measured win: 2.6-4.3×; members-step equality tested. The lead may drop it and keep only the workers (about 2.2-3.3× instead of 7.7-10.5×).
- **Registration closure.** `light_triage.py` is now in the desk's executed closure and the receipt template. Every changed file is in the v4 closure. Landing this is a **code change**, so the full desk must pass before the next arm after it lands.

## 7. Speed-ups implemented (step 3)

| Change | Files | Equality evidence |
|---|---|---|
| Scoped parse dedupe | `joulewise/adapters/powermetrics.py` (`document_memo`, off by default), `joulewise/b5/harvest.py` (`assess_member` opens it) | memo tests; member assessment equal field for field plus re-reduced bytes, clean and damaged; whole-archive equality |
| Member pool reaches the ALIGN harvest | `scripts/align_pilot_session.py` (`harvest_workers`, `--harvest-workers`; absent keeps the recorded argv) | `DeskWorkersTests`; whole-archive equality at 3 workers |
| Verified offload and same-path restore | `joulewise/align/apple/harvest_offload.py`, `scripts/align_v4_harvest_off.py` | `OffloadTests`, `RunnerTests` (round trip; relocation, tamper, manifest, ledger, mirror and file-type refusals) |
| Light triage, shared with the desk | `joulewise/align/apple/light_triage.py`, `scripts/align_v4_session.py` | `LightTriageTests` |

**Gap:** the `triage`, `final` and `desk` subcommands are thin glue over tested parts (`powermode_desk_check`, `light_triage`, the desk CLI). They have not been run end to end on a synthetic v4 kit session. Their first run is part of N7.

**Not built (follow-ups):**
- **F1:** dedupe inside the desk-verdict child (scenario B).
- **F2:** streaming the document parse to cut the 8× memory, which allows more Air workers.
- **F3:** dedupe in the desk's own extraction (eng-desk scope).
- **F4:** fold the 4-5 tree inventories into one (about 1-1.5 min on a real window).

## 8. Minutes saved and turnaround (step 4)

| Quantity | Today | Harvest off (this design) | Basis |
|---|---:|---:|---|
| MBP desk/harvest per window | 98-103 min | **pack 1-3 min** (+2-8 min if the triage falls back to the MBP) | measured desk; pack from section 2.3 |
| **MBP minutes saved per window** | | **95-102** (90-100 with MBP triage) | |
| Air full desk (harvest + desk), scenario A | n/a | 12-34 min: members 7-16 + desk remainder 4-15 + unpack 1-3 | 85-90 min serial ÷ (dedupe 2.6-4.3 × workers 2-2.8) |
| Air full desk, scenario B (child runs, no F1) | n/a | 60-75 min | child ≈ 0.65 × today's member time |
| Between-window turnaround, desk deferred | ≈ 133-163 min | **33-63 min** | finalize 5-20 + pack 1-3 + max(cool-down 15-25, Air triage 7-15) + pre-arm 2-5 + dwell 10 |
| Turnaround when B2 requires the full desk first (after W1, code/config change) | ≈ 133-163 min | 33-63 (A) / 75-115 (B) min | the MBP waits on the Air, but no longer computes |

All new figures are estimates from synthetic ratios and recorded totals. None is a native measurement.

**To measure natively before relying on them:**
- **N1:** step timings of one real ALIGN harvest, and whether `withheld/desk-verdict-run.json` exists, with its `elapsed_s` and `timed_out`. This settles scenario A or B.
- **N2:** one real window harvested on both the MBP and the Air. `archive_projection` must be equal.
- **N3:** the real compression ratio and pack wall time (the pack prints bytes, payload bytes and elapsed).
- **N4:** Air peak RSS per worker on real member sizes (`/usr/bin/time -l`), to choose 2 or 3 workers.
- **N5:** Air desk wall at 1/2/3 workers, with the Air quiet.
- **N6:** cool-down length with and without the pack at its start (window_timing receipts).
- **N7:** light-triage wall time on the Air.
- **N8:** the transfer path and rate (Thunderbolt bridge, Wi-Fi or SSD).

## 10. Reduce once (Ed's directive, 2026-11-08)

**Directive.** Windows should give outputs that are easier to analyze. The harvest on the Air reduces each member once:
- the raw powermetrics XML becomes a compact columnar per-sample file plus a per-turn energy table;
- every reduced file is digest-bound to its raw plist, and the raw plist stays the custody evidence;
- the extractor is a targeted fast one, proven equal to `plistlib`, run in parallel across members;
- the in-window instrument does not change (only boundary markers are allowed, per SPEED-TOOLBOX).

### 10.1 Built: targeted extractor and columnar samples (`joulewise/align/apple/pm_reduce.py`)

**The extractor.**
- About 87% of every powermetrics document is the per-CPU `processor.clusters` subtree. In the seed, that is 66.9 KB of 77 KB, and no energy or thermal consumer reads it.
- `strip_clusters` cuts exactly that subtree out of the document bytes, by `<array>` depth matching, and passes the rest to **`plistlib` itself**. So every retained value comes from the registered parser's own semantics: dates, reals, integers, booleans and strings.
- A document is cut only when `<key>clusters</key>` occurs exactly once and a balanced array follows it. Otherwise the whole document is parsed.
- At run time, `verify_every=64` re-parses the first document, the last, and every 64th in full and **refuses** on any difference.

**The columns.** One row per sample, written as NumPy `.npy` v1.0 by the standard library alone. Columns:
- `elapsed_ns`, `plist_timestamp_s`;
- `cpu_w`, `gpu_w`, `ane_w`;
- `cpu_mj`, `gpu_mj`, `ane_mj`;
- `thermal` (a code);
- `gpu_active_mhz` (diagnostic only; see the gaps below).

The header binds the raw SHA-256, the raw size and the extractor version. About 80 B per sample against about 77 KB of XML: **about 960× smaller**.

**Where it runs.** `scripts/align_v4_harvest_off.py reduce --session-root S --out R --workers N` runs on the Air after `unpack`. It is order-preserving and parallel across members. It writes a **sibling** directory, never into the harvest archive, so the archive byte-identity proof in section 4 is untouched. It also writes `MANIFEST.json` with every raw and reduced digest.

**Proven** (`tests/align/test_harvest_off.py::PmReduceTests`, 5 tests, failing first):
- **Extractor equals plistlib.** It equals `plistlib` minus `clusters` on **every one of 1,735 documents** in all seven powermetrics fixtures in the repo: production seed main/idle/idle_post, d078, g2b 1,577 frames, replay and sample.
- **Columns equal the registered parser.** Every column equals `parse_powermetrics_records`' fields bit for bit: elapsed, plist timestamp, rails in W, rail energies in mJ, thermal pressure.
- **Edge cases.** Awkward documents (escaped strings, a self-closing clusters array) fall back to the whole parse and stay equal.
- **Refusal.** A fast path that would differ refuses at the verified document.
- **Pool.** The member pool equals serial byte for byte.

**Measured speed** (Air at load about 7-9, 116 MB real-format stream):

| Path | Throughput | vs plistlib |
|---|---:|---:|
| plistlib | 20.2 MB/s | 1.0× |
| fast extractor | 130.4 MB/s | 6.5× |
| fast extractor plus verify-64 plus columns | about 108 MB/s | 5.4× |

**Gaps (not yet built):**
- `gpu_active_mhz` follows `native_pm_samples`' formula but is not yet proven equal to its rich-telemetry path. Treat it as diagnostic until it is.
- Monotonic time is not in the file. The mapping to the episode clock stays with the registered episode code (`clock_mappings`), as in 10.2.
- `fast_documents` holds one stream's reduced documents in memory, about 1 GB per GB of plist. Make it streaming before using 3 or more workers.

### 10.2 Specified, not built: the per-turn energy table

The per-turn table must not be a new integral.
- It is the output of the **registered** per-member code, run once on the Air: `read_bundle_record` → `member_record`, with turn-owned and gross energy, half-widths, decode clocks and turn observations. The boundaries are the existing turn stamps; no window-side change is needed.
- It is stored per member with the SHA-256 of every input: `power_trace.csv`, `outputs/align_episode.json`, `outputs/align_turns.jsonl`, `rich_telemetry.jsonl`, the raw plist, and the reduced `.npy`.
- **Equality gate before any analysis reads it:** the table equals the full desk's `PILOT.json` per-turn values for every member of a synthetic window, bit for bit. That is the same code on the same inputs, under the D-188 result-equivalence rule.

### 10.3 Blinding

The sample columns and the per-turn table carry energy, which is outcome-bearing. They live under the same restriction as `withheld/`, and only the blinded engine reads them. The `MANIFEST.json` digests and row counts are structure-only.

### 10.4 Estimates

**Reduction time per window on the Air:**
- Plist bytes per window: 16.5-23.5 GB (89% of 18.6-26.4 GB). With Ed's 507 MB per member, 22 members' main streams come to about 11 GB.
- At about 108 MB/s per core: **2.5-3.6 min on one core, about 1.3-1.8 min with 2 workers, about 0.9-1.3 min with 3**.
- It fits inside the Air timeline after `unpack` and in parallel with `triage`.

**Analysis speedup when the engine reads only reduced artifacts:**
- **Per window:** about 17-25 MB of columns plus the per-turn tables. A raw pass is 16.5-23.5 GB through `plistlib`, about 5-20 min per window per pass at 20-60 MB/s. Reading the columns takes well under 1 s. The **I/O and parse step is about 300-1,000× faster**.
- **Desk:** the 10-15 min non-harvest remainder (mostly `episode_summary` and the thermal desk's `native_pm_samples` re-reading plists) falls to an estimated 1-2 min, about 5-10×, once it reads the reduced files.
- **Multi-window engine** (8 calibration plus 3-6 test windows): today each analysis pass re-reads about 11-14 windows of XML, 1-4.5 h. Reduced, it is seconds per pass, so the engine is bound by its own arithmetic.
- **Harvest-only effect** (the harvest's own 18 parses): about another 5-6× on top of the memo. This needs F5 (below) and its own equality proof.

None of these is native. Add **N9:** reduce one real window on the Air; check wall time, RSS and reduced-to-raw ratio, plus the per-turn table's equality to that window's `PILOT.json`.

**F5 (follow-up):** route the harvest's own document parse through the cut-and-`plistlib` path wherever its callers do not read `clusters`. Per caller, prove equality of the whole assessment, as in section 4.

**Not applicable:** batching (no inference). No reduced value is cached as a decision: each reduced file is recomputed from bytes it is bound to by digest.

## 9. Test commands (one module per process)

```
python3.13 -B -m unittest tests.align.test_harvest_off          # 24 OK (failing-first: 17 errored on 05b6d04cb; the 5 PmReduceTests errored before pm_reduce existed)
python3.13 -B -m unittest tests.align.test_v4_executed_closure  # 2 OK
python3.13 -B -m unittest tests.align.test_v4_registration      # 20 OK
python3.13 -B -m unittest tests.align.test_v4_kit               # 116 OK
python3.13 -B -m unittest tests.align.test_v4_cadence           # 16 OK
python3.13 -B -m unittest tests.align.test_thermal_desk         # 25 OK
python3.13 -B -m unittest tests.align.test_pilot3               # 7 OK (1 skipped)
python3.13 -B -m unittest tests.test_powermetrics               # 61 OK
python3.13 -B -m unittest tests.test_adapters_powermetrics      # 3 OK
python3.13 -B -m unittest tests.test_audit_powermetrics_parser  # 4 OK
python3.13 -B -m unittest tests.b6.test_session_wrapper         # 6 OK
python3.13 -B -m unittest tests.test_harvest_b5_window          # STOPPED at 115/187, all passing (see note)
python3.13 -B -m unittest tests.test_desk_compressed_readers    # 9 OK
python3.13 -B -m unittest tests.align.test_v4_powermode_record  # 8 OK, 1 FAIL pre-existing on base (P5)
```

**Note on `tests.test_harvest_b5_window`.**
- On this Air, the run reached 115 of 187 tests, all passing. It then blocked reading `~/Library/Mobile Documents/.../JouleWise-backup/window_c_20260726/.../raw/powermetrics.plist`, a **real** iCloud backup capture.
- The cause appears to be the fixture's historical ledger prefix, whose custody locators point at real paths. The harvest's historical-custody step follows any locator that exists on the host. This is pre-existing and not caused by this branch.
- I stopped the run rather than read real data.
- Run the module in CI or on a host without that path.
- **Recommended fix:** the fixture should rebase the prefix's locators into the temporary tree, or the test should stub `historical_custody`.

