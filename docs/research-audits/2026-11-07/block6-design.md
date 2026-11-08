# Block 6 design and registration audit: synthesis of two seats

**Date:** 2026-11-07. **Synthesis:** Opus 5.5. It reconciles two independent seats that worked from the same brief:

- **Seat 1:** Fable 5.1 (high). Its durable copy is `docs/research-audits/2026-11-07/block6-design/fable-seat.md` on
  `origin/research/2026-11-07-block6-design-fable` (`b9019c48b`). Its return adds one F4 refinement after that push.
- **Seat 2:** Opus 5.5 (xhigh). It committed nothing.

Both reports are reproduced verbatim in the appendices.

**Basis.**
- I read `origin/main` at `bd7a3efcd`. The seats read `ca2d1ee97`. The only difference between the two is 24 lines
  added to `RUN_STATE.md` after its line 1044 (item 202), so every REG, DLE, LEAN, TRACE, script and test citation
  is unchanged.
- I read the lanes at these commits:
  - block-6 collection: `lane/2026-10-17-b6-packs-registered` `1706257c4`, pin `f31aca19f`, tag `b6/collection`;
  - DESIGN: PR #537 `578685ec3`, plus PR #572 `bb9669b69` on top of it. Both are open; I cite `bb9669b69`;
  - S-9/S-11 fill: PR #529 `c37614f71`;
  - B6-AN-1 driver: `lane/2026-10-27-b6-analysis` `10b2b679c`;
  - RC-B6-1 lean block-6 recompute: `lane/2026-10-27-recompute-b6` `74a4f8123`;
  - the local-only r4 lane: `lane/2026-11-07-b5-analysis-r4` `7db6fb9a3`, in the canonical clone.

**Blinding.**
- I opened no `/Users/edr/jw-b5-*`, `night-*`, custody, archive or `restricted/` path.
- I read and inferred no block-5 or block-6 energy, interval, contrast, outcome word or verdict.
- Every number below is a design constant, a code constant, a count, a line number or a wall-time estimate.

**What I ran.**
- Static reads of code and documents at the commits named, plus `git` and `gh` queries.
- One synthetic probe: I loaded the `s13_block6` bar set through `scripts/compare_b5_recompute.py` and fed it one
  meter row. It ran under python3.13, `nice -n 19 taskpolicy -b`, `JW_B5_SYNTHETIC_ONLY=1`, with TMPDIR
  `/private/tmp/jwburn-b6synth`.
- I touched no real data, loaded no model weights and did nothing on the measurement Mac.

**Aliases** (as in the seats):

| Alias | File |
|---|---|
| REG | `docs/registrations/block6_replication_DRAFT.md` |
| DLE | `docs/analysis/b5/DEVIATION-LOG.md` |
| LEAN | `docs/analysis/b5/LEAN-COVERAGE-AUDIT.md` |
| TRACE | `docs/run_reports/2026-11-07-b5-release-hold-trace.md` |
| RESUME | `docs/handoff/2026-11-07-account-retirement/RESUME.md` |
| DESIGN | `docs/design/b6_analysis_additions.md` at `bb9669b69` |
| RC-B6-1 | `scripts/independent_recompute_b6.py` at `74a4f8123`; its report is `.codex-report/RC-B6-1.md` there |
| B6-AN-1 | `.codex-report/B6-AN-1.md` at `10b2b679c` |
| I | `scripts/independent_recompute_b5.py` |
| C | `scripts/compare_b5_recompute.py` |

Citations take the form `path:line`, at `bd7a3efcd` unless another commit is named.

---

## Executive summary

**Block 6 has already been measured.** Nine sessions, all of them counting, closed on 2026-10-21 and are sealed and
unanalysed (`RUN_STATE.md:203-207`). Both seats caught this. So amendments "before any Block 6 data exists" are no
longer possible. What remains is blind REG §17 entries under §12.4 (REG:1168-1173). Both seats advise landing them
**before the block-5 unseal**.

The seats agree on the verdict, and each load-bearing claim held up when I checked it:

1. **No registered, runnable block-6 analysis path exists.** Three candidates exist, and none is merged:
   - L9 plus a binding seam, per DESIGN and B6-AN-1. B6-AN-1 runs only against a fake L9 adapter.
   - The lean block-5 script that DLE-2 and `CANONICAL.md:48` name as the production program. It has no block-6 mode.
   - RC-B6-1, the only real block-6 implementation. It is not in `CANONICAL.md`.

   REG §17 has had no entry since 2026-10-17. The §17 entry DLE-2 says is owed, and a DLE-1 counterpart, do not exist.
2. **S-13 is not operational.** Three printed-precision tables disagree, and their bars differ by up to 100×. The lead
   ratified one of them on 2026-10-27, but it was never registered.
3. **The D5 cause fix is still local only.** The r4 lane is at `7db6fb9a3`, with no origin branch and no tag. Block 6's
   runner writes the same campaign-log record types as block 5's, so the fix applies to block 6. Two dangers remain:
   - L9 reads a compressed campaign log as empty;
   - a floor-binding refusal still "completes" the dry run, with exit 3.
4. **The comparator does not cover every registered family.** It checks what the lean program computes. The seven
   DLE-2 families, both whole-machine lines (4 of block 5's 6 release defects were in the request-level one),
   §9.5 item 7, E_add and the P* exclusion have no producer on any candidate production path.
5. **Every raw plist is `.zst`.** Both lean programs stop on compressed files (`trace_plist_missing`), and `main` has no
   way to read them.

**Speed.**
- The lean path takes roughly 20-40 min for block 6 once it uses the member pool. RC-B6-1 is serial today, at an
  estimated 1.4-3.7 h.
- The heavy L9 audit as designed takes about 16-25 h. That drops to about 3-5 h with floor-session reuse, no repeats
  and units run in parallel.
- So block 5 r3's 1 h 40 min is achievable on the lean path only.

**What follows.** Section 3 lists twelve registration amendments (R1-R12) and section 4 eight code preconditions. Eleven
decisions are needed from the lead. Decisions 1 and 2 gate most of the rest.

---

## 1. Decisions needed from the lead

1. **Production architecture.** This gates R1, R3, R4, R11 and R12. The options:
   - **(a) REG §13 as written.** L9 with an `AnalysisBlock` seam plus the B6-AN-1 driver prints the numbers; the lean
     program checks them.
   - **(b) DLE-2 literally.** The lean program prints, and the heavy L9 pipeline audits once. This still needs the seam.
   - **(c) Seat 2's proportionate path.**
     - RC-B6-1 prints, with the member pool added and the block-5 script's digest pinned.
     - The second side for the block-6 layer is three pieces: the twins already on `main`, a small stdlib checker for
       counting, pairing and §10-§11, and the reducer cross-check promoted to a gate. The twins are
       `joulewise/twins/harvest_twin.py` (REG §1.7-1.8) and `joulewise/twins/engine_twin.py` (REG §9.4). The
       reducer cross-check is `stored_energy_mismatch`, I:479.
     - The L9 audit becomes optional, recorded as a §17 deviation.

   **Synthesis recommendation: (c), with C3 mandatory.** C3 re-derives exclusions under the block-6 catalog.
   - (c) is the only option whose parts exist today.
   - C3 keeps one independent re-derivation of the collection-time judgments. Without it, DLE-2's own open review
     point applies: the audit run would be "the only check of those judgments" (DLE:184-188).
   - Options (a) and (b) both need the L9 seam: binding sites across `whole_window.py`, `floor_extraction.py`,
     `floor_mint_estimator.py`, `b5_analysis/context.py`, `bracket.py`, the mint script and `disclosures.py`
     (DESIGN §4.2, :312-360). They also need an equivalence replay that takes hours.
2. **S-13 printed precision.** This gates R2. Pick one table and one comparator code path.

   **Recommendation: keep S-13's rule and register the parameter it lacks.** Use the strictest value per family across
   the three tables:

   | Family | Decimals |
   |---|---|
   | J | 5 |
   | ratios (R, R_cm, the factor, the energy ratio) | 4 |
   | per-token | 8 |
   | t | 3 |
   | p | 4 |
   | b_op (s) | 6 |
   | counts and words | exact, with the FS3 rule |
   | run phase energy | 1 mJ (unchanged) |

   - This supersedes lead decision 1 of 2026-10-27. RC-B6-1.md:147-152 says Ed may override that decision before the
     release.
   - Seat 1's option (a), adopting block 5's coded 1e-6 relative bars, does not satisfy S-13's wording. Above about
     5 J they are looser than a 5-decimal half-unit: 26 J × 1e-6 = 2.6e-5 J, against 5e-6 J.
   - The strictest table is still far above float noise. DESIGN :962-980 derives 2.2e-7 J at 1,000 J.
3. **Amendment deadline.** REG §12.4 allows §17 entries while block 6 is blinded, that is, up to the block-6 release.
   Both seats prefer a deadline before the block-5 unseal, and seat 1 would register "no amendments after". After the
   unseal the signer has seen block-5 outcomes, so a blind statement is no longer credible.
   **Recommendation:** land R1-R12 before the block-5 unseal. After it, allow only entries that fix a tooling defect
   and choose no rule, labelled as such.
4. **The D5 r4 lane.**
   - Push `lane/2026-11-07-b5-analysis-r4` (`7db6fb9a3`, local only), review it and tag `b5/analysis-r4`.
   - Any L9 use for block 6 must be based at or after that tag.
   - The fix's two-mode rule needs a block-6-shaped fixture (R12).
5. **If the audit has not finished at release.** Either hold (seat 2), or release labelled provisional (seat 1 offers
   both; DLE:189-191). **Recommendation: hold.** It is simpler, and it removes the provisional-labelling surface.
6. **Coverage, family by family.** This applies to the seven DLE-2 families, the request-level and per-phase
   whole-machine lines, and §9.5 item 7. For each, choose one:
   - **(a)** computed by the production program and compared; or
   - **(b)** "copied from the harvest or acceptance record, bound by digest, not recomputed", with the item-83
     ruling-3 hand check.

   **Recommendation:** (b) for count-type disclosures, (a) for both whole-machine lines.
7. **S-15 and §10's whole-machine Q.**
   - Adopt DESIGN §8's meter-only per-phase definition. Label it single-implementation, or name a second producer.
   - Then rule on block 5's side of §10. Either block 5's per-phase value is computed after the block-5 release by
     block-6 code (a new block-5 number), or §10 prints "block 5: not computed".
8. **Estimand wording.** Rule on four items:
   - §9.5 item 3's T: estimator-1 weights (DESIGN) or the plain mean over kept members (RC-B6-1).
   - The E_ref/T_ref basis.
   - The J6 timing-bound sensitivity line: in or out.
   - A §10 label for the block-5/block-6 s_bracket difference.
9. **Host and read path.**
   - The host: this Air has 54 GiB free now, against 32.75-38.82 GiB per session decompressed. The MBP belongs to the
     magistrate.
   - The read path: stdlib `compression.zstd` streaming, `desk_compress.read_bytes` (needs the zstd binary), or an
     APFS in-place restore.
10. **Item 144's L9-ENV-3 mirror deletion.** Hold it until any L9 block-6 audit has run, or until decision 1 retires
    that audit.
11. **One structure-only probe of the nine sessions, counts only.** Both seats ask for one. It should count four
    things:
    - waited runs with attempt-N baselines;
    - wait-cap and budget skips;
    - `member.anchor_not_bounded` members;
    - member phase checks re-run under the registered b_op (10.818 ms) instead of the stored bracket.

    It sizes the D2, D3 and D4 exposure and settles seat 1's open question 3 before any program is promoted.

---

## 2. Findings

**Severity:**
- **BLOCKER:** stops a compliant blind dry run or release.
- **MAJOR:** a wrong or unchecked number is possible.
- **MINOR:** process or durability.

Each finding says where the seats stand, then what I checked.

### F1. BLOCKER: no registered, runnable production path

- **What the registration says.**
  - REG §13 (:1175-1188) and S-14 (:1207): "block 5's L9 release tag plus the block-6 additions".
  - REG §12.3 item 4 (:1154-1155) needs an "analysis program" and an "independent recompute".
  - REG §1.10 (:274-275) defines the recompute as a check.
  - REG §13 (:1186-1188) requires a release re-run in which "every output digest must equal the dry run's".
- **What DLE-2 says.**
  - DLE-2 (DLE:140-197) makes the lean recompute the production path for block 6. It names
    `scripts/independent_recompute_b5.py` "with its member pool".
  - `CANONICAL.md:48` says the same.
  - DLE-2 says the block-6 §17 entry "is owed" (DLE:167-168).
  - DLE-1 replaced the release re-run with digest re-verification, for block 5 only (DLE:71-137).
  - A lead ruling of 2026-10-27 asked for "a separate release run reproducing its digests" for block 6
    (`RUN_STATE.md:310`). REG §17's last entry is dated 2026-10-17 (REG:1382-1406).
- **Why the named program cannot run block 6.** The block-5 script takes one archive per pack (`--alpha`, `--beta`,
  `--gamma`, I:3148-3152). It binds block 5's catalog (I:73), the GAMMA midpoint window reason (I:75-76, :720) and
  the `claim_usable_false` flag (I:891-892).
- **The three unmerged candidates.**
  - DESIGN, PRs #537 and #572, both open: L9 as production, with an `AnalysisBlock` seam.
  - B6-AN-1, not merged. It ran "pass on the fake adapter", and the "real L9 owed" (B6-AN-1.md:120, :124). Its
    release mode is "not built yet" (:23).
  - RC-B6-1, not merged. It loads the block-5 script by file path (RC-B6-1:42-44).
- **No release program for block 6.** There is no `release_b6`. `scripts/release_b5.py` pins only the block-5 bar set
  (:55-58).
- **The seats.** Seat 1 F1 finds "two incompatible plans": DESIGN's L9 and DLE-2's lean path. Seat 2 §1 adds RC-B6-1
  and notes that the CANONICAL row points at a script with no block-6 mode. Both are right. Seat 2's picture is the
  complete one, and I confirmed every row of its table.

### F2. BLOCKER: S-13 is not operational

- **The rule.** S-13 (REG:1206, marked "closed") and §12.3 item 4 (:1154-1155): each run's phase energy within 1 mJ,
  and "every printed quantity, compared unrounded, within half a unit of its last printed digit". REG registers no
  printed digits.
- **Three tables exist (verified):**

  | Table | Where | J | R, ratios | per-token | t | p | Status |
  |---|---|---|---|---|---|---|---|
  | Placeholder | `tests/independent_recompute/bar_sets/s13_block6.json` on `main` | 5 | 4 | 6 | 3 | 4 | self-declared "PLACEHOLDERS ... must be replaced" |
  | DESIGN D15 | DESIGN :962-980 | 5 | 4 | 8 | — | — | derived (above float noise, below 1% of the smallest half-width); unmerged |
  | RC-B6-1 ratified | RC-B6-1:1127-1135 | 4 | R and R_cm 2; factor and energy ratio 3 | 6 | 2 | 4 | lead decision 1, 2026-10-27 (RC-B6-1.md:147-152; confirmed at `RUN_STATE.md:310`); not in REG §17 |

  For R the bars are 5e-5 against 5e-3: 100×.
- **There are two comparator code paths.**
  - C uses family bars, `max(absolute, relative × |v|, half-unit)` (C:189-193).
  - RC-B6-1 has its own `compare`, keyed on patterns. It compares words, booleans and integers exactly, with no FS3
    rule (RC-B6-1:1190-1212). C has FS3 (`word`, C:242).
- **The placeholder key and the missing families.**
  - C never reads `placeholder` (no match in C), so the placeholder set loads cleanly.
  - My probe shows that a meter row compared under that set refuses with `bars_family_missing:meter_j` (C:212-215).
  - So the five missing meter and machine families (`machine_j, meter_j, meter_w, rho, window_edge_s`) fail closed,
    not silently. This answers seat 1's open question 6.
- **The run set behind "each run's phase energy" is not registered.** RC-B6-1 lead decision 2 chose kept units,
  surviving references and the clean corpus.
- **Block 5 avoided this question** with item 83 rulings 1-2: its coded bars bind, and S-13 "is block 6's and stays
  there" (`RUN_STATE.md:342-343`).
- **The seats.** Seat 1 says block 6 registers no precision and only a placeholder exists. That is true of REG, but it
  missed the lead-ratified table on the RC-B6-1 lane. Seat 2's "three conflicting tables" is correct. Decision 2
  above settles seat 1's option (a) against seat 2's strictest-per-family.

### F3. BLOCKER: the D5 lesson is not carried, and block 6 exercises the binder three times

- **The cause** (RESUME:21). `_order_member_ids(..., campaign_log=True)` counts the campaign-level evaluation row as
  executed members. Every calibration bundle then appears twice, and all four GAMMA floor cells stay unbound.
- **The fix exists only locally, and it changed after seat 1 looked.**
  - `lane/2026-11-07-b5-analysis-r4` is at `7db6fb9a3` in the canonical clone. It tracks `origin/main`, 5 commits
    ahead. `git branch -r --contains 7db6fb9a3` is empty, there is no `b5/analysis-r4` tag, and no PR is open.
  - Seat 1 saw `cf9fda671`. Since then the lane gained two commits, `7e6ba73b2` and `7db6fb9a3`.
  - Per `7e6ba73b2`'s message, the first fix (`cf42f2a98`) "refused all four synthetic GAMMA floor resolutions (step 9b
    outcome_class, exit 3)".
  - The rule is now two-mode. A log that has executed-member rows binds from them. A log with none keeps the old
    parse.
- **Block 6's runner writes the same record types.** `scripts/run_campaign.py` at `f31aca19f` and at `cf42f2a98`
  carries the same five `record_type` literals: `campaign_occurrence_supersession`, `campaign_stop`,
  `campaign_verdict`, `idle_admission_whole_window_verdict` and `shakedown_gate`. Seat 2's claim holds. The r4 rule
  therefore takes its member-rows mode on block-6 logs, provided those logs carry executed-member rows. I did not check
  that on block-6 bytes.
- **Compressed campaign logs read as empty.**
  - `campaign_provenance.load_campaign_log_rows` reads a compressed log as an empty log (DESIGN :233-236).
  - DESIGN :111 says five sessions' `campaign_log.jsonl` were compressed. That is a design statement, not checked
    against archives.
  - An empty log has no member rows, so the binder refuses.
- **The exposure.** The pairing is GAMMA r1 ↔ (ALPHA r1, BETA r1), r2 ↔ (ALPHA r3, BETA r2) and r3 ↔ (ALPHA r3,
  BETA r3), with ALPHA r4 floor-only (DESIGN :626-631). So the binder runs three times over cross-session roots.
- **The failure mode.**
  - A refusal makes step 9b exit 3, while `completed_without_tooling_refusal` stays true (DLE:334-347).
  - REG §12.3 item 3 ("no tooling refusal") would therefore be met by a tooling defect.
  - The lean programs do no floor binding: they take the armwise maximum (TRACE:298-300). So only a comparator
    disagreement can catch it, and only if the second side runs L9.
- **The seats.** Seat 1's "local only" is confirmed and updated above. Seat 2's "identical record types" and
  "compressed log reads empty" are confirmed.

### F4. BLOCKER: the comparator covers what the lean computes, not every registered family

- **What is accepted, and for which block.**
  - DLE-1 accepts the seven uncovered families for block 5 only (DLE:111-128). The seven are monitor cost, arm
    hazards, battery, battery temperature, reference/corpus/NEG-8 history, attempt history and selection.
  - DLE-2 requires each to be added to the lean program, or named as supplied by the audit, before block 6 (DLE:169-176).
  - None of the seven has a lean implementation (LEAN:70-80).
  - REG §9.5's preamble (:1009-1012) requires these disclosures in every counting session, so they recur nine times.
- **RC-B6-1's gaps** (RC-B6-1.md:178-200, :262-281).
  - Not computed: §9.5 item 5 (the per-phase whole machine; S-15 is open), §9.5 item 7 (block-5 codes carried) and
    the §8.3 item 3 E_add and P* alternatives.
  - The J6 sensitivity line is dropped (open issue 5).
- **What RC-B6-1 does cover.** Seat 1 said block-6-only quantities have "neither producer nor comparator family". That
  holds on `main`, but RC-B6-1 covers §9.1-§9.4, §9.5 items 1-4, 6 and 8, §10, §11.1, §11.2 and §11.4.
- **The request-level whole-machine line is ambiguous.** This is B5-PLAN §8.2,
  `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md:646`.
  - It runs under REG §13's "B5-PLAN §3.1 steps 1 to 11", but REG §9.5 does not list it.
  - All of block 5's D1-D4 lived in it: the `battery_term`, `machine_j`, `meter_j`, `meter_w`, `rho` and
    `window_edge_s` rows of TRACE's table (:145-157).
  - RC-B6-1 has no meter or machine keys at all.
- **The key contract was written by the lean program itself.**
  - `configs/b6/recompute/comparison_keys.json` carries `"ruling": "lead decision 2, 2026-10-27: this script's key
    pattern is the comparison contract"`, and B6-AN-1 "is to emit exactly these keys" (RC-B6-1.md:153-164).
  - This reopens the one-side-keyed class that RC-CMP-9's expected-check table closed in C (`claimed`, C:200-202).
  - So a "pass" means the two sides agree on what the lean computes. It does not mean REG §12.3 item 4's "every
    printed quantity".
- **The seats.** They agree. Seat 2's emphasis on the whole-machine line is verified.

### F5. BLOCKER: compressed inputs, and no read path on `main`

- **Every large file is compressed.**
  - After each harvest, the desk lane compresses every file of 1 MiB or more under the runs roots, custody and
    `sources/` (`joulewise/b6/desk_lane.py:243-245` at `1706257c4`; DESIGN §0 item 8). That includes the raw sampler
    plists.
  - `trace_plist_missing` is a STOP flag in both lean programs (I:64-65; RC-B6-1:91 inherits it).
- **`main` has no read path.**
  - `joulewise/desk_compress.py` and `scripts/restore_run_to_scratch.py` are absent from `main`.
  - `desk_compress.read_bytes` exists at `f31aca19f` (`joulewise/desk_compress.py:50`) and shells out to a zstd binary
    (`zstd_path`, :20).
  - `restore_run_to_scratch.py` arrived with PR #573. That PR merged into `lane/2026-10-22-bytes-battery-term`
    (`cf960e97e`), which is in neither `main` nor `archive/pre-prune-2026-11-06`.
  - This also confirms seat 1's remark that B6-AN-1's integration base includes BYTES-lane code (B6-AN-1.md:251-253).
- **Disk.**
  - The Air has 54 GiB free now (`df -g`). Seat 2 measured 66 GiB earlier.
  - One session is 32.75-38.82 GiB decompressed, and a GAMMA unit about 109 GiB (DESIGN :238-241).
  - So a plain restore of more than one session does not fit.
- **Options.**
  - `compression.zstd` streaming, with a SHA-256 check against the desk record. It is stdlib in Python 3.14.6, present
    on this Air, but python3.13, which the runbooks pin, lacks it (verified).
  - `desk_compress.read_bytes`.
  - An APFS in-place restore per unit (DESIGN §0 item 8). B6-AN-1 A7 exercised it on synthetic trees only.
- **The seats.** They agree.

### F6. MAJOR (BLOCKER for the block-5 script): exclusions and counting

- **The block-5 script** re-derives against block 5's catalog (I:73), applies the GAMMA midpoint reason (I:720) and
  flags `claim_usable_false` (I:891-892).
  - `exclusions_rederivation_mismatch` and `kept_units_disagree` are STOP flags (I:65-68).
  - r2-gamma's `claim_usable` is false under a rule REG §8.2 drops (`RUN_STATE.md:169`; REG:600-603).
  - Pointed at block 6, it stops or misjudges.
- **RC-B6-1** takes counting from `derived/b6-acceptance.json`, checked against `attempts.jsonl`. It takes kept units
  as "roster units none of whose runs the acceptance record excludes" (RC-B6-1:11-15). It does not re-derive them
  under the block-6 catalog (digest `b5bce6c6…`, REG:1196).
- **The P* desk exclusion** (REG §8.3 item 3, S-9 at :1202) changes kept units, and no implementation applies it
  (RC-B6-1 open issue 3). DESIGN §0 item 2 specifies it. B6-2's replay removes 0 of 840 science runs (DESIGN §0
  item 9).
- **The seats.** Seat 1 F6 describes the block-5 script, seat 2 §4 describes RC-B6-1. Both are right; neither program
  re-derives under the block-6 catalog.

### F7. MAJOR: b_op

- **The stored bracket is wrong; counting is not.** The block-6 harvest stored its brackets under block 5's acceptance
  (s_bracket 14.531 ms against the registered 10.818 ms). The cause is that `_Harvest._acceptance_path` falls back to
  block 5's file (DESIGN §4.8, :550-560). The acceptance itself evaluated the bracket under the block-6 registration,
  so counting is unaffected (DESIGN :557-558).
- **The block-5 script** recomposes b_op with block 5's constants and falls back to the stored b_op when captures are
  missing (LEAN:115). It would be wrong on block 6.
- **RC-B6-1** recomposes `max(pre, post) + max(drift, 10.818 ms)` from the stored captures (RC-B6-1:62, :317-332)
  and compares the result with the acceptance record's `calibration.operative_bound_s`. Two gaps:
  - A mismatch raises `b_op_mismatch`, which is not in RC-B6-1's STOP set (:91-93). DESIGN §4.8 makes any difference
    a tooling refusal, so the two block-6 implementations disagree on severity.
  - When captures are missing, RC-B6-1 uses the acceptance record's `pre_s` and `post_s`, raising
    `b_op_from_record`. Those values are captures, so the s_bracket error does not reach them.
- **The seats.** Seat 1 F5 ("falls back to the wrong value") describes the block-5 script. Seat 2 ("carried")
  describes RC-B6-1 and DESIGN. Both are right.

### F8. MAJOR: hash independence holds for the code, but the inputs are not authenticated

- **The code is separate.**
  - RC-B6-1 imports nothing from `joulewise/` (RC-B6-1:4-7).
  - C enforces `test_no_l9_import` (`tests/independent_recompute/test_comparator.py:805`).
- **The inputs are not authenticated.**
  - `Reader.raw` reads bytes without checking them against the harvest or seal manifests (LEAN:121; I:290).
  - DLE-2's "bound by content hash" (DLE:152-155) is implemented as L9's step-0 census plus `release_b5.py`
    stage (a). Both are block-5 only.
  - RC-B6-1 records `b5_program_sha256` (:1106) but never compares it against a pinned value. Any later edit to the
    block-5 script, such as DLE-2's coverage additions, silently changes block-6 arithmetic.
- **Two further weaknesses.**
  - Kept units are not re-derived (F6).
  - The comparator is a subcommand of the production file.
- **The seats.** They agree (seat 1 F8's caveats; seat 2 §4).

### F9. MAJOR: runtime (the two seats' figures reconciled)

- **Block 5 r3's heavy dry run took 1 h 40 min** (RESUME:20).
- **The lean block-5 figures are projections, not measurements.**
  - About 8-13 min end to end with 10 workers on a free host, and 25-65 min serial
    (`docs/analysis/b5/RELEASE-RUNBOOK-lean.md:128-141`; `docs/run_reports/2026-11-06-b5-care-audit.md:160-171`).
  - Seat 1 called 8-13 min "measured" and cited lines :148-161. Both are corrected here.
- **RC-B6-1 has no member pool.** Its CLI is at RC-B6-1:1298-1320; it has no `--workers` and no pool.
- **The block-6 size is an estimate.** The six floor sessions are 125 runs each where RUN_STATE records it (:158,
  :204). Seat 2's figure of about 1,071 members (3.4× block 5's 316) is not verified, but the magnitude holds: at
  least 750 in the floor sessions alone.
- **The lean estimates.**
  - About 1.4-3.7 h serial.
  - About 20-40 min pooled. Seat 1 says 30-40 min and seat 2 17-27 min. The gap is their I/O assumptions, and neither
    is measured.
  - Decompressing `.zst` adds CPU that nobody has measured.
- **The L9 audit as designed.**
  - It needs about 15 session-passes: six floor units, plus three GAMMA units of three sessions each.
  - B6-AN-1 A7 runs both phases twice, and REG §13 adds a release re-run.
  - The total is about 16-25 h (seat 2).
  - With floor-session steps reused across units (D-188 result equivalence), no repeats and units in parallel, it
    drops to about 3-5 h. Seat 1's "about 5 h" is the serial-with-reuse case.
  - Restore I/O comes on top, unmeasured.
- **Conclusion.** The 1 h 40 min target holds only on the lean path once it is pooled.

### F10. MAJOR: estimand gaps

1. **§9.5 item 3, T** (REG:1016-1018). DESIGN :659-662 uses estimator-1 weights: 0.2 × the repeat mean + 0.8 × the
   quad-run mean. RC-B6-1:560-561 uses the plain mean over repeat and quad members. The two are identical only for a
   complete cell: 10 repeats and 10 quads of 4 give 10/50 = 0.2 and 40/50 = 0.8. Any cell with unequal losses
   differs. The text should also state the E_ref/T_ref basis exactly: the start, midpoint and end references'
   request energy and length.
2. **§9.5 item 5 / S-15** (REG:1028-1035, :1208).
   - REG says the per-phase whole-machine definition is "the one committed for block 5". But B5-PLAN §8.2 is
     request-level ("the harvest computes no phase-level figures", `analysis_plan_block5.md:654`).
   - The per-phase line exists only in the recompute (DESIGN §0 item 5), and DESIGN §8 is the candidate definition.
3. **§10** (REG:1058-1078).
   - Its floor summaries mix two s_bracket regimes. Block 5 used 14.531 ms and block 6 uses 10.818 ms, which REG
     sizes at up to 3.713 ms, or 0.175 J of floor (REG:378-387). Seat 2's "about 0.17 J" matches.
   - Three edge cases are unregistered: Q not computable, n = 1, and "block 5: not computed". The 2026-10-27 lead
     ruling fixed their wording in the driver (`RUN_STATE.md:310`), not in REG.
4. **§11.2.** When the cause is a binding defect (F3), a `not_estimable` block-6 session prints "not replicated". The
   dry-run completion criterion has to exclude that case.
5. **§8.3 item 3, E_add and P\*** (REG:651-659, :793-799; S-8 :1201, S-9 :1202). Both enter kept units, hence every
   estimand. No production path computes them.
6. **The J6 timing-bound sensitivity line** (RC-B6-1 open issue 5) is not in REG §9.5, but L9 run unchanged would
   print it. Rule it in or out.
7. **The pairing tie rule** ("earlier t0", DESIGN D16) is not registered. The nine sessions cannot reach it, but it
   belongs in REG.

### F11. MAJOR: the fixtures repeat D5's root lesson

- **The lesson.** The D5 tests passed because their fixtures lacked the real runner's row shape (DLE-4 on the r4 lane).
- **Neither block-6 fixture set is real-chain.**
  - RC-B6-1's fixtures are hand-built (open issue 1). `tests/independent_recompute/support_b6.py:54` writes only
    `rich_telemetry_idle.jsonl`, with no `environment_admission.attempts`.
  - B6-AN-1 runs through a fake adapter.
  - DESIGN §16's generator, which runs the real chain and harvest at `f31aca19f`, is not built.
- **D2.** Waiting admission makes re-measured idle baselines the designed path in block 6 (REG §3.2 item 1,
  :330-337).
  - My static check: `f31aca19f` writes `environment_admission.attempts` as a list of dicts, each with an `attempt` key
    (`joulewise/controller.py:1799`, `:1850`, `:2249`). The adapter names attempt N's file
    `rich_telemetry_idle_attempt_{N}.jsonl` (`joulewise/adapters/powermetrics.py:281`;
    `joulewise/environment_admission.py:131`).
  - That is exactly what the D2 fix reads (I:1954-1967). So the formats match, but no test covers them. This answers
    half of seat 1's open question 7.
- **D4.** Wait-cap and wait-budget skips write `decision="abort"` before sampling (`controller.py:2165-2172` at
  `f31aca19f`).
  - Structurally they would land in `no_measured_request` (I:2440-2448).
  - That list belongs to the request-level machine disclosure, which RC-B6-1 does not have.
- **D3.** r4-alpha has two `member.anchor_not_bounded` members (`RUN_STATE.md:204`).

### F12. MINOR: open slots and durability

- **Open slots.**
  - S-9 and S-11 are filled only on PR #529, open since 2026-10-22 (REG:1202, :1204).
  - S-14, S-15 and S-16 are open (REG:1207-1209).
- **The block-6 inputs live off `main`.**
  - Block-6 collection code, the catalog, the acceptance and the pins live only on the draft PR #502 lane
    (`1706257c4`) and the tag `b6/collection`, which points to `f31aca19f`.
  - `configs/b6/` and `joulewise/b6/` are absent from `main`.
  - S-14 should vendor `configs/b6/registration/*` and `flag_catalog_b6.json`, byte-identical to the S-3, S-4 and S-18
    digests.

### F13. MINOR: map, mirror and scope notes

- **`CANONICAL.md:48`** names the block-5 script as production for blocks 6 and later. It has no row for RC-B6-1,
  B6-AN-1 or DESIGN. The prune rule (check CANONICAL before building, delete superseded work in the same PR) needs
  those rows.
- **Item 144** (`RUN_STATE.md:807-822`) deletes L9-ENV-3's whole-window mirror, about 440 lines, after the block-5
  release. Block 6 ran the same frozen `reduce.py` (REG:536-539), so any L9 block-6 audit still needs the mirror.
  - Seat 2 says the lean `overlap()` is already equivalent to the clamp. I did not re-verify this, so it is not relied
    on here.
- **Items 144-145** queue a `reduce.py` clamp plus an acceptance reissue for the next uncollected registration
  (`RUN_STATE.md:813-826`). They are not a block-6 amendment.

---

## 3. Registration amendments (merged; each is a dated REG §17 entry under §12.4)

- Each entry is signed blind, extending the DLE signing statement to block 6, and is checked by one executing refuter.
- No entry changes registered arithmetic.
- The order is what blocks what.

| # | Amendment | From | Resolves |
|---|---|---|---|
| R0 | **Framing entry.** Block 6 is collected and blinded, and these entries are made under §12.4 before release. The signer states that no block-5 or block-6 outcome has been seen. The deadline is decision 3. | seat 2 #1 | §0 premise |
| R1 | **Production program and second side** (decision 1). Name the printing program by path and digest, and pin the block-5 script digest it loads. Redefine §12.3 items 3-4: what "analysis programs" and "independent recompute" now are. Replace §13's release re-run with DLE-1-style digest re-verification plus an input census, and drop the determinism repeats. Disagreement rule: a hold, decided by the defect found (CARE §2.5 item 3). Add the audit-unfinished rule (decision 5). The disagreement surface includes strict refusals. Restate DLE-2's agreement gate on the first counting block-6 session. Correct §1.10 and `CANONICAL.md:48`. | seat 1 A1; seat 2 #2, #3 | F1 |
| R2 | **S-13 made definite** (decision 2). One printed-precision table, pinned by digest. One comparator code path. The registered run set for run phase energies. The FS3 tie rule in that path. Coverage defined as a registry of REG-printed quantities, with unmatched or absent keys failing closed. Strike the placeholder set, or make `load_bars` refuse any set with `placeholder: true`. | seat 1 A2; seat 2 #4 | F2 |
| R3 | **Printed-quantity table** (decision 6). For every §9.5-§11.4 quantity, the seven DLE-2 families, the §8.2 request-level whole-machine line and §9.5 item 7, give the producer(s), comparator family and bar. Where there is one producer, label it "not independently recomputed", or "copied from record, bound by digest", as item 83 ruling 3 did for block 5. State whether B5-PLAN §8.2's request-level line is registered for block 6. | seat 1 A3; seat 2 #5 | F4 |
| R4 | **S-14 contents.** For any L9 use, a base at or after `b5/analysis-r4` (D1 fix, D5b, D5 two-mode rule). The blind dry run runs floor binding on all three GAMMA units with their real pairs and prints per-cell bound flags (structure only). "All serving cells unbound" is a tooling refusal class, never an outcome. An exit 3 counts as completion only if a structure-only probe shows the refused resolutions are not binding failures. | seat 1 A4; seat 2 #6 | F3, F10.4 |
| R5 | **b_op for block 6.** Both programs recompose b_op from each session's captures under `configs/b6/registration/acceptance.json` (`ea130c87…`, s_bracket 10.818 ms). The harvest's stored bracket, made under block 5's acceptance, is disclosed only and enters no number. A difference from the acceptance record's `calibration` b_op beyond 1e-6 relative is a refusal, never a flag or a fallback. | seat 1 A5 | F7 |
| R6 | **Exclusions and counting.** The sealed `joulewise.flags.exclusions.compute` with catalog digest `b5bce6c6…` and no pack-scoped window reasons. Counting from `derived/b6-acceptance.json` and the loop record. `claim_usable` is never read. Both programs refuse on disagreement. Tested on r2-gamma's structure. | seat 1 A6; seat 2 C3 | F6 |
| R7 | **Session index and pairing table, registered as structure.** The nine session ids, rounds and t0 order. The pairing table of F3 (fixed by counting alone, REG §6.2). The tie rule: earlier t0. | seat 1 A7 | F10.7 |
| R8 | **S-15 fill** (decision 7). DESIGN §8's meter-only per-phase definition (BAT-2 settled as meter-only, REG:1030-1035), with both producers named or the line labelled single-implementation. Block 5's per-phase value: computed after the block-5 release by block-6 code, or "block 5: not computed". | seat 1 A8; seat 2 #6 | F10.2 |
| R9 | **Estimand text** (decision 8). §9.5 item 3's T weighting and E_ref/T_ref basis. A §10 label for the s_bracket regime difference, with a labelled block-6-only summary beside it. The §10 edge cases (non-computable Q left out, with n reduced and named; n = 1 prints "not defined"; "block 5: not computed"). §11.2 excludes binding-defect `not_estimable`. J6 line in or out. | seat 1 A9; seat 2 #7 | F10 |
| R10 | **S-9, S-11 and S-8.** Merge PR #529's §17 entry, or enter it again. Register that P_x, T_phase, E_add and the removal counts are hazard structure, computed and reported before the dry run. The production path implements the E_add alternative and the P* desk exclusion, including GAMMA's per-model P*. Name the E_add code as part of S-14. | seat 1 A10; seat 2 #6, #8 | F6, F10.5 |
| R11 | **Inputs and reading.** Cite tag `b6/collection` (`f31aca19f`) and the S-3, S-4 and S-18 digests, and vendor those files into S-14. The production path authenticates its inputs: the archive `SHA256SUMS`, the `harvest.json` and acceptance digests, and the desk-compression rows, checking decompressed SHA-256. It reads `.zst` through one named path (decision 9). `trace_plist_missing` stays a STOP. | seat 1 A11; seat 2 C1 | F5, F8, F12 |
| R12 | **Fixtures before S-14 is cut.** Production-shaped synthetic sessions generated by the real chain at `f31aca19f` (DESIGN §16). They must cover: waited runs with attempt-N telemetry; wait-cap and budget skips; `anchor_not_bounded` members; campaign logs that mix executed-member rows and the trailing whole-window evaluation row; compressed campaign logs and plists; and one cross-session GAMMA unit. | seat 1 A12; seat 2 C4 | F3, F11 |

## 4. Code preconditions (not registration text, but they gate the release)

| # | Precondition | From |
|---|---|---|
| C1 | `.zst` read path plus input authentication (R11). | seat 2 C1 |
| C2 | A member pool in the block-6 lean program; reuse the block-5 script's `MemberPool` (I:586, :3161-3165). | seat 2 C2 |
| C3 | Re-derive block-6 exclusions in the lean program (R6). | seat 2 C3 |
| C4 | Real-chain fixtures (R12). | seat 2 C4 |
| C5 | Keep the L9-ENV-3 mirror until any L9 block-6 audit has run (decision 10). | seat 2 C5 |
| C6 | `CANONICAL.md` rows for the block-6 tools; delete superseded lanes or mark them. | seat 2 C6 |
| C7 | A `release_b6` wrapper, analogous to `release_b5.py` stages (a)-(c), that pins the R2 bars by digest. | seat 2 C7 |
| C8 | Split the comparator out of the production file, keyed by the R3 registry; make `b_op_mismatch` a STOP (R5); pin the block-5 script digest. | seat 2 §4; this synthesis (F7) |

## 5. Lessons checklist (merged)

| Lesson | Registration | RC-B6-1 (lean b6, unmerged) | Block-5 script (named by CANONICAL and DLE-2) | L9 / DESIGN | Verdict |
|---|---|---|---|---|---|
| Monitor cost | no §17 entry | not computed | not computed | via the unbuilt seam | **Not carried** |
| Arm hazards | — | not computed | not computed | unbuilt | **Not carried** |
| Battery (phase, subject, discharged) | — | battery-assist line only | not computed | unbuilt | **Not carried** |
| Battery temperature | — | not computed | not computed | unbuilt | **Not carried** |
| Reference, corpus, NEG-8 history | — | allowance, bound, verdict only | gross terms; history not computed | unbuilt | **Partial** |
| Attempt history (blocks 5 and 6) | — | not computed | not computed | unbuilt | **Not carried** |
| Selection | counting and pairing replace it | counting checked against `attempts.jsonl`; pairing implemented | one window per pack | DESIGN §4.4-4.6, §5 | Partial; R6 and R7 needed |
| D1 (L9 key) | — | no machine line | fixed in r3 | fixed in r3 | Carried in L9; a D1-type bug would pass the lean side (F4) |
| D2 (idle attempt) | — | via `B5.rail_idle_power`; fixture lacks attempt N | fixed | — | Format matches statically; untested (F11) |
| D3 (unanchored members) | — | machine line absent | fixed | — | Due when the machine line is built |
| D4 (no measured request) | — | machine line absent | fixed | — | Wait-cap skips untested (F11) |
| D5 (campaign-log parse) | S-14 not pinned | no binding (only the comparator catches it) | — | r4 local only; compressed log reads empty | **Not carried** (F3) |
| D6 (NEG-8 terms) | §9.5 item 7 disclosure-only | compares allowance, bound and verdict only | conditional landed | — | OK |
| Item 53 (`claim_usable`) | — | carried | **not carried** (I:891-892) | DESIGN §4.5 | Never point the block-5 script at block 6 |
| FS3 tie rule | — | **not carried** (words exact) | in C | — | R2 |
| One-side-keyed contract (RC-CMP-9) | — | **regressed** (self-generated keys) | closed in C | B6-AN-1 copies the keys | R2, R3 |
| Stored bracket under block-5 acceptance | — | carried (10.818 ms; mismatch only a flag) | **not carried** (fallback) | DESIGN §4.8 | R5 |
| Estimands well defined | S-13, S-15, §9.5 item 3 T, §10 edges open | — | — | — | R2, R8, R9 |
| Recompute hash-independent | — | code yes; inputs no; block-5 digest unpinned | code yes; inputs no | — | R11, C8 |
| Comparator covers every family | — | no | no | — | R3 |
| Runs fast | — | serial, ~1.4-3.7 h est. | pooled | ~16-25 h as designed | C2; lean path only |

## 6. What I dropped, corrected or could not verify

- **Corrected (seat 1).** "The lean path measured 8-13 min" is a projection (RELEASE-RUNBOOK-lean.md:128-141), and the
  citation was :148-161.
- **Corrected (seat 1).** "Block 6 registers no printed precision" is true of REG, but the lead ratified RC-B6-1's
  table on 2026-10-27 (F2).
- **Corrected (seat 1).** "Block-6-only quantities have neither producer nor comparator family" holds on `main` only.
  RC-B6-1 covers most of them (F4).
- **Updated (seat 1).** The r4 lane is now at `7db6fb9a3`, not `cf9fda671`, and its fix became two-mode after
  `cf42f2a98` broke the synthetic chain (F3).
- **Resolved (seat 1, open question 6).** The comparator refuses meter rows when the bar set lacks the meter
  families. It is not silent (F2).
- **Half-resolved (seat 1, open question 7).** The D2 metadata and file names match statically. The wait-cap path
  is untested (F11).
- **Superseded (seat 2).** "66 GiB free" is now 54 GiB.
- **Not verified (seat 2), kept as an estimate.** "About 1,071 block-6 members" (F9).
- **Not verified (seat 2), kept as a design statement.** "Five sessions' campaign logs compressed" comes from
  DESIGN :111 (F3).
- **Not verified (seat 2), not relied on.** The lean `overlap()` being equivalent to the L9-ENV-3 clamp (F13).
- **Dropped (seat 2).** "~40 binding sites, 5 frozen-file merges" for the L9 seam. DESIGN §4.2 confirms the scale (many
  sites across several frozen files, plus an hours-long replay), but I did not confirm the exact counts.
- **Dropped (seat 2).** "One refuter AGREE" on PR #529. Not checked.
- **Dropped (seat 1).** "Items 3 and 4 of §9.5 exist only on the recompute side" is trivially true on `main`, where no
  block-6 L9 exists. It is folded into R3.
- **Out of scope (seat 2, open question 3).** The brief names Block 6 and its files explicitly, so it means the
  collected block. The reduce.py clamp is noted under F13.

---

## Appendix A: seat 1 report (Fable 5.1, high), verbatim

````markdown
TOP: ["Block 6 has two incompatible, unregistered analysis production plans: REG §13 / DESIGN B6-1 (PR #537) build on heavy L9 with an AnalysisBlock seam; DLE-2 (2026-11-06) makes the lean recompute the production path. REG §17 has no entry since 2026-10-17 (block6_replication_DRAFT.md:1382-1406 @ ca2d1ee97) and DLE-2 says the entry is owed (DEVIATION-LOG.md:167-168). §12.3 item 4 and §13's post-release byte re-run become wrong under DLE-2.","S-13's tolerance ('half a unit of the last printed digit', REG :1154-1155, :1206) is undefined because block 6 registers no printed precision; the only block-6 bar set (tests/independent_recompute/bar_sets/s13_block6.json) is self-declared PLACEHOLDER, the comparator never reads the `placeholder` key (compare_b5_recompute.py:153-155, :191-192), and the set names 11 of the 16 block-5 release families (missing machine_j, meter_j, meter_w, rho, window_edge_s).","The D5 lesson (campaign-log evaluation row counted as members in analysis_engine/inputs.py _order_member_ids, RESUME.md:27-29) is fixed in no pushed or pinned commit (r4 lane exists only as local worktree jw-wt/b5-r4 @ cf9fda671); block 6 runs the same floor binder three times over cross-session pairs (GAMMA r1↔A r1/B r1, r2↔A r3/B r2, r3↔A r3/B r3), and an unbound floor prints as a registered outcome with a D-189 exit 3, so REG §12.3 item 3 would be met by a tooling defect.","The seven DLE-2 uncovered families (monitor cost, arm hazards, battery, battery temperature, reference/NEG-8 history, attempt history, selection) have no recompute implementation on main (LEAN-COVERAGE-AUDIT.md:53-62, :70-80) and REG §9.5 (:1007-1011) requires each of nine sessions to print them; block-6-only quantities (§10 summary, §11 Δ/replication word/flagged-inclusive, §9.5 items 5-8, P*/E_add) have neither producer nor comparator family.","Every block-6 archive stored its calibration bracket under block 5's acceptance (s_bracket 14.531 ms vs registered 10.818 ms; DESIGN §0 item 7; harvest_b6_session.py:14,43-47 @ 1706257c4) and desk-compresses every raw plist to .zst (desk_lane.py:243-244); the recompute falls back to the stored b_op (LEAN :115) and stops on a missing plist (independent_recompute_b5.py:64-68), so as written it would either misdefine b_op or stop on every session.","The recompute and L9 are hard-wired to one window per pack (independent_recompute_b5.py:3148-3161, dry_run.py:232, :707, :1649; compare_b5_recompute.py:104) and re-derive exclusions against block 5's catalog (independent_recompute_b5.py:73) with STOP flags on mismatch; block 6 needs the b6 catalog (259 codes, S-3 digest b5bce6c6…), counting from derived/b6-acceptance.json (RUN_STATE item 53 r2-gamma claim_usable finding), six floor units and three GAMMA units.","Wall time: block 5 r3 is 1 h 40 min per three-window set; a heavy L9 audit over nine sessions is about 5 h plus in-place restore of ~109 GiB per GAMMA unit, while the lean path is about 30-40 min (RELEASE-RUNBOOK-lean.md:148-161); the 1 h 40 min target holds only on the lean path or with per-unit parallelism.","S-15 (whole-machine per phase) cannot be filled by pointing at block 5: B5-PLAN §8.2 is request-level only (analysis_plan_block5.md:653) and the per-phase line exists solely in the recompute; S-9/S-11 remain OPEN on main (PR #529 unmerged since 10-22); §10 edge cases and the pairing tie rule are unregistered.","All twelve amendments (A1-A12) must land before the block-5 unseal, because REG §12.3 item 2 (:1150-1151) makes any post-unseal block-6 analysis decision one taken with block-5 outcomes in view; block-6 collection code and configs exist only on an unmerged lane (f31aca19f not in main) and the b6/collection tag."]
OPEN: ["When is the local r4 lane (jw-wt/b5-r4, lane/2026-11-07-b5-analysis-r4 @ cf9fda671, not on origin) pushed, reviewed and tagged? S-14 cannot cite the D5 cause fix until then.","Does DLE-2 (lean recompute as production) supersede DESIGN B6-1's L9-based build for block 6, or do both run with lean printing and L9 auditing? The B6-AN-1 driver (lane/2026-10-27-b6-analysis) was built on a BYTES draft base and has no release mode.","Did the block-6 harvest's member-level phase checks (REG §8.3 attribution-bound quarter rule) use the stored b_op under block 5's acceptance (s_bracket 14.531 ms)? A counts-only blind replay under the registered b_op would show whether any kept-unit set differs.","Who rules block 6's printed precision for S-13, or should block 6 adopt block 5's coded 1e-6 bar set (already full-size tested) with the 1 mJ phase-energy bar as ceiling?","Should block-6 registration amendments be permitted at all after the block-5 unseal? REG §12.3 item 2's rationale argues for 'no', making the amendment window the next few days.","Does the comparator require the five meter/machine families (machine_j, meter_j, meter_w, rho, window_edge_s) when meter rows exist, given the s13 set omits them yet loads without refusal in tests?","Does the block-6 driver at f31aca19f write the same environment_admission.attempts metadata and rich_telemetry_idle_attempt_N.jsonl names that the D2 fix reads, and does no_measured_request cover idle.wait_cap_skip / idle.wait_budget_skip members? Neither is covered by a fixture."]
# Block 6 design and registration audit: Fable 5.1 seat

**Date:** 2026-11-07. **Seat:** Fable 5.1 (high), independent of the Opus seat on the same brief.
**Durable copy:** `docs/research-audits/2026-11-07/block6-design/fable-seat.md` on `origin/research/2026-11-07-block6-design-fable` (`b9019c48b`). This return adds one refinement to F4 found after the push (see F4).
**Repo state read:** `origin/main` at `ca2d1ee97`; the block-6 collection line `lane/2026-10-17-b6-packs-registered` at `1706257c4` (collection pin `f31aca19f`); the block-6 analysis design `lane/2026-10-22-b6-analysis-design` at `578685ec3` (PR #537); the S-9/S-11 fill `lane/2026-10-22-b6-s9-s11` at `c37614f71` (PR #529); the block-6 driver draft `lane/2026-10-27-b6-analysis` at `10b2b679c`.
**Blinding:** no `/Users/edr/jw-b5-*`, `night-*`, custody, archive or `restricted/` path was opened; no block-5 or block-6 energy, interval, contrast, outcome word or verdict was read or inferred. Every number below is a design constant, a count, a wall time or a line number. Tests run: `tests.independent_recompute.test_comparator` S-13 bar-set tests (`JW_B5_SYNTHETIC_ONLY=1`, `nice -n 19 taskpolicy -b`, TMPDIR under `/private/tmp/jwburn-fable-b6`): 2 selected tests OK. No real data, no model weights, nothing on the measurement Mac. Worktree created under `jw-wt/` and removed.

Citations are `path:line @ commit`. Aliases: **REG** = `docs/registrations/block6_replication_DRAFT.md` (bytes identical at `2a4e5149c` and `ca2d1ee97`, per `docs/registrations/block6_freeze_by_commit_addendum.md:5-6`); **DLE** = `docs/analysis/b5/DEVIATION-LOG.md`; **LEAN** = `docs/analysis/b5/LEAN-COVERAGE-AUDIT.md`; **TRACE** = `docs/run_reports/2026-11-07-b5-release-hold-trace.md`; **RESUME** = `docs/handoff/2026-11-07-account-retirement/RESUME.md`; **DESIGN** = `docs/design/b6_analysis_additions.md` (on `578685ec3` only); **I** = `scripts/independent_recompute_b5.py`; **C** = `scripts/compare_b5_recompute.py`. All at `ca2d1ee97` unless another commit is named.

---

## 0. One correction to the brief, and the verdict in three sentences

The brief says to list amendments needed "BEFORE any Block 6 data exists". Block 6 finished collecting on 2026-10-21: nine counting sessions, alpha r1/r3/r4, beta r1/r2/r3, gamma r1/r2/r3 (addendum `:24-25`; `RUN_STATE.md:203` item 59). The data exist, sealed and unanalysed. REG §12.4 (`:1168-1173`) therefore governs: no change to registered arithmetic; a rule found wrong may change while block 6 is blinded, by a dated §17 entry checked by one executing refuter. The real deadline is **before block 5 is unsealed**: REG §12.3 item 2 (`:1150-1151`) says block-6 values estimate the same quantities as block 5's, so any block-6 analysis decision taken after the block-5 unseal is taken with block-5 outcomes in view. Every amendment below should land before the block-5 unseal OK.

Verdict. (1) Block 6 has **two incompatible, unregistered production plans** for its analysis (the L9-based DESIGN of 10-22 and DLE-2's lean-recompute production path of 11-06); REG §17 has had no entry since 2026-10-17 (`:1382-1406`), and DLE-2 itself says its block-6 entry "is owed" (DLE `:167-168`). (2) The registered agreement tolerance S-13 is **not well defined**: it is "half a unit of the last printed digit" and block 6 registers no printed precision; the only block-6 bar set in the tree is marked `placeholder`, and the comparator ignores that key. (3) Of the block-5 lessons, D1-D4 and D6 are in main's recompute and comparator, but **D5's cause fix is in no pushed or pinned commit**, block 6 exercises exactly that binder three times over cross-session floor pairs, and the seven DLE-2 uncovered families recur in every one of nine sessions with no block-6 producer or comparator row.

---

## 1. What block 6 is, as registered, and what exists in code

| Registered element | Where | State on `ca2d1ee97` |
|---|---|---|
| Registration + analysis plan, REGISTERED 2026-10-17 | REG `:3`, `:1382-1406` | unchanged since; §17 last entry 2026-10-17 |
| Estimators 1-4: block 5's, per counting session, no pooling | REG §9 `:899-1006` | L9 and recompute exist for one window per pack only (F7) |
| §9.5 labelled lines (8 items), §10 summary, §11.1-11.4 reporting | REG `:1007-1120` | no producer on main; `joulewise/b6/analysis/summary.py` and an 89-line `scripts/b6_analyze.py` on `lane/2026-10-27-b6-analysis` against a fake L9 adapter (`.codex-report/B6-AN-1.md` @ `10b2b679c`: "run through the real L9 programs is owed"; "no release mode") |
| Release condition: close, block-5 release, blind dry run over every session with no tooling refusal, recompute within S-13 | REG §12.3 `:1146-1166` | no block-6 release program; `scripts/release_b5.py` pins the block-5 bar set only (`:58`, `:61`) |
| Analysis commit S-14, whole-machine definition S-15 | REG `:1207-1208` | OPEN |
| S-9 (P*), S-11 (T_phase), due before the blind dry run | REG `:1203`, `:1205` | OPEN on main; filled in PR #529 (`c37614f71`) with a §17 entry, unmerged since 10-22 |
| Collection code, catalog, acceptance, pack files | REG S-1..S-4 `:1194-1197` | **not on main**: `f31aca19f` is not an ancestor of main; `configs/b6/` and `joulewise/b6/` are absent from `ca2d1ee97`; tag `b6/collection` exists (`RUN_STATE.md:872` item 149) |
| Hidden offsets divided out before printing | REG §12.1 `:1138` | `joulewise/b6/blinding.py`, `export_runs.py:149` @ `1706257c4` apply factors only at the export table; raw bundles are unaffected, so raw reads by the recompute are safe |

Two facts about the collected archives the registration did not anticipate (DESIGN §0 items 7-8 `:42-85` @ `578685ec3`, confirmed in lane code):

- **Every block-6 archive stored its calibration bracket with block 5's acceptance** (s_bracket 14.531 ms instead of the registered 10.818 ms, REG `:368-369`). The harvest entry point calls the shared `joulewise.b5.harvest.harvest` with the b6 catalog (`scripts/harvest_b6_session.py:14`, `:43-47` @ `1706257c4`).
- **Every file of 1 MiB or more under the runs roots, custody and `sources/` is desk-compressed to `.zst` after the harvest** (`joulewise/b6/desk_lane.py:243-244` @ `1706257c4`; `joulewise/desk_compress.py`). The raw sampler plists the recompute integrates are among them.

---

## 2. Findings

### F1. Two production plans, neither registered (BLOCKER for the §17 entry)

- REG §13 (`:1175-1188`): "The programs are block 5's analysis programs (lane L9 ...) at their release tag, plus the block-6 additions ... The analysis commit is pinned before the blind dry run ... after the release the analysis re-runs from identical bytes and every output digest must equal the dry run's."
- DESIGN (PR #537, 10-22) builds exactly that: an `AnalysisBlock` binding seam on L9, one L9 chain per GAMMA unit over three sessions, in-place restore of the compressed bytes, a cross-block phase after the block-5 release (DESIGN `:42-85`, `:1138-1204`).
- DLE-2 (11-06, `:140-197`): "For blocks 6 onward, the lean recompute ... is the production path"; L9 runs once per block as an off-critical-path audit; collection-time judgments bound by content hash. DLE-2 lists what it owes: the §17 entry, coverage of the seven families, the agreement gate "on the first counting block-6 session", the audit-unfinished rule, blinding at signing (`:166-193`).
- Registration text that DLE-2 makes wrong: §12.3 item 4 "the independent recompute agrees with the analysis programs" is vacuous when the recompute is the analysis program; §13's post-release byte-identical re-run was dropped for block 5 by DLE-1 (`:71-137`) and has no block-6 counterpart; §1.10 (`:275-276`) defines the recompute as a check, not a producer.

### F2. S-13 is not a well-defined tolerance (BLOCKER for the release comparator)

- REG S-13 (`:1206`) and §12.3 item 4 (`:1154-1155`): 1 mJ per run phase energy, "and half a unit of its last printed digit for every printed quantity". Block 6 registers no printed digits anywhere; the derivation at `:1156-1160` addresses only the 1 mJ bar.
- `tests/independent_recompute/bar_sets/s13_block6.json` says in its own `source` field that its decimals "are PLACEHOLDERS ... must be replaced by the ruled precision. Not adopted for block 5". The comparator reads `printed_decimals` (C `:153-155`, `:191-192`) and never reads `placeholder` (no match in C), so the set would bind silently if pinned.
- Block 5 settled its precision question the other way: the coded 1e-6 bars bind block 5, "S-13 is block 6's and stays there", "block-5 printed precision is then not needed" (`RUN_STATE.md:342-343`, item 83 rulings 1-2). Block 6 inherited the dependency on an unruled precision.
- Coverage: the s13 set names 11 families; the block-5 release set `configs/analysis/b5/recompute_bars.json` names 16, adding `machine_j, meter_j, meter_w, rho, window_edge_s`. Whether the comparator requires those five when meter rows exist was not verified.
- Half a printed unit is weaker than block 5's bars for most families (a 4-decimal `contrast_p` tolerates 5e-5 in p, which can straddle the Holm threshold; DLE-2 `:180-181` names the FS3 tie rule for block 5 only).

### F3. The comparator does not cover every registered family, and block 6 adds families with no producer or row

- The seven uncovered families (LEAN §2 `:70-80`; DLE-1 `:111-128`): monitor cost, arm/host and anchor summaries, battery phase/subject summaries and discharged energies, stage battery temperature, reference/corpus/NEG-8 history, all-attempt history with yield and G10, selection and eligibility. None has a recompute implementation on `ca2d1ee97` (LEAN `:53`, `:56-62`). REG §9.5 (`:1007-1011`) requires each counting session to print B5-PLAN §8.1's disclosures, "the attempt history of the pack, now block 5's and block 6's attempts; battery, thermal, contention and clock counts; reference drift ...; monitor cost". So the seven recur nine times, and under DLE-2 nothing on the production path computes them unless the §17 entry names them "supplied by the heavy audit run" (DLE `:174-175`).
- Block-6-only printed quantities with no comparator family and no recompute code on main: §10 mean and s_Q; §11.1 Δ and per-session differences; §11.2 replication word; §11.4 flagged-inclusive line; §9.5 item 6 (new G/F consistency test); item 7 (block-5 codes carried); item 8 (waited-runs line); §8.3 item 3's desk P* exclusion and S-8's E_add alternative; §9.5 item 5 (whole-machine per phase with rails' share, S-15).
- Two §9.5 lines exist only on the recompute side: item 3 scaled allowance (I `:83`, `:2718-2744`) and item 4 single-step reconstruction (I `:82`, `:2206-2283`). Item 4 is registered as "computed by the independent recompute" (`:1024`), a single-source diagnostic by design; item 3 is not so labelled.

### F4. The D5 lesson is not yet in any pushed or pinned commit, and block 6 hits the same binder harder (BLOCKER for S-14)

- D5 cause (RESUME `:27-29`): `joulewise/analysis_engine/inputs.py` `_order_member_ids(..., campaign_log=True)` counts the GAMMA campaign log's campaign-level evaluation row as executed members; every calibration bundle appears twice and `component_evidence_root_disagreement` leaves all four GAMMA floor cells unbound. The evidence itself was intact. RESUME says an r4 PR "b5 analysis r4: L9 campaign-log member parse (D5 cause), DLE-4" is in flight; at audit time no open PR or origin branch carries it (`gh pr list` searches for "r4" and "campaign-log"; `git branch -r`). **Refinement after the push:** a local worktree `jw-wt/b5-r4` on `lane/2026-11-07-b5-analysis-r4` at `cf9fda671` exists on this Air and is not on origin (not opened by this seat). The fix is therefore local-only and unreviewed; S-14 cannot cite it until it is pushed, reviewed and tagged. Probes are in `docs/handoff/2026-11-07-account-retirement/tools/probe_d5_*.py`.
- Why block 6 is more exposed: REG §6.2 (`:483-505`) binds each GAMMA session's floors to an ALPHA and a BETA session from other archives; with the actual counting set the pairing is GAMMA r1 ↔ (ALPHA r1, BETA r1), GAMMA r2 ↔ (ALPHA r3, BETA r2), GAMMA r3 ↔ (ALPHA r3, BETA r3), ALPHA r4 floor-only (DESIGN §5 worked example 1 `:603-639`, from `RUN_STATE.md` item 59 counts). The binder's campaign-order, ABBA-tag and "every calibration bundle exactly once" checks run three times over cross-session roots produced by `f31aca19f` code, whose campaign-log shape the block-5 fixtures never covered.
- Failure mode if unfixed: a binding refusal prints as a registered scientific outcome (`not_estimable` after D5b, `not_resolvable` before), step 9b exits 3 as a D-189 outcome class, and the dry run "completes" (DLE-3 `:334-347`). REG §12.3 item 3 ("no tooling refusal") would be satisfied by a tooling defect. The only stop is a comparator disagreement against a recompute that takes the armwise maximum without binding (TRACE `:298-300`).

### F5. D1-D4, D6 are carried in main's tooling, but two block-6 shapes are untested

- On `ca2d1ee97`: D1 key fix (DLE-3 item 1), D2 idle-attempt selection and D4 `no_measured_request` (DLE-3 item 4; TRACE §5), D3 `descriptive_unanchored`, D6 condition `neg8_survivor_terms` (C `:952`, `:1399`, `:3300`), and `trace_plist_missing` is a STOP flag (I `:64-68`; DESIGN §15 step 10's audit F4 fix has landed).
- D2 in block 6: waiting admission ends the stream and tries a fresh baseline for up to 1,500 s (REG §3.2 item 1 `:332-337`), so re-measured idle baselines are the designed response to disturbance. The D2 fix reads `environment_admission.attempts[*]` and `rich_telemetry_idle_attempt_N.jsonl`; its tests use block-5-shaped fixtures. Whether the block-6 driver at `f31aca19f` writes the same metadata and names is unverified.
- D4 in block 6: new member states `idle.wait_cap_skip`, `idle.wait_budget_skip` (EXCLUDE_MEMBER in `configs/b6/flag_catalog_b6.json` @ `1706257c4`), runs skipped before sampling; no block-6 fixture exercises `no_measured_request` on them.
- D6 in block 6: REG §9.5 item 7 (`:1041-1050`) keeps the bracket bar bytes and makes the decision disclosure-only, the right shape for the conditional comparison. But the stored bracket's b_op is under the wrong acceptance (section 1). The recompute "recomposes b_op from pre/post plus allowance, compares stored b_op, and falls back to it if captures missing" (LEAN `:115`); for block 6 the fallback target is wrong, and `b_op_s` could compare two programs that both read the stored value.

### F6. The exclusion re-derivation and counting source will refuse or misjudge every block-6 session as written

- The recompute re-runs the exclusion function against block 5's sealed catalog (`CATALOG_PATH = configs/campaigns/v5_claim_25g83/flag_catalog.json`, I `:73`); `exclusions_rederivation_mismatch` and `kept_units_disagree` are STOP flags (I `:65-68`). Block 6's catalog is `configs/b6/flag_catalog_b6.json` (259 codes; S-3 digest `b5bce6c6…`, REG `:1196`), 25 of block 5's 32 session-removing codes are flags (REG `:594-600`), and the GAMMA midpoint reason is dropped (REG `:600-602`).
- `RUN_STATE.md:169` item 53: r2-gamma's `derived/exclusions.json` says `claim_usable: false` (`neg8.midpoint_lost_primary`) while the loop counted it under REG §8.2. The consumer must take counting from the acceptance record, never from `claim_usable` (DESIGN §4.5-4.6 `:434-519` gives a rule; nothing on main implements it).
- Both programs therefore need: the b6 catalog by digest, the sealed `joulewise.flags.exclusions.compute` with no pack-scoped window reasons, counting from `derived/b6-acceptance.json`, and a refusal on disagreement.

### F7. One window per pack is hard-wired; nine sessions and the pairing need a driver, and the wall time follows

- I `main` takes `--ALPHA/--BETA/--GAMMA`, one archive each (`:3148-3161`); `MODELS` constants (`:44-45`). `joulewise/b5_analysis/dry_run.py` `PACKS=('alpha','beta','gamma')` (`:232`), `select_analysed_attempts` picks one analysed attempt per pack and refuses a window harvested twice (`:707`, `:1649`, `:1711`); C `PACKS` (`:104`).
- Units: six floor sessions and three GAMMA units (ALPHA r3 serves two). Pairing rule 2 is well defined for GAMMA r2 (no ALPHA in round 2; r2-alpha never ran). The registration has no tie rule for two counting sessions of one pack in one round (DESIGN D16 supplies "earlier t0"); unreachable with the nine, but it belongs in the registration.
- Wall time. Block 5 r3's real dry run took 1 h 40 min for one three-window set (RESUME `:26`); step 1 strict validation is about 920 s of that and "frozen CPU", step 5 about 970 s (`docs/run_reports/2026-11-07-b5-robust-fullchain.md:80-87`). A heavy L9 audit over six floor sessions and three GAMMA chains is about 3× if floor sessions are extracted once and units run serially: **about 5 h**, plus in-place restore and re-compression of the desk-compressed bytes per unit (a GAMMA unit is about 109 GiB plain, DESIGN §0 item 8). The lean path measured 8-13 min end to end per three-window set on a free host with 10 workers (`docs/analysis/b5/RELEASE-RUNBOOK-lean.md:148-161`): **about 30-40 min** for block 6. The 1 h 40 min target holds only on the lean path, or on a heavy path that runs the three GAMMA units in parallel and skips step 1 by hash binding, which DLE-2 kept for the audit and did not adopt (DLE `:200-210`).

### F8. Is the recompute hash-independent? Yes on values, with three caveats

- It shares no code with L9 (`test_no_l9_import`, `tests/independent_recompute/test_comparator.py:805`), re-integrates raw power records under stored clock inputs, and the comparator verifies L9's output digests (`l9_output_digest_differs`). Under DLE-2 item 2 it binds anchors, fits, exclusions and the NEG-8 record by content hash rather than re-deriving them; the audit run is then "the only check of those judgments for block 6" (DLE `:185-188`).
- Caveat 1: `Reader.raw` reads bytes and records names; it does not authenticate them against the harvest or seal manifests (LEAN `:121`). Caveat 2: every block-6 raw plist is `.zst`; with `trace_plist_missing` a STOP flag the recompute stops on every session until it reads through `desk_compress.read_bytes` or runs inside the in-place restore (DESIGN §15 step 10). Caveat 3: the b_op fallback of F5.
- D-188's exact-equality standard (`docs/decision_log.md:12239-12250`) is for L9 versions against the r1 reference; across lean and L9, S-13 governs.

### F9. Estimand definitions: mostly sound, four gaps

1. **§9.5 item 5 / S-15.** REG says the per-phase whole-machine definition is "the one committed for block 5" (`:1030-1035`); B5-PLAN §8.2 is request-level and says "the harvest computes no phase-level figures" (`configs/campaigns/v5_claim_25g83/analysis_plan_block5.md:653`). The per-phase line exists only in the recompute (`machine_member`, `phase_machine_mean`). S-15 cannot be filled by pointing at block 5, and today the line has one producer. DESIGN §8 (`:802-856`) is a written candidate (meter-only, battery at request level, edge-shift sensitivity δ = b_op + r_max, four corners).
2. **§10 edge cases.** Not registered: a session whose Q is not computable, n = 1, block 5 did not compute Q (the per-phase whole-machine value, which block 5's L9 never printed and which DESIGN §8 proposes to compute from block 5's archives after the release, a new block-5 number). B6-AN-1 ruling 1 and DESIGN §10 (`:866-890`) fix wordings; none is registered.
3. **§11.2 with `not_estimable` block-6 sessions.** "Otherwise not replicated" covers it, but a `not_estimable` caused by a binding defect (F4) would print as "not replicated". The dry-run completion criterion must exclude that case.
4. **§8.3 item 3 / S-8 / S-9 / S-11.** The desk P* exclusion and the E_add alternative enter kept units, hence every estimand. PR #529's replay says 0 of 840 science runs reach the line (counts only, blind), so no number is expected to move; the registration still requires the computation and its S-9/S-11 values, and on main both slots are OPEN. P_x, T_phase, E_add and the counts are hazard structure, releasable now under §12.1 (`:1129-1133`).

### F10. Durability of the block-6 inputs

Block 6's collection code, catalog, acceptance, identity pins and pack registrations live only on a draft lane (PR #502, CI-only, last updated 10-18) and the `b6/collection` tag; main was pruned on 11-06 (`archive/pre-prune-2026-11-06`). The analysis commit S-14 should carry `configs/b6/registration/*` and `flag_catalog_b6.json` byte-identical to the S-3/S-4/S-18 digests, so no analysis step depends on an unmerged branch, and the §17 entry should cite the tag.

---

## 3. Registration amendments needed before any block-6 analysis (and before the block-5 unseal)

Each is one dated REG §17 entry under §12.4, signed blind with the DLE signing statement extended to block 6 (DLE `:182`), checked by one executing refuter. Ordered by what blocks what.

| # | Amendment | Resolves | Changes registered arithmetic? |
|---|---|---|---|
| A1 | **Production program and agreement gate.** Name the program that prints (lean recompute per DLE-2) and the program that audits (L9 heavy, once). Replace §12.3 item 4's wording with: L9 and the lean program agree on every family of A3 within A2's bars; replace §13's post-release byte re-run with DLE-1-style digest re-verification; add the audit-unfinished rule (hold, or release labelled provisional) and the strict-refusal surface of the audit (DLE `:189-191`); state the dry-run completion criterion (exit 0, or a D-189 exit 3 whose refused floor resolutions a structure-only probe shows are not binding failures). | F1, F4, F9.3 | No |
| A2 | **S-13 made definite.** Either (a) adopt block 5's coded bar set (1e-6 relative J/W/ratios, 1e-6 absolute rho and p, exact counts and words) with the 1 mJ phase-energy bar as the registered ceiling, or (b) register a printed-decimals table per family. Add the five meter/machine families and every A3 family. Strike the `placeholder` set and make `load_bars` refuse any set carrying `placeholder: true`. Register the FS3 tie rule for block 6. | F2 | No |
| A3 | **Printed-quantity table.** For every quantity of §9.5-§11.4 and the seven DLE-2 families: producer(s) (lean / L9 / both), comparator family, bar, and the label "not independently recomputed" where there is one producer (as RS item 83 ruling 3 did for block 5). Name the audit run as the supplier of any family the lean program does not print. | F3, F9.1 | No |
| A4 | **S-14 contents.** The analysis commit contains the D5 cause fix (campaign-log member parse, pushed and reviewed first) and D5b; the blind dry run runs step 9's floor binding on all three GAMMA units with their real paired sessions and prints per-cell bound flags (structure only) before the comparator; "all serving cells unbound" is a tooling refusal class, never an outcome. | F4 | No |
| A5 | **b_op for block 6.** Both programs recompose b_op from each session's stored captures under `acceptance.json` `ea130c87…` (s_bracket 10.818 ms); the harvest's stored bracket (block-5 acceptance) is disclosed beside it and enters no number; a difference beyond S-13 between stored captures and recomposed b_op is a refusal, not a fallback. | F5, §1 | No (restores the registered value) |
| A6 | **Exclusions and counting.** The exclusion function is the sealed `joulewise.flags.exclusions.compute` with catalog digest `b5bce6c6…` and no pack-scoped window reasons; counting is `derived/b6-acceptance.json` `counting` (and the loop record); `claim_usable` is never read; both programs refuse on disagreement. Tested on r2-gamma's structure. | F6 | No |
| A7 | **Session index and pairing table, registered as structure.** The nine session ids, rounds and t0 order; the pairing table of F4 (fixed by counting alone, REG §6.2); the tie rule (earlier t0). | F7 | No |
| A8 | **S-15 fill.** Adopt a written per-phase whole-machine definition (DESIGN §8 is the candidate), name both producers, label block 5's per-phase value as computed after the block-5 release by the block-6 code. | F9.1 | New disclosure line only |
| A9 | **§10 and §11 edge cases.** Non-computable Q left out with n reduced and named; n = 1 prints "not defined"; "block 5: not computed"; per-token summarised per session. | F9.2 | No |
| A10 | **S-9 / S-11 / S-8.** Merge PR #529's §17 entry or re-enter it; register that P_x, T_phase, E_add and the removal counts are hazard structure computed and reported before the dry run; name the E_add code as part of S-14. | F9.4 | No (0 of 840 on replay) |
| A11 | **Inputs and reading.** Cite tag `b6/collection` (`f31aca19f`) and the S-3/S-4/S-18 digests; vendor those files into S-14; both programs read desk-compressed files through `desk_compress.read_bytes` or inside a verified in-place restore; `trace_plist_missing` stays a STOP. | F8, F10 | No |
| A12 | **Fixtures.** The eleven production-shaped synthetic sessions generated by the measurement code at `f31aca19f` (DESIGN §16), covering re-measured idle baselines, wait-cap skips, compressed files and a cross-session GAMMA unit, are required before S-14 is cut. | F5 | No |

Timing recommendation under A1: run the three GAMMA units in parallel and extract each floor session once; keep step 1 strict validation in the audit only. Expected: lean path about 30-40 min for all nine sessions; heavy audit about 5 h plus restore I/O, off the critical path.

---

## 4. Open questions for the lead

1. The r4 lane (D5 cause) exists only as a local worktree (`jw-wt/b5-r4`, `cf9fda671`) and not on origin; when is it pushed, reviewed and tagged? S-14 depends on it.
2. Does DLE-2 supersede DESIGN B6-1's L9-based build for block 6, or do both run with the lean program printing and L9 auditing? A1 needs that decision; the B6-AN-1 driver was built on a BYTES draft base and has no release mode.
3. Did the block-6 harvest's member-level phase checks (REG §8.3: "the timing bound is small against the phase length, and the attribution bound is at most a quarter of the phase energy") use the stored b_op under block 5's acceptance? DESIGN §0 item 7 says counting is unaffected; a counts-only replay of the phase checks under the registered b_op (hazard structure, blind) would settle whether any kept-unit set differs.
4. Who rules block 6's printed precision (A2 option b), or is option a preferred? Hash-independence and speed are both better served by option a, already tested at full size.
5. Should block-6 amendments be permitted after the block-5 unseal at all? Given §12.3 item 2's rationale, I would register "no", which makes the A1-A12 window the next few days.

---

## 5. Lessons checklist (brief items, one line each)

| Lesson | Carried into block 6? |
|---|---|
| Monitor cost | No producer on the production path; no comparator row (F3) |
| Arm hazards | Same |
| Battery (phase/subject, discharged energy) | Same; `battery.assist_outside_request` is new in the b6 catalog |
| Battery temperature | Same |
| Reference / corpus / NEG-8 | Gross terms recomputed; history and screen not; D6 conditional landed |
| Attempt history (block 5's and block 6's, REG §9.5) | Not recomputed; L9's history check is against the block-5 index only |
| Selection | Pairing and counting are registered rules but no program implements them on main (F6, F7) |
| D1 L9 key bug | Fixed in r3 |
| D2 idle attempt | Fixed in recompute; untested on block-6 driver shapes |
| D3 unanchored members | Fixed |
| D4 no measured request | Fixed; wait-cap skips untested |
| D5 campaign-log parse | Cause found; fix local-only, unpushed; block 6 triples the exposure (F4) |
| D6 NEG-8 protocol | Fixed; the stored-bracket acceptance mismatch is the block-6 analogue (F5) |
| Estimands well defined | Estimators 1-4 yes; S-15, §10 edge cases, S-13 precision no (F2, F9) |
| Recompute hash-independent | Yes on values; input authentication, compressed reads and b_op fallback are the caveats (F8) |
| Comparator covers every family | No (F3) |
| Runs fast | Lean path yes (30-40 min); heavy path about 5 h unless parallel per unit (F7) |
````

## Appendix B: seat 2 report (Opus 5.5, xhigh), verbatim

````markdown
TOP: ["Block 6 is not unmeasured: nine sessions, all counting, were collected 2026-10-17 to 10-21 and are blinded (RUN_STATE.md:203-207). Amendments can only be blind REG §17 entries under §12.4 (REG:1168-1173), made before the release, not 'before data exists'.","No end-to-end Block-6 analysis path exists. CANONICAL.md:48 names independent_recompute_b5.py, which still binds the block-5 catalog, the GAMMA midpoint reason and claim_usable (:73, :75-76, :891-892) and would mishandle r2-gamma. The lean b6 program and the B6-AN-1 driver are unmerged, B6-AN-1 runs on a fake L9 adapter, the L9 seam is unbuilt and there is no release_b6. REG §12.3 item 4 has no second side.","The §17 entry DLE-2 says is owed (DLOG:167-168) does not exist. DLE-1 is not carried: REG:1187-1188 still requires a release re-run. The S-9/S-11 fill sits on an unmerged lane (c37614f71), and S-14, S-15 and S-16 are open.","All seven DLE-2 families, the request-level whole-machine line (where D1-D4 lived), §9.5 item 7, E_add and P* are missing from the lean b6 program and its key contract. The contract is generated from the lean's own output, which reopens the one-side-keyed class RC-CMP-9 had closed. A comparator pass does not cover 'every printed quantity'.","S-13 is not operational: three conflicting printed-precision tables (s13_block6.json placeholders, design D15, RC-B6-1 ratified) give bars that differ up to 100x (R: 5e-5 vs 5e-3). The run set is unregistered and the FS3 tie rule is not carried (words are compared exactly).","Hash independence has gaps: the lean authenticates no input (DLE-2 relied on L9's step-0 census and release_b5 stage (a), both Block-5-only); b5_program_sha256 is recorded but not pinned; kept units are taken from the acceptance record with no exclusion re-derivation.","Runtime and disk: every Block-6 raw plist is desk-compressed, so the lean stops on trace_plist_missing, and the restore tool it names is not on main. The Air has 66 GiB free against 33-39 GiB plain per session. The lean b6 program is serial (est. 1.4-3.7 h; about 20-30 min with the member pool). The L9 audit as designed is about 15 session-passes x2-3 repeats, about 16-25 h. Python 3.14's stdlib compression.zstd allows streaming reads with no restore.","D2 is the designed path in Block 6 (waiting admission promotes attempt N, controller.py@f31aca19f:2044-2189). The fix reaches b6 through B5.rail_idle_power, but the b6 fixtures never write attempt-N telemetry. D5's root lesson (synthetic fixtures lacked the real runner's rows) applies to both hand-built Block-6 fixture sets, and compressed campaign logs read as empty in L9's loader.","Ill-defined estimands: §9.5 item 3 T (estimator-1-weighted vs plain mean; the two implementations disagree) and the E_ref basis; §10 mixes s_bracket regimes (14.531 vs 10.818 ms) in the floor summaries; the J6 sensitivity line is unruled; E_add and the P* desk exclusion (a registered kept-unit rule) are unbuilt in the production path."]
OPEN: ["Lead ruling: build the L9 Block-6 binding seam so the heavy audit can run as DLE-2 literally says, or adopt the cheaper second side of lean production plus harvest_twin, engine_twin, a small counting/pairing/§10-§11 checker and a reducer stored-energy gate, recorded as a §17 deviation?","Where do the nine Block-6 session archives live now (presumably under /Users/edr/night-b6 on the MBP; not checked), does a second physical copy exist (audit F1), and will the analysis run on the Air (66 GiB free) or the MBP (magistrate-owned, busy with ALIGN)?","Did the brief mean Block 6 (already collected) or the next uncollected registration (DIFFICULTY or a later BYTES pass)? If the latter, the item 144/145 reduce.py clamp plus ULP acceptance reissue belongs in that registration.","Which printed precision will the paper's Block-6 tables actually use? S-13's half-unit bar depends on it, and the three existing tables disagree.","Should a structure-only probe count Block-6 idle.waited runs, wait-cap skips and member.anchor_not_bounded members, to size the D2/D3/D4 exposure before the lean program is promoted?","Should the J6 timing-bound sensitivity line (an L9 ruling for Block 5, not in REG §9.5) be printed for Block 6?"]
# Block 6 design and registration audit (Opus seat, 2026-11-07)

**Basis.** `main` at `ca2d1ee97` (canonical clone `jw-wt/handoff`, fetched today). Lanes are cited at the commits named below. "REG" means `docs/registrations/block6_replication_DRAFT.md` and "DLOG" means `docs/analysis/b5/DEVIATION-LOG.md`, both at `ca2d1ee97`.

**Blinding.** I opened no `/Users/edr/jw-b5-*`, `night-*` or `restricted/` path, and I saw no Block-5 or Block-6 outcome. I ran one synthetic test module (§9). I opened no external URL. I committed nothing. The audit worktree and the TMPDIR have been removed.

---

## 0. The brief's premise is wrong, and that changes what an amendment can be

**Block 6 has already been measured.** It ran nine sessions, alpha r1/r3/r4, beta r1/r2/r3 and gamma r1/r2/r3, all of them counting. Collection ran from 2026-10-17 to the close at 2026-10-21 02:54 PDT (`RUN_STATE.md:203-207`, item 59; `docs/registrations/block6_freeze_by_commit_addendum.md:24-25`, which also lists each session's executed commit). The data are blinded. So no amendment can be made "before any Block 6 data exists".

The rule that governs now is REG §12.4 (`REG:1168-1173`):
- No change to registered arithmetic is allowed once data exist.
- A §8 rule may be changed while the block is blinded, by a dated §17 entry with one executing refuter, and the original rule's result is printed beside the new one.
- A program-only change such as DLE-2 (which changes no estimand) goes in as a §17 entry. DLOG:167-168 says this entry is owed.

Every amendment below is therefore framed as "before the Block-6 release, decided blind". If the brief meant the next *uncollected* registration (DIFFICULTY, or a later BYTES pass), the queued `reduce.py` clamp and ULP acceptance reissue (`RUN_STATE.md:813-825`, items 144-145) belongs there, not in Block 6. Block 6 ran with the frozen `reduce.py` (`REG:536-539`).

## 1. What exists for the Block-6 analysis today

| Piece | Where | State |
|---|---|---|
| Registration | `main` REG, REGISTERED 2026-10-17 | No §17 entry after 2026-10-17 (`REG:1398-1406`). S-14, S-15 and S-16 are open (`REG:1207-1209`). S-9 and S-11 are open on `main` (`REG:1202,1204`) |
| S-9/S-11 fill and its §17 entry | `lane/2026-10-22-b6-s9-s11` `c37614f71` | Unmerged. One refuter AGREE. B6-2's replay removes 0 of 840 runs |
| Analysis design (B6-1) | `fix/2026-10-22-audit-b6-design` `bb9669b69`, `docs/design/b6_analysis_additions.md` | Unmerged. Written before D-188 r2/r3, DLE-1/2/3 and r4. Assumes L9 is production and the recompute is the check |
| Pure-layer driver (B6-AN-1) | `lane/2026-10-27-b6-analysis` `10b2b679c`, `joulewise/b6/analysis/**` | Unmerged. Runs on a **fake L9 adapter**. None of the binding work is built: the `AnalysisBlock` seam, the block-6 exclusions document, P*, allowance, b_op, verdict admission, the §6 lines, `machine.py`, `compare.py`. No release mode (`.codex-report/B6-AN-1.md`, "DIFFERENCES" item 1; A7 "partial") |
| Lean Block-6 program and S-13 comparator (RC-B6-1) | `lane/2026-10-27-recompute-b6` `74a4f8123`, `scripts/independent_recompute_b6.py` | Unmerged. Loads `independent_recompute_b5.py` by path. Built on hand-made fixtures. Leaves out whole-machine, block-5 codes, E_add and P* (RC-B6-1 open issues 1, 3, 5) |
| Map of current tools | `CANONICAL.md:48` | Names `scripts/independent_recompute_b5.py` as "production numbers for blocks 6+". That script has **no Block-6 mode**, and none of the rows above is listed |
| Release tool | `scripts/release_b5.py` | Block-5 only (`release_b5.py:49-58,66-69`). There is no `release_b6` |
| Block-6 code on `main` | — | None (`joulewise/b6`, `configs/b6` and the harvest script are absent, by REG §7 item 1) |

**Consequence.** The release condition of REG §12.3 item 4 has nothing to compare against. "Independent recompute agrees with the analysis programs" needs two sides:
- **L9 (the heavy pipeline):** it cannot open a Block-6 archive (design §0 item 1), and its seam is not built.
- **B6-AN-1:** its "analysis" quantities come from a fake.
- **The lean b6 program:** it is the only real implementation.

## 2. Block-5 lessons: carried into Block 6 or not

| Lesson | Block-6 exposure | Registration | Analysis code (design / B6-AN-1) | Lean recompute (RC-B6-1) | Verdict |
|---|---|---|---|---|---|
| DLE-2 family 1: monitor cost | Printed (REG §9.5 preamble, `REG:1009-1012`) | No §17 entry | Via L9 seams (unbuilt) | Not computed. Not in the key contract | **Not carried** |
| 2: arm/host hazards, anchor summaries (plus new block-6 hazard flags: sleep, agent, waits, time server) | Printed | — | Unbuilt | Not computed | **Not carried** |
| 3: battery phase and subject summaries, discharged energy | Printed | — | Unbuilt | Only the battery-assist line | **Not carried** |
| 4: battery (stage) temperature | Printed | — | Unbuilt | Not computed | **Not carried** |
| 5: reference, corpus and NEG-8 history | Printed ("reference drift with realised counts") | — | `lines.history()` unbuilt | Only allowance, bound and verdict (3 keys). No realised counts, no idle-subtracted family, no loss history | **Partial** |
| 6: attempt history (block 5 plus block 6) | Printed | — | Unbuilt | Not computed | **Not carried** |
| 7: selection and eligibility | Counting and pairing replace selection | — | Counting from acceptance (A1), pairing (A2) | Counting checked against `attempts.jsonl`; pairing implemented; L2 prerequisites not re-adjudicated | Partial (better than B5) |
| D1 (L9 printed `battery_available`) | The same L9 disclosure code, if L9 runs | — | Fixed in r3 | **No request-level whole-machine line and no `machine/meter/battery_term` keys**, which is where D1-D4 lived | **Not carried** (a D1-type bug would pass) |
| D2 (idle term read from the wrong attempt) | **This is the designed path in Block 6.** Waiting admission measures attempt N and promotes it (`joulewise/controller.py` at `f31aca19f`, `_wait_hazard_idle` 2044-2189, `idle.waited` at 2135) | — | — | The fix flows through `B5.rail_idle_power` (`independent_recompute_b6.py:425-438`), but the fixtures write only `rich_telemetry_idle.jsonl` (`tests/independent_recompute/support_b6.py:54`) and no `environment_admission.attempts` | **Code carried, untested on the Block-6 shape** |
| D3 (succeeded member whose anchor did not resolve) | Present (r4-alpha excluded 2 `member.anchor_not_bounded`, `RUN_STATE.md:204`) | — | — | Only matters for the whole-machine line, which is not built | Due when that line is built |
| D4 (no measured request) | Block-6 wait-cap and budget skips write `decision="abort"` (`controller.py@f31aca19f:2171`), the same shape | — | — | As D3 | Due when that line is built |
| D5 (L9 counted campaign-level rows as members) | Applies to L9's GAMMA-unit floor binder. Block 6's `run_campaign.py` writes the same `record_type` set as r4's (I diffed the literals at `f31aca19f` against `cf42f2a98`: identical), so the r4 fix covers Block 6 **if the L9 base is at least r4** | S-14 not pinned | **New twist:** `campaign_log.jsonl` is desk-compressed in five sessions, and `load_campaign_log_rows` reads a compressed log as **empty** (design §4.1, lines 233-236) | No floor binding. A D5-type refusal would show as a `floor_gate_j`/outcome mismatch, so it is caught | **Root lesson not carried** (see below) |
| D5b (refusal label) | L9 claim gate | — | r3 | — | Needs an L9 base of at least r3 |
| D6 (NEG-8 terms compared unconditionally) | Low: the Block-6 contract compares only allowance, bound and verdict | — | — | — | OK |
| Item 53 (r2-gamma `claim_usable:false`) | Real | — | Carried (design §4.5, B6-AN-1 A1) | Carried | **But** the program CANONICAL names still binds the block-5 catalog (`independent_recompute_b5.py:73`), the GAMMA midpoint reason (`:75-76,:720`) and the `claim_usable_false` flag (`:891-892`). It must never be pointed at Block-6 archives directly |
| FS3 tie rule (`RUN_STATE.md:588-594`) | Word flips at thresholds: R vs 2, "agree", LOO sign | — | — | Words are compared exactly ("Words, booleans and integers must be exactly equal") | **Not carried** |
| RC-CMP-8/9 "one-side-keyed" class (closed by a registry-driven expected-check table) | — | — | B6-AN-1 copies the recompute's key file | The contract is written by the lean's own `keys` command from a block run (`comparison_keys.json` `ruling`) | **Regressed** |
| Audit F4 (CSV fallback breaks independence) | Every raw plist is compressed | — | — | `trace_plist_missing` stops the run (`:419-428`; b6 `STOP_FLAG_CODES:91`). The restore tool it names, `scripts/restore_run_to_scratch.py` (`:87-88`), is **not on main** | Fails closed, but there is no working path |
| L9-ENV-3 inverted-corner clamp | Same frozen `reduce.py` bytes, so the same envelopes | — | — | The lean's `overlap()` already gives 0 J for an inverted window, which is equivalent to the clamp | Carried in the lean. **But** item 144 queues deleting L9's ~440-line mirror after the B5 release (`RUN_STATE.md:819-820`), and an L9 audit of Block 6 still needs it |
| Harvest stored its bracket with B5's acceptance (design §4.8) | All sessions | — | Design rebuilds b_op | Uses s_bracket 10.818 ms and checks the acceptance `operative_bound_s` | Carried |

**The root lesson of D5.** The synthetic chain resolved both floors (`release-hold-trace.md:92-93`) because its fixtures lacked the real runner's trailing whole-window evaluation row. Both Block-6 fixture sets have the same weakness:
- RC-B6-1's fixtures are hand-built (open issue 1: "not yet run on archives written by the real harvest").
- B6-AN-1 runs through a fake adapter.

Design §16's generator, which runs the real chain and harvest at `f31aca19f`, is the cure. It has not been built.

## 3. Are the estimands well defined?

1. **§9.5 item 3, T.** REG:1018 says "E and T are the cell's estimator-1 mean and mean phase length".
   - The design reads T as weighted 0.2/0.8 (design §6 item 3).
   - RC-B6-1 uses the plain mean over kept members (`independent_recompute_b6.py` ~560).
   - The two agree only for a complete cell, so they will disagree on any cell with unequal losses. Pick one.
2. **§9.5 item 3, E_ref/T_ref, "the surviving references that set the allowance".** When the bound term binds, the corpus sets the allowance. Both implementations use the start + midpoint + end references' *request* energy and length, so the text should say exactly that.
3. **S-13 is not operational**: "half a unit of its last printed digit" needs a printed precision, and three tables disagree:
   - `tests/independent_recompute/bar_sets/s13_block6.json:4` calls its own values PLACEHOLDERS (J 5 decimals, R 4, t\* 3, p 4).
   - Design §11 / D15 (lines 962-977): J 5, ratios 4, per-token 8.
   - RC-B6-1's `RATIFIED_COMPARISON_DECIMALS` (`independent_recompute_b6.py:1127-1135`): `*_j` 4, R and R_cm 2, factor 3, energy ratio 3, t 2, p 4.
   - The bars therefore differ by up to 100× (R: 5e-5 against 5e-3). The run set for "each run's phase energy" is also not registered (RC-B6-1 chose kept units, survivors and the clean corpus).
4. **§10 across blocks.** Block 5's b_op uses s_bracket 14.531 ms and Block 6's uses 10.818 ms (`REG:378-387`). The s_Q of the attribution and operative floors therefore carries a systematic offset of up to about 0.17 J, a design figure. §11.1 discloses the difference, but the §10 line does not. Label it, and print a Block-6-only summary beside it as a labelled line (no arithmetic change).
5. **§11.2.** "Replicated" is well defined but reads oddly when block 5's word is `unresolved` or `not_resolvable`. A wording note or labelled line would help (optional).
6. **S-15** (whole-machine per phase) is open. The only per-phase definition is in the lean program (design §8). The BAT-2 question, whether to put the battery inside the value, must be settled as meter-only, as REG:1030-1037 registers.
7. **J6 timing-bound sensitivity line** (an L9 ruling, not in REG §9.5). L9 run unchanged would print it; RC-B6-1 drops it (open issue 5). Rule it in or out.
8. **§8.3 item 3 and §8.5 lines are owed and unbuilt in every implementation:**
   - the E_add outside-processor alternative ("owed before the analysis release", `REG:651-654,793-799`);
   - the P* desk exclusion (`REG:655-659`, S-9). This one changes kept units. The lean takes kept units only from the acceptance record's `excluding` rows, so it does not apply a registered exclusion. No number moves on B6-2's replay, but the production path must evaluate it.

## 4. Is the recompute hash-independent?

- **Code.** The lean b6 program imports no `joulewise/` code, which is good. It records `b5_program_sha256` (`independent_recompute_b6.py:1105-1106`) but **does not pin it**. Any later change to the B5 script (for example the DLE-2 coverage additions) silently changes Block-6 arithmetic. Pin it to the digest that passes the Block-5 release check at `b5/analysis-r4`.
- **Inputs.** The lean authenticates nothing:
  - `Reader.raw` only reads bytes (`independent_recompute_b5.py:290-299`; `LEAN-COVERAGE-AUDIT.md:121`).
  - DLE-2's "bound by content hash to the harvest record" (DLOG:152-155) is in practice L9's step-0 census, verified by `release_b5.py` stage (a), which is Block-5-only.
  - With L9 off the critical path, the Block-6 production path must itself verify archive `SHA256SUMS`, the `harvest.json` and acceptance digests, and the desk-compression rows.
- **Kept units.** These come from the acceptance record with no re-derivation. The B5 lean re-derived them from flags and the catalog (`check_exclusions`, `:920-946`). Port that to the Block-6 catalog (`b5bce6c6…`, no pack-scoped reasons).
- **Comparator.** It lives inside the production file (`compare` subcommand) and its keys come from the production side. It should be a separate file with pinned bars, keyed by a registry of the quantities REG prints.

## 5. Does the release comparator cover every registered family?

**No.** RC-B6-1's contract (ALPHA/BETA 100 keys, GAMMA 89, 310 block keys) covers:
- §9.1-§9.4;
- §9.5 items 1-4, 6 and 8;
- §10, §11.1, §11.2 and §11.4;
- b_op, the NEG-8 allowance, bound and verdict;
- run phase energies.

It leaves out:
- **everything in §2's "Not carried" rows**, including the request-level whole-machine line (which held 4 of B5's 6 defects);
- the S-15 per-phase line;
- §9.5 item 7 (block-5 codes carried);
- the E_add and P* lines;
- the LOO rows and Holm order;
- p42 status;
- the idle-subtracted screen family;
- kept-unit positions.

Because the contract is generated from the lean's own output, "comparator passes" means "the two sides agree on what the lean computes". It does not mean REG §12.3 item 4's "every printed quantity". This is the same gap DLE-1 accepted for Block 5 "only" (DLOG:111-128), now carried into Block 6 without an entry.

## 6. Will the analysis run fast?

- **Lean b6, as built, is serial.** It has no `MemberPool` (the B5 script has `--workers`, `:3161-3165`).
  - Block 6 has about 1,071 members, roughly 3.4× Block 5's 316.
  - The care audit estimates the B5 lean at 25-65 min serial and 5-8 min with the pool (`docs/run_reports/2026-11-06-b5-care-audit.md:171`).
  - Scaled up, Block 6 is about **1.4-3.7 h serial and about 17-27 min pooled**.
- **Compressed bytes.** Every raw plist is `.zst`, and today the lean stops on them.
  - This Air has 10 cores, 24 GB of RAM and **66 GiB free** (`df -g` today).
  - A session is 32.75-38.82 GiB plain (design §1), so a plain restore of more than one session does not fit.
  - Python 3.14's standard library has `compression.zstd` (checked: importable on `/opt/homebrew/bin/python3` 3.14.6, absent on 3.13). Streaming the `.zst` files with a SHA-256 check against the desk record keeps the lean standard-library-only, writes nothing into session directories (which removes audit F1's "only physical copy" risk from the analysis) and needs no restore tool.
- **The L9 audit as designed** runs 6 floor units and 3 GAMMA units, each GAMMA unit covering 3 sessions. That is about 15 session-passes against Block 5's 3.
  - If cost scales with sessions, that is about 5 × 100 min ≈ 8 h per pass.
  - B6-AN-1 runs each phase twice (lead item 4).
  - REG §13 adds a release re-run (`REG:1186-1188`).
  - With 9-15 APFS restore cycles on top (unmeasured), the total is **about 16-25 h**.
  - Three changes would bring it to about 3-5 h, off the critical path: reuse floor-session steps 0-4 across units (D-188 result equivalence), drop the repeats (DLE-1's reasoning) and run units in parallel.

## 7. Amendments to make before the Block-6 release (blind, REG §12.4)

Each item is a dated REG §17 entry with one executing refuter unless marked otherwise.

1. **Framing entry.** Record that Block 6 is collected and blinded, that these entries are made under §12.4 before release, and the signer's statement (no B5 or B6 outcome seen).
2. **DLE-2 for Block 6 (owed, DLOG:167-168).**
   - Name the production program by path and digest (the merged `independent_recompute_b6.py`) and pin the B5 lean digest.
   - Redefine §12.3 items 3-4: what "analysis programs" and "independent recompute" now mean, and what the second side is.
   - Disagreement rule (CARE §2.5 item 3): a hold, decided by the defect found.
   - Release while the audit is unfinished: **hold** (DLOG:189-191).
   - The disagreement surface includes strict refusals.
   - Restate the "first counting block-6 session" agreement gate (DLOG:177-179), which cannot be met without a second side.
3. **DLE-1 for Block 6.** Replace §13's release re-run ("every output digest must equal the dry run's", `REG:1187-1188`) with a re-verification of the dry-run digests plus an input census. Drop the determinism repeats.
4. **Complete S-13.**
   - One printed-precision table, pinned by digest: the strictest value per family from the three tables in §3.
   - The run set for run energies.
   - The FS3 tie rule.
   - Coverage defined as a registry of REG-printed quantities, with unmatched or absent keys failing closed.
5. **Coverage entry.** For each of the 7 DLE-2 families, the §9.5 preamble disclosures, the request-level whole-machine line and §9.5 item 7, either:
   - (a) computed by production and compared; or
   - (b) "copied from the harvest or acceptance record, bound by digest, not recomputed", with the RS item 83 ruling 3 hand check.

   Under proportionate care, (b) is fine for count-type disclosures.
6. **Slot fills.**
   - Merge S-9/S-11 (`c37614f71`).
   - S-14: for any L9 use, a base at or after `b5/analysis-r4` (D1, D5b, D5), plus the GAMMA pack-file estimator-1 fix.
   - S-15: the meter-only definition of design §8, labelled as a single-implementation descriptive line (or name a second implementation).
   - S-16: schedule it after the B5 release.
7. **Estimand text.**
   - §9.5 item 3: the T weighting and the E_ref/T_ref basis.
   - §10: label the floor offset and add a Block-6-only line.
   - J6 line: in or out.
   - §11.2 wording (optional).
8. **§8.3 item 3.** Production implements the E_add alternative and the P* desk exclusion, including GAMMA's per-model P* alternative.

Code preconditions (not registration text, but they gate the release):
- **C1.** `.zst` streaming plus input authentication.
- **C2.** Member pool.
- **C3.** Re-derive Block-6 exclusions in the lean.
- **C4.** Real-chain fixtures at `f31aca19f` covering: waited runs with attempt-N telemetry, wait-cap skips, members with unresolved anchors, campaign logs with trailing whole-window rows, and compressed campaign logs.
- **C5.** Keep the L9-ENV-3 mirror until any L9 Block-6 audit has run.
- **C6.** `CANONICAL.md` rows for the Block-6 tools; delete superseded lanes.
- **C7.** A `release_b6` wrapper (the analogue of stages a, b and c).

## 8. Recommended shape (lead's ruling; proportionate)

Building the L9 Block-6 seam (design §4.2: ~40 binding sites, 5 frozen-file merges, an hours-long equivalence replay) only to obtain an audit is the expensive path. Two independent twins already exist on `main` and could serve as the second side for the Block-6-specific layer:
- `joulewise/twins/harvest_twin.py`: §1.7 `calibration_bracket` and §1.8 `session_drift`;
- `joulewise/twins/engine_twin.py`: GAMMA §9.4, written from REG §9.4.

The cheaper path:
1. The lean b6 program is production, pinned to the B5-release-validated arithmetic.
2. The second side for the Block-6 layer is the two twins plus a small stdlib checker for counting, pairing and §10/§11.
3. The per-run reducer cross-check (`stored_energy_mismatch`) is promoted to a gate. It is a second parse of the same raw plists.
4. The L9 Block-6 audit becomes optional, recorded as a §17 deviation.

**What this costs:** a second derivation of the collection-time judgments (DLE-2 open point 1). Re-deriving exclusions (C3) and the reducer gate reduce that loss.

## 9. Evidence and method

- I read REG in full, DLOG, `LEAN-COVERAGE-AUDIT.md`, the release-hold trace, the care audit §2.5, the `RUN_STATE` items listed above, the design, the B6-AN-1 and RC-B6-1 reports, the S-9/S-11 diff (digits masked), and the code cited.
- **Ran:** on `main` `ca2d1ee97`, with the four RC-B6-1 files from `74a4f8123` overlaid, `tests.independent_recompute.test_block6` under `nice -n 19 taskpolicy -b`, `JW_B5_SYNTHETIC_ONLY=1`, python3.13. Result: **26 tests OK in 62.2 s**. So the b6 wrapper still works with today's B5 script, but only on the hand-built fixtures.
- **Not verified:** Block-6 structure counts (how many waited runs or unresolved anchors); where the session bytes live and whether a second copy exists; real-data runtime.
````
