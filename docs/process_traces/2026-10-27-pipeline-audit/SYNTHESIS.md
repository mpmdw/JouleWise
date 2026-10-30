> **Status: PROPOSALS, NOT ADOPTED.** Read-only audit (workflow wf_0ae9b90a-b4b, 23 agents) for Ed. Nothing here binds until Ed decides; see CRITIQUE.md beside this file, which corrects several items.

# JouleWise: from measurement to released numbers, made faster

For Ed. Written 2026-10-27, about 13:00 PDT. Read-only synthesis of seven segment maps, each checked by a science skeptic and a cadence skeptic. I read no measurement data.

**How to read the citations.**
- `jw:` is `scratchpad/jw` (main). `l9:`, `bytes:` and `recompute:` are the matching `scratchpad/wt/*` worktrees. `scout:` is `scratchpad/wt/scout/.codex-report/BLIND-DRY-RUN-SCOUT.md`. `b6design:` is `origin/lane/2026-10-22-b6-analysis-design:docs/design/b6_analysis_additions.md`.
- "RS n" is `jw:RUN_STATE.md` item n.
- `[seg ID/sci]` and `[seg ID/cad]` point to a step in a segment map and to the science-skeptic or cadence-skeptic finding on it. Segments: collect, b5, recompute, b6, bytes, gov, outcomes. "E01-E25" are rows of the outcomes ledger.
- **(V)** means I re-read those lines myself in this synthesis. Every other citation comes from the segment maps, whose skeptics read them. **INFERRED** means nobody read it.

## Bottom line

1. **The biggest loss of collection time in October was agents on the measurement Mac, not the science checks.** Each census hit was a real contaminant. Together they cost about 15-20 h of quiet-Mac time: BETA a2, BY-H2's 9.5 h idle, s6-p1's 276-min chain, and two machine-test installs (E02; overlap INFERRED). Moving every agent to the Air or the cloud costs no code and fixes this.
2. **The Air can take block 5's blind dry run and the recompute off the Mac. You have already permitted this** (ED-RULING item 6b, `jw:docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:75-80` (V); `BLOCK5-TRANSFER.md` (V)). Its deadline check is running on the Air now: `tests.b5_analysis.test_dry_run` at 60473bee, pid 53226, Python 3.13.18 (V). The Air is a Mac16,13 (Apple M4, 24 GiB) with 198 GiB free on macOS 15.7.9 (V, `sysctl`/`df`/`sw_vers`). The recompute map's "41 GiB free" is out of date; RS 79 says about 200 GiB (V). I add five conditions the skeptics showed are needed (§2, ED2). With them, BYTES never has to pause for block 5.
3. **Nothing about the harvest moves off the Mac.** Two findings rule it out. On a host without the BYTES key, `_stored_or_draw` silently draws a new blinding factor (`bytes:joulewise/b6/blinding.py:88-134` (V)). And a deadline firing during re-reduction turns into a registered member exclusion, not a fault [collect C19/sci].
4. **Reviews get faster without losing protection.** Run the two-family executing passes in parallel and early. Write down when delta rounds stop. Replace the block-5 step-12 cold gate with a comparator plus one executing seat. Run the determinism rerun blind, before the release event. Every first-round number catch in October came from executing seats (E13, E14). No lone cold judge caught a W-class defect (outcomes E17; PL OP-3).
5. **BYTES is marginal against 2026-11-02.** Eight sessions are needed and about 13 slots remain if the Mac is never held. Pass 1 lost 2 of 6 attempts (INFERRED arithmetic, §5). Run s1-p1 next, flip pass 2 to registered today, and extend the end date by 3 days, blind (decision 5).
6. **Estimates (INFERRED):** block-5 numbers about 11-01, BYTES stage 2 about 11-02 to 11-03, block-6 numbers about 11-03 to 11-05.

---

## 1. The pipeline in one table

| Stage | What it protects | Current cost | New cost | Runs on | Verdict |
|---|---|---|---|---|---|
| Machine test (per collection-code change) | Collection defects that lose or miscount runs. October: 2 A, 2 B catches (E05) | 40-70 min Mac per change (E05) | Same for collector, driver, controller, smoke-prepare and launchd changes. Desk-only changes are checked by replaying stored archives (PR-4) | Mac (live); Air or cloud (replay) | KEEP, narrower trigger |
| Pre-arm checks, PRECHECK, agent census | Physical contamination: mediaanalysisd, a throttled sampler, agents (E01-E03; RS 46-47, 67) | About 5 min twice per cycle. Agents on the Mac cost about 15-20 h in October (E02) | Checks unchanged. Agents removed from the Mac (ED1) | Mac | KEEP; remove the cause |
| Smoke and smoke desk | Structural failure of a new pack. October record: 0 catches, 1 false hold, missed s1-p1 (E04) | About 50 min per session (c634f6f3 RECORD:41) | Unchanged for BYTES pass 2: registered at `bytes:docs/registrations/bytes_pack_v1.md:450` (V), and the p2 trees are new [collect C4/sci]. Fixed to read committed bytes after BYTES (PR-9) | Mac | KEEP for BYTES; fix afterwards |
| Session chain | The data | 313-388 min | Unchanged | Mac | KEEP |
| Harvest and desk | Registered exclusions, provenance, the blinding key draw | 88-101 min plus about 7 min of desk | Unchanged | Mac | KEEP on the Mac |
| Attempt line, verdict mail, magistrate | Your awareness; handling of anomalies | 1.5-2 h of agent time on the Mac per session, plus a duplicate email (collect C17) | Loop mail only. Magistrate wakes only on exceptions, runs off the Mac, never polls into it | Mac (loop); cloud or Air | MERGE |
| Package and transfer (new, ruling 6b) | Copies hash-verified file by file | n/a | About 0.5-1 h of Mac at a desk, by script, not an agent (INFERRED) | Mac script, then iCloud, then Air | ADD |
| L9 code acceptance | Analysis code correctness | Review, then 2 cold passes in series. A full-size run takes about 6 h | Six modules; one cached full-size run (running on the Air now); one parallel two-family executing stage that counts as both review and cold passes; CI | Cloud, Air | LIGHTEN (ED3) |
| 9b fail-closed evidence | A deadline firing cannot change a kept unit (ED item 6 condition) | Waiting for a natural firing | Per-site fault injection, hours | Cloud | MOVE EARLIER |
| Block-5 blind dry run | End-to-end on the real bytes, blind | Mac, holding BYTES about one slot (ED item 6a) | Air under 6b, with the cache | Air (Mac fallback) | MOVE (ED2) |
| Block-5 determinism | Reproducible numbers | A full rerun after the release, on the path to numbers (`jw:configs/campaigns/v5_claim_25g83/analysis_plan_block5.md:194-195` (V)) | A second blind run before the release event | Same host, same paths | MOVE EARLIER (B5-1) |
| Independent recompute and comparator | Arithmetic checked by independent code | Comparator does not exist [b5 R2] | Built now on synthetic outputs; run after the dry run, never beside it | Cloud (build); Air (run) | BUILD |
| Step 12 results cold gate | Wrong printed numbers | Judge plus refuter, days (`jw:docs/design/analysis_cadence_plan.md:16`) | Comparator plus one executing seat, hours | Cloud, lead | LIGHTEN (B5-2) |
| Block-6 build and review | Pairing, replication word, summaries | Full-size synthetic run per round; serial review plus 2 cold passes | One known-answer full-size run plus one parallel two-family stage | Cloud | LIGHTEN (§17) |
| Block-6 real runs | End-to-end and determinism | Scout serializes everything after block 5's release (scout:12) | Both blind runs before block 5's release; only the cross-block phase after it | Mac after BYTES, or Air after block 5 | MOVE EARLIER |
| BYTES pass-2 gate | Registered estimators for p2 | Two-seat cold gate plus a Mac suite run: about 1 day plus 1.5-2.5 h (bytes C9) | Generator, one executing check, CI | Cloud, then one cherry-pick | LIGHTEN (BY-2) |
| BYTES known-bytes test | Caveat lines | Runs before stage 1 | Order unchanged; prints "not measured" if it misses its slot | Mac quiet gap | KEEP |
| BYTES stage 1 to stage 2 | Commitment before held-out unblinding; independent twin | Unmeasured | Adds a kept-unit guard, DC/rest agreement before the commitment, and a pool sized by measurement | Mac, idle after collection, keys local | KEEP plus guard |
| Reviews, CI, councils | Code and science judgments | Serial rounds; CI shard 10 takes 94-150 min (E10) | Parallel stages, a stopping rule, a split shard | Cloud | LIGHTEN (§3d) |

---

## 2. Adopted changes, by authority

Every item below either drew no unrefuted failure mode from the science skeptic or was modified to close the one it drew. Each gives the change, what still protects the science, the saving and on which path, and the evidence.

### 2.1 No authority needed (new checks, seat launches, or byte-identical speedups)

- **N1. Shared physics_cache through the whole dry-run path, including the 9b archive replay.** This is non-governed code: `whole_window.py:407-412`, `cli.py`. It landed in L9-2 at b5df45ab and 60473bee (RS 79, V).
  - *Protects:* the cache is keyed by the evidence SHA-256, consulted only after the hash checks, and stores successes only (`l9:joulewise/cli.py:462-468`; `reduce.py:1526-1594`) [b5 P2/sci]. A cache hit cannot fire the deadline. Modified per the science skeptic: test byte-identity on a fixture where the uncached arm does not itself hit the deadline.
  - *Saves:* most of the 82 identical refits, which took 594 s of the first 941 s (`l9:.codex-report/L9-2.md:139-140`). The saving over a whole run is unmeasured; today's Air run will measure it. Path: block-5 dry run, its rerun, and block 6.
- **N2. Process pool for dry-run steps 1-2: defer for block 5.** A deterministic pool or cache bug is seen only by a fixture serial-versus-parallel test and a full-size synthetic run. Release digest equality compares two pooled runs and cannot see it (E20/sci). Today's full-size run does not include a pool. So: if today's cached run shows steps 1-2 fast enough, run block 5's first dry run without the pool. Add the pool later with workers ≤ P-cores (4 on the M4), serial cache warm-up, and one new full-size run. Saves an extra full-size cycle now.
- **N3. Per-site 9b fault injection.** This is ED item 6's condition (`ED-RULING.md:65-67` (V)), and L9-2's report still says "Step 9b: NEEDS_RULING" (`l9:.codex-report/L9-2.md:9` (V)). The science skeptic modified the method:
  - inject per site, from step N onward, on uncached NEG-8 references;
  - patch the clock or the function, because the deadline is a default argument bound at definition (`powermetrics_fiducial.py:497,918`);
  - list every caller of the strict-invalid predicate whose `unlisted_strict_invalid` can be `'read'` (`whole_window.py:5412,5606`);
  - assert that each case gives a refusal, never a dropped survivor [b5 P5/sci].
  - *Saves:* the wait for a natural firing, and it makes host speed a time cost only, on the Mac or the Air. Cloud, hours.
- **N4. S11 index generator** (`configs/analysis/b5/analysed_windows.json`, still absent on L9-2). Validated by `load_window_index`, followed by one lead diff against the RUN_STATE attempt history, committed before the dry run. The absolute roots must be identical to the Mac's (ED2) [b5 P8/sci].
- **N5. FILL and L9-pin addendum script.** It fills from the reviewed L9 tag and refuses if the dry run's `analysis_commit` differs from that tag [b5 P9/sci]. The lead reconciles "eleven open markers" (SEAL_RECORD:300) against the 13 FILLs of plan §13 (`analysis_plan_block5.md:776-779` (V)). Saves hours of hand drafting.
- **N6. Recompute-versus-L9 comparator, built blind now in the cloud on synthetic outputs.** Requirements [recompute R15/sci; b5 R2/sci; outcomes E22/sci]:
  - numeric families at the bars of B5-4;
  - exact-match families for outcome words, dominance branch, p42 status and Holm order;
  - a value missing or null on either side counts as **disagree**;
  - it refuses unless every step-11 fill or placement is mapped or explicitly listed as uncovered;
  - planted-fault tests per family, in the F4/F12 pattern;
  - before the release it posts pass/fail counts only.
  - *Saves:* the release cannot be evaluated today without it.
- **N7. Recompute hygiene:**
  - stdout prints STRUCTURE codes only. Today it prints every flag code, including science-derived pass/fail codes (`recompute:scripts/independent_recompute_b5.py:58-63,2638-2655`) [recompute R14/sci].
  - a stdlib re-derivation of member exclusions from `flags.jsonl` through the registered catalog, a partial AN-18 that catches consumer and mapping errors [recompute R5/cad];
  - record the interpreter version;
  - run the recompute plus the comparator on today's synthetic `test_dry_run` window, so coverage gaps surface blind [b5 cadence missed item].
- **N8. Release-event drafting script** from the seal-record digests, the index and the dry-run record. The lead dates and commits it under the condition of decision 4 [b5 R3].
- **N9. Block-6 pure layer.** Counting consumer, pairing, §10/§11 and the structure-only record continue in the cloud. A first driver against a fake L9 adapter is already pushed (3710aa2c, a1097e20; RS 79 (V)). Reissue the B6-AN-1 brief to cite b6design §4-§14 and §17 and to drop S-9/S-11, which B6-2 already filled [b6 B6-02, B6-05].
- **N10. Block-6 independent recompute adaptation, in a separate seat.** Requirements [b6 B6-10/sci; recompute R16/sci; b6 B6-10/cad]:
  - pairing hard-coded from the registration: G r1 ← A r1, B r1; G r2 ← A r3, B r2; G r3 ← A r3, B r3;
  - counting re-derived from the acceptance records, not from the driver's index;
  - its own reader (`desk_compress.read_bytes`) with a digest check;
  - §10 and §11, including the replication word with its same-sign-of-dbar condition, the flagged-inclusive line and the S-15 line.
  - *Saves:* keeps the block-6 check off the path after block 5's release.
- **N11. BYTES: a sub-pack that never counts.** Run one synthetic campaign with s1 absent from both passes and one with s6 absent, through the CLI and the twin. If they refuse, add CLI-only census placeholders. Any change to `bytes_analysis.py` goes through BY-amendment instead [bytes A1/sci]. Saves a possible multi-day stall at stage 2.
- **N12. BYTES timing and silent-drop check on the Air.**
  - Time re-reduction on a subset of the non-claim H/BY-H2 archives at the planned pool width, and record headroom against 120 s.
  - Separately, force a firing on a synthetic bundle. The code path is verified: `AnalysisError` subclasses `ValueError` (`bytes:joulewise/bytes_analysis.py:46` (V)), and the broad except at `:1016-1017` (V) turns the row into `unusable`. Whether a firing actually produces `status != succeeded` is INFERRED until this runs [bytes A4/sci, A5/sci].
- **N13. BYTES CLI guard** in `scripts/bytes_analyze.py`, which is not digest-pinned; only `bytes_analysis.py` is (`bytes_pack_v1.md:361,384` (V)). Refuse to write predictions or stage-2 output if any selected row is unusable for a re-reduction reason, or if the analysis's kept units differ from the acceptance kept set. A session pool comes only after N12, with width taken from N12 [bytes A5/sci, A11/sci].
- **N14. Known-bytes v2 probe, chain extension and Δ code** in the cloud, integrating through the same reducers as pass 1 [bytes C12/sci].
- **N15. CI.** Split shard 10; add a shard-coverage assertion; keep the quarantined contention job required [gov G08; outcomes E10/sci].
- **N16. Pruning tally as a fixed table** with `caught_number` and `caught_session_refusal` columns, plus a collector script [gov G28/sci].

### 2.2 Lead ruling

- **L1. s1-p1 before the s6-p1 retry.**
  - *Why:* `freeze_lines` needs exactly 3 fit points (`bytes_analysis.py:89-90`). Without s1 there is no `predictions.json`, so stage 2 cannot run either [bytes C7/cad]. s1-p2 is last in base order (`bytes:configs/b6/loop_bytes.json`), while s6-p2 is first.
  - *Saves:* the fit set gets two chances instead of one, last-slot chance.
  - If s6-p1's retry has already passed PRECHECK, run s1-p1 right after it. The loop's retry mechanics are INFERRED.
- **L2. Override item 78's pointer** ("p2 after the fit set") so the pass-2 flip (BY-2) lands today [bytes C9/cad].
- **L3. Block-6 integration base:** main + L9 + 1706257c, **plus** #573's block-6 reader corrections (903b5a2f, db9e8ab3, `desk_restore.py`, `restore_run_to_scratch.py`). Not 1706257c alone, which lacks them; the analysis's own steps 1-2 run those readers [b6 B6-01/sci]. Regenerate `registry.json` and `hazard_refusals.json` with their tools, and add the block-5 equivalence test (5 frozen-file digests, b6design:1154-1163).
- **L4. Merge B6-2 (S-9/S-11)** (`origin/lane/2026-10-22-b6-s9-s11` c37614f7). Add a structure-only test that the consumer's desk-exclusion count equals B6-2's recorded "0 of 840" [b6 B6-05/sci].
- **L5. Block-6 counting comes from loop acceptance** (the r2-gamma fix, RS 53). The release record mechanically requires analysis counting to equal acceptance counting for all 9 sessions [b6 B6-04/sci].
- **L6. Fix rounds may resume from the first changed step,** reusing content-addressed outputs keyed by the **full analysis-tree digest**. The registered record is one complete clean run [b5 D1/sci; b6 B6-15/sci].
- **L7. BYTES DC/rest agreement on the fit configurations runs before the stage-1 commitment.** The registration's "after each release" allows that order. It is the only real-data check that can see a re-reduction-driven fit-set change before predictions freeze [bytes A6/sci].
- **L8. Meter clock-fit method ruled blind now: choose the fit, never widen the bar.** The known difference is 0.020 J against a 1.24e-4 J bar (recompute commit 7e322b76). The ruling feeds S-15 and block 5's machine line [recompute R12]. Saves a certain release-day refusal.
- **L9. Known-bytes reading rule.** One blind executing delta pass scoped to the reconciler's CHANGES rows, reproducing §5 with its own script, then bind [bytes C11/sci]. It is off the critical path.
- **L10. Fallback local Sol seats run on the Air, never the Mac** [gov G22]. Seat scratch once pinned 53 GiB on the Mac (7209d1b0 RECORD:100-104).
- **L11. Scope grants.** Grant module, tests and registries up front. Fence tightly the estimator files **and** every registered pack, catalog, flag_effects, sizing and registration file of blocks 5 and 6 and BYTES [gov G01/sci].
- **L12. Physical-cause councils start with a deterministic structural locate,** as M1 did on s5-p1 (a46602ae RECORD:6-8) [outcomes E18/cad].
- **L13. Block-5 ledger.** Check whether anything still appends to the -b5 checkout's ledger (dry_run.py:555-558 hashes it live). On the Air the copy is frozen; record its SHA in the transfer manifest [b5 S0, P8].
- **L14. Correct "2026-11-02 00:00 PDT"** in ED-RULING 6a (V, line 72) and RS 77 to the registered `2026-11-02T00:00:00-08:00` (`bytes_pack_v1.md:105` (V)). On 11-02 the zone is PST, so "00:00 PDT" would be one hour earlier.

### 2.3 Ed ruling (adopted, pending your answers in §7)

- **ED1. No agent on the measurement Mac** (decision 1). Evidence: E02, RS 16, RS 67, RS 78; a46602ae RECORD:4-7.
- **ED2. Activate ruling 6b** for block 5 (decision 2), with five conditions added to `BLOCK5-TRANSFER.md`:
  - (a) N3 per-site fail-closed evidence, which ED item 6 requires anyway;
  - (b) the data unpacked at the **same absolute paths** as on the Mac (your user is `edr` on both), using APFS transparent compression if space is short (INFERRED: readers unaffected);
  - (c) **one heavy job at a time on the Air**, with the recompute after the dry run, never beside it [b5 S9b/cad];
  - (d) the restricted folder readable only by a separate non-agent macOS account (decision 6);
  - (e) packaging on the Mac by a committed script triggered at a desk, not by an agent. The file now says "the orchestrator on the measurement Mac does" it (`BLOCK5-TRANSFER.md:19` (V)).
  - Also add **BETA a1/a4/a5** to the package. The recompute's BETA-inclusive labelled line needs them (RS 37; recompute R11), and the transfer file excludes superseded attempts (`:34` (V)).
  - *Saves:* about one BYTES slot (about 10 h), and block 5 no longer waits for BYTES gaps.
  - *Science still protected:* a firing costs time, not numbers, given (a). The determinism check runs on the same host and paths. Blinding is enforced by account permissions.
- **ED3. L9 gate amendments** (decision 3):
  - the Fable and Opus executing passes, carrying a probe-and-mutation mandate, launch together now and count as item 1's executing review and item 3's cold passes;
  - any later number-bearing L9 commit gets a delta pass from both families;
  - drop `test_docs_freshness` from item 1;
  - replace item 4 ("reduced fixture", infeasible per `l9:.codex-report/L9-2.md:131-138`) with B5-1 [gov G04/sci, G23/sci; b5 P4/sci].
  - *Saves:* one serial seat, and takes the cold passes off the dry-run-to-release path.
- **ED4. Release condition with no extra cold gate** (decision 4); covers the scout's added gate (scout:132,206).
- **ED5. BYTES end date plus 3 days** (decision 5).
- **ED6. Custody on the Air** (decision 6).
- **ED7. Orchestrator placement** (decision 7).
- **ED8. Delete the four-model council text** (decision 9) [gov G15].

### 2.4 Block-5 plan amendment (prospective cold erratum plus seal-record addendum; text in §3a)

The route is a cold erratum because items 3 and 4 below are a blinding change (a new pre-release reader of restricted paths) and a threshold. Registration §10 says those take "one judge, one refuter" (`registration_block5.md:5144-5146` (V)). Plan items 1, 2 and 5 ride in the same erratum. The plan's own bytes are not edited (plan §13, `:779-783` (V)).

- **B5-1. Determinism before the release event.** A second complete blind run in a fresh custody root, on the same host and absolute paths, run after the first, never beside it. Every output digest must match. After the release the lead reads only digest-verified outputs.
  - *Why:* the release-mode run does not check for a release event (`l9:joulewise/b5_analysis/dry_run.py:1088-1218`) [b5 R4/cad]. Reading numbers before determinism is established breaks the safety argument for ruling (c) [b5 R4/sci].
  - *Saves:* one full analysis run (hours) between the release event and the numbers, and shrinks the ledger-drift window.
- **B5-2. Step 12 becomes the comparator plus one executing seat** with no prior L9 involvement. After the release event the seat:
  - (i) runs N6;
  - (ii) re-derives the recompute-only labelled lines: both GAMMA scaled-allowance contrasts, and one cell of each other line, including the BETA-inclusive branch above 16 units;
  - (iii) checks every rendered fill against its issued value: rounding, units, labels, outcome words, placement. Evidence for why: C66 printed 2.8011 for an estimate of -2.8011 (PL:455);
  - (iv) confirms N7's flags-to-catalog re-derivation matches `exclusions.json`.
  - *Saves:* 1-3 days after the release (cadence plan:16; #416's cadence) [recompute G1/sci; b5 R5/sci; outcomes E22/sci].
- **B5-3. The independent recompute is a pre-release automation reader with structure-only public output.** Today's custody map names only the harvest, the dry run and the scheduler (`registration_block5.md:4895-4897` (V)).
- **B5-4. Release tolerance.** S-13's bars (1 mJ per run phase energy; half a unit of the last printed digit, unrounded, with the observed difference printed beside it) plus exact match for categorical outputs. This fills RS 37's "tolerance fixed before release".
- **B5-5. Release condition:**
  - the dry run complete with no tooling refusal;
  - B5-1's digests equal;
  - the comparator agrees;
  - both cold passes cover the final pin;
  - a mechanical check that the dry-run commit equals the reviewed tag;
  - no other gate.

### 2.5 Block-6 §17 entry (one entry, one executing refuter; text in §3b)

| # | Change | Still protects | Saves |
|---|---|---|---|
| B6-1 | Synthetic testing becomes fixtures with registered member counts and raw files of 1 MiB or more, plus **one** known-answer full-size run on the release candidate | Only planted truth catches scale-dependent kept-unit errors, which the recompute cannot see because it takes exclusions as input [b6 B6-07/sci] | 6-12 h per fix round |
| B6-2 | Review plus two cold passes become one parallel Fable+Opus executing stage with a mutation mandate. It may run beside the blind run and finishes before the release record. Delta rounds follow the gate policy, with no hard cap | Two families; #416 rounds 4-6 found real HIGHs, so a cap is unsafe [b6 B6-09/sci] | 1-2 days of serial rounds |
| B6-3 | S-14 is block 5's release tag plus the additions. An early pin is allowed only with a re-pin on **any** L9 change and a release-record check | Code identity [b6 B6-11/sci] | Allows an overlap if needed |
| B6-4 | Second full per-session blind run before the release, same host, run after the first. Digests bound before opening. After block 5's release only the cross-block phase runs, twice | Determinism [b6 B6-15/sci,cad] | One full block-6 run after the release |
| B6-5 | S-16 runs where block 5's raw bytes are and lists its raw inputs. A rule it cannot evaluate prints "not evaluated" | No silent zero [b6 B6-17/sci] | Folds into one invocation |
| B6-6 | Custody roots extended to the analysis host at identical paths, under a non-agent account | Bindings name absolute roots (b6design:287-293) [b6 B6-12/sci] | Lets the Air run block 6 if it is free first |
| B6-7 | S-15 filled (design §8, meter only, fit per L8) | WHAT is printed fixed blind | Removes S-15 from the pin's critical path |

### 2.6 BYTES registration amendment (Addendum 10; text in §3c)

- **BY-1. End date:** `end_t0_before` becomes 2026-11-05T00:00:00-08:00 (decision 5).
- **BY-2. Pass-2 gate.**
  - The generator emits the p2 packs as registered, with estimator versions = `18582818…`, and recomputes the sizing, clock and disk rows.
  - Remove the stale p2 `draft_notes`.
  - Requirements: `--check`, CI sidecar and tree-selection tests, and a cherry-pick verified by tree equality.
  - One executing reviewer, no two-seat cold gate. No suite rerun on "the laptop" (which per `bytes_pack_v1.md:103` (V) is the measurement Mac), because only JSON and sidecars change.
  - The p2 first-session smokes stay (`:450` (V)) [bytes C9/sci,cad].
  - *Saves:* about 1 day, and the difference between pass 2 starting 10-28 or 10-29.
  - Land it as **one** measurement-checkout commit at a desk: each commit changes `code_commit` and forces smokes (`fingerprint.py:42-43,75-99`) [bytes cadence missed item].
- **BY-3. Priority, declared before anyone sees any p2 output.** Applies only if the date binds:
  1. any pass-1 sub-pack still not counting;
  2. s5-p2;
  3. s1-p2 and s2-p2 (fit set);
  4. s6-p2, s3-p2, s4-p2.
  - The science skeptic moved the fit set up: its pass difference guards the committed lines [bytes C10/sci].
- **BY-4. Thermal labelled alternative.** The registered rule stays primary for every model and pass. Beside it, for **every** model in both passes, print a labelled line in which a `thermal.os_level_nonzero` episode excludes a unit only if it overlaps the decode span. It is computed outside `bytes_analysis.py` and checked by the twin. Collection for s5-p2 is unchanged, because M1 shows no wait would save a unit (a46602ae RECORD:8). Applying it to every model closes the "model-specific post-hoc rule" objection [bytes C8/sci].

### 2.7 Governed-code reissue

- **GOV-1. The deadline fix,** option (a), plus the calibration-acceptance reissue: one governed change **after** block 5's first dry run (cadence plan §2.4). It makes off-Mac analysis routine. Not on the critical path.
- **GOV-2. At the next block's code freeze** (number-bearing collection code, executing review, re-pin; `bytes:joulewise/b6/registration.py:22-28`):
  - a controller **absent** sidecar becomes a flag, while a digest mismatch stays a refusal [outcomes E08/sci];
  - a cooperative stop between stages, only when the zero yield is session-wide or the stage is the reference corpus [collect C15/sci; outcomes E07/sci].

### 2.8 Process-rule change

- **PR-1.** The gate policy in §3d.
- **PR-2. Loop improvements, batched after BYTES collection closes, with one machine test** [collect C0/cad]. No loop code changes mid-pass-2: every pass-2 session smokes anyway, the notice already overlaps the smoke (`bytes:joulewise/b6/loop.py:321-328,489`), and mid-collection tooling surprises cost s1-p1. The batch:
  - drain non-waiting states in one tick (C1; first measure the `since` stamps);
  - send the notice during the previous desk, carrying predicted flags and thin-margin by a follow-up mail (C5/sci);
  - an immediate zero-yield **alert** with no automatic stop (C15/sci);
  - a light first pre-check (C2/cad, unreviewed by the science skeptic, ≤5 min).
- **PR-3. A committed replay harness** (old-versus-new over every archive on disk) with a hard structure-only mode for any archive under withheld custody [outcomes E06/sci].
- **PR-4. Machine-test trigger.** A live run only for collector, driver, controller, smoke-prepare or launchd changes; it also installs the loop's own plist and runs one BYTES pack from committed bytes. Desk and harvest-only changes are checked by PR-3 on stored machine-test archives [outcomes E05/cad].
- **PR-5. TIER-01.** First attribute October's post-merge defects (MT1, MT2, s1-p1 sidecars, `cell.below_minimum`) to their PRs' tiers, then record the overdue day-30 decision. The defect log is empty and unmaintained, not a count of zero (`jw:docs/process/tier01_defect_log.md`) [gov G10/sci].

---

## 3. Draft amendment texts (ready to commit after the named checks)

### (a) Block 5: cold erratum appended to the seal record

The registration requires this form, quoted:

> "A rule, threshold, catalog effect, roster or blinding change is a prospective cold erratum (one judge, one refuter), settled in one erratum." (`jw:configs/campaigns/v5_claim_25g83/registration_block5.md:5144-5146` (V))
>
> "A **cold erratum** is a change to a sealed document made this way; it is **prospective** when it is made before the bytes it governs exist." (`:566-567` (V))
>
> "It is written as a named section appended to the seal record … The analysis plan is read by no program. If a value is filled into it after the seal commit, its SHA-256 changes, and an addendum to the seal record states the new digest." (`:5682-5687` (V))

```markdown
## B5-ERRATUM-R1 (prospective cold erratum, 2026-10-2X): release ordering, results check, recompute custody, release tolerance

**Made blind.** Drafted, judged and refuted before the release event and before any block-5 analysis output exists.
No author, judge or refuter has read a block-5 energy, power, duration, a RESTRICTED flag count, or any path that
registration §8 restricts. Judge: <seat, ruling path>. Refuter: <seat, ruling path>. Settled in this one erratum.

**Route.** Registration §10 (one judge, one refuter) for items 3 and 4, which change a reader of restricted paths and
a threshold; items 1, 2 and 5 change how the analysis plan's steps are ordered and checked and ride in the same
erratum. The analysis plan's bytes are not edited (plan §13); this section governs where they differ.
Plan SHA-256 at this erratum: <unchanged digest>.

1. **Determinism before the release (plan §3.2 item 2).** After the blind dry run completes with no tooling refusal,
   steps 1–11 run a second time, blind, from identical bytes at the same pinned commit and window index, on the same
   host and absolute paths, in a fresh custody root, never concurrently with any other analysis job. Every output
   digest must equal the dry run's; a mismatch is a determinism defect under R3. Only structure is serialized, as in
   §3.2 item 1. After the release event the lead reads only outputs whose digests both runs agree on. Plan §3.2 item
   2's post-release rerun is not run.
2. **Results check (plan §1 item 4; §3.1 step 12; registration §8 "Who may read", the clause naming "the results cold
   gate").** Step 12 is replaced by: (a) the comparator of item 4, whose program, coverage map and planted-fault tests
   were committed and executing-reviewed before the dry run; and (b) one executing seat with no prior involvement in
   lane L9, which after the release event (i) runs the comparator, (ii) re-derives by its own computation both GAMMA
   contrasts of the scaled-allowance line and one cell of every other line that only the independent recompute
   produces, including the BETA-inclusive pooled branch above 16 units, (iii) checks every rendered fill of step 11
   against its issued value for rounding, units, label, outcome word and placement, and (iv) confirms that the
   recompute's re-derivation of member exclusions from `derived/flags.jsonl` through the sealed catalog equals
   `derived/exclusions.json`. A disagreement goes to R3 or to plan §3.2 item 3, never to a reselection. That seat is
   the post-release reader the custody map named as the results cold gate.
3. **The independent recompute (`scripts/independent_recompute_b5.py` at its reviewed pin) is pre-release
   automation.** It may read restricted paths before the release event. It writes its values only into restricted
   custody. Its public output is the comparison's structure: STRUCTURE-class flag codes, run counts, and per-family
   pass/fail counts. It prints, emails and commits no value.
4. **Release tolerance (RUN_STATE item 37 (ii)).** Each run's phase energy agrees within 1 mJ; every printed quantity
   agrees, unrounded, within half a unit of its last printed digit; outcome words, dominance branch, p42 status and
   Holm order agree exactly. A quantity missing or null on either side is a disagreement. Every step-11 placement is
   mapped to a compared quantity or listed as uncovered and handled by item 2(b). The observed difference is printed
   beside each bar and is never used as the bar.
5. **Release condition.** The release event is recorded only when: the dry run is complete with no tooling refusal;
   item 1's digests are equal; item 4 agrees; the blind executing Fable and Opus passes cover the final L9 pin; and the
   dry run's `analysis_commit` equals the reviewed L9 tag. There is no other gate before the release.

**What this changes:** when determinism is checked; who checks the printed numbers after the release, and how; one
more automated pre-release reader with structure-only output; the agreement bars.
**What this does not change:** any estimator, exclusion, kept count, flag catalog effect, blinding factor, the
analysed attempts (ALPHA a1, BETA a6, GAMMA a1), the order and content of steps 1–11, any refusal rule, or any
registered number.
```

### (b) Block-6 §17 entry

The registration requires this form, quoted:

> "A change after that commit is a dated entry in §17 with its reason (§12.4 says what such a change may and may not touch)." (header, per the b6 segment)
>
> "No change to registered arithmetic after any block-6 data exists. A rule of §8 found wrong may be changed while block 6 is blinded, by a dated entry in §17 checked by one executing refuter…" (`jw:docs/registrations/block6_replication_DRAFT.md:1170-1173` (V))

ED-RULING item 7 requires this entry for §13 (`ED-RULING.md:81-83` (V)). The format follows the existing change log (`:1382-1406` (V)).

```markdown
- 2026-10-2X (lead, <session>): §13 order and code, §12.3's cold-pass timing, S-2 custody roots, S-14 and S-15.
  Made while block 6 is blinded, before any block-6 analysis output exists and before block 5's release; no author or
  refuter has read a block-6 energy or a restricted path. Checked by one executing refuter (<seat, report>). Reason:
  ED-RULING 2026-10-27 item 7, and the same evidence for block 5 (a full-size synthetic run per fix round costs about
  6 h; the real blind dry run is the end-to-end test on the actual data).
  (1) §13's "tested on synthetic fixtures and on full-size production-shaped synthetic archives through the real stage
  chain" is met by: fixture tests carrying the registered member counts (10 repeats and 10 quads per cell) and raw
  files of at least 1 MiB, so the compressed-read path runs; serial-equals-parallel and plain-equals-compressed digest
  tests; and one full-size production-shaped synthetic run with planted known values through the real stage chain, on
  the release-candidate commit, not repeated per fix round.
  (2) §13's executing review and the two blind executing cold passes are met by one stage of two blind executing
  seats, Fable 5.1 and Opus 5.5, launched together, each briefed to run probes and mutations on the block-6 additions.
  The stage may run while the per-session blind dry run runs and completes before the release record. A number-bearing
  commit after it gets a delta pass from both families until a round reports nothing above LOW. In §12.3, "at merge
  (§13)" reads "before the release record (§13)".
  (3) S-14 is the L9 commit tagged at block 5's release plus the block-6 additions at the commit covered by (2). If the
  per-session blind run starts before that tag exists, S-14 is the L9 commit of block 5's blind dry run; any later L9
  change re-pins S-14 by a dated entry and re-runs every unit whose program closure changed; the release record
  refuses unless S-14's L9 commit equals block 5's release tag.
  (4) Before the release, a second complete per-session blind run from archive bytes at the final S-14 pin, in a
  second custody root, on the same host and absolute paths, run after the first; every output digest must be equal.
  The release record binds these digests before any value is opened. After block 5's release only the cross-block phase
  (§10, §11, S-16) runs, twice, with equal digests. This replaces §13's "after the release the analysis re-runs from
  identical bytes".
  (5) S-16 runs where block 5's raw bytes are and lists every raw input it reads; a rule it cannot evaluate prints
  "not evaluated", never 0.
  (6) S-2: restricted block-6 paths may also exist on the analysis host <Mac | Ed's MacBook Air>, at the same absolute
  paths, under a macOS account no agent session uses, excluded from Spotlight and iCloud; §12's automation-only rule
  applies there unchanged.
  (7) S-15: whole-machine energy per phase is the definition of b6design §8 at <commit>, meter only (§9.5 item 5),
  with the clock fit <method ruled blind, L8>; a battery-inside variant is a labelled alternative only. The independent
  recompute computes the same definition and S-13 applies to it.
  Changes: when and how the analysis code is tested and reviewed, when determinism is checked, where the analysis may
  run; fills S-15 and fixes S-14's meaning. Does not change: any §8 rule, estimator, pairing, counting rule, S-13 bar,
  blinding rule, or the release condition of §12.3 beyond the cold passes' timing. No §8 rule changes, so no
  original-rule result is printed beside it.
```

### (c) BYTES Addendum 10

The authority is the "Authority" paragraph, which orders addenda (`bytes:docs/registrations/bytes_pack_v1.md:14` (V)), plus ED-RULING 6a for the date ("amend the end date prospectively while BYTES is still blinded", `ED-RULING.md:72-74` (V)).

```markdown
**Addendum 10 (2026-10-2X; item 1 by Ed, items 2–4 by the lead).** Made while BYTES is blinded: nobody has read a
BYTES energy, power or held-out row; only structure (counts, codes, verdicts) of pass-1 sessions has been seen, and no
pass-2 session exists.
1. **End date.** In §5 "Stopping" and every pack's `stopping.end_t0_before` not yet passed,
   2026-11-02T00:00:00-08:00 becomes **2026-11-05T00:00:00-08:00**. No t0 between 2026-10-31 16:30 PDT and
   2026-11-01 02:00 PST, as before.
2. **Pass-2 registration gate (§13, "pass-2 packs remain draft until their registration gate").** The gate is:
   `scripts/bytes_plan_trees.py` emits the six p2 packs as `registered` with estimator versions bound to
   `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`, their sizing, clock and disk rows recomputed by
   the registered derivation, and no draft notes; `--check` passes; CI's every-pack sidecar test and pass-2
   tree-selection test pass; one executing reviewer confirms the p2 trees are p1's with module order reversed and the
   rows recompute; the measurement checkout receives the commit by cherry-pick verified by tree equality. Because only
   pack JSON and sidecars change, §19's whole-suite run on the measurement laptop is not repeated. Each p2 sub-pack's
   first session keeps its smoke (§19).
3. **Priority if the date binds.** At an arm, if the remaining packs cannot all start before item 1's date at the
   measured cycle time, the next pack is the first of: a pass-1 sub-pack not yet counting; s5-p2; s1-p2, s2-p2;
   s6-p2, s3-p2, s4-p2. Otherwise the registered order stands. Declared before any pass-2 data exist and before anyone
   reads any per-session analysis output.
4. **Thermal labelled alternative (§6, §7).** The registered exclusions are unchanged and every printed result uses
   them. Beside each per-model point, H1 word and H2 fit, a line labelled "thermal: decode-span only" is printed in which
   `thermal.os_level_nonzero` removes a unit only when its reading overlaps that unit's decode span; it is computed for
   every model in both passes, outside `joulewise/bytes_analysis.py`, and the twin computes it independently at §12's
   bars. Collection is unchanged.
Changes: the last t0, the pass-2 gate's form, an order used only if the date binds, one labelled line.
Does not change: any estimator, exclusion, bar, coverage, family, blinding, the stage-1 commitment's content or
timing, the known-bytes order (the test runs after pass-1 collection and before stage-1 unblinding; if it misses that
slot, "Known-bytes check: not measured" prints and nothing is filled in later), or any registered number.
```

### (d) Minimal gate policy (process rule; orchestration.md)

```markdown
**Gate policy (2026-10-2X).** Made before any block-5, block-6 or BYTES result is seen; it changes how code and rules
are checked, never what is computed. Where a registration requires more (block-5 §10, block-6 §13 as amended, BYTES
§19), the registration wins.
1. **Review stage.** Number-bearing or collection code: two blind executing seats from different families (Fable 5.1,
   Opus 5.5), launched together, each briefed to probe and mutate. Their reports count as both the independent review
   and the cold pass. Code touching counting, exclusion, estimators, the claim path, the agent census, stand-down, arm
   checks or admission always gets two families; mailer, notices and text get one.
2. **Delta rounds.** Every fix diff to such code gets a delta pass by both families until one round has nothing above
   LOW in both. "Cannot occur on the real records" counts only when the replay set contains every input class the
   finding names. The same defect class twice: the lead writes a structural rule; a third time: consult.
3. **Rule changes.** One executing refuter plus a recorded lead line. A blind executing judge rules only when the
   refuter's executed result contradicts the lead on a counting or exclusion rule, when a two-seat council splits on
   science, or when a registration requires a judge.
4. **Registration gates.** Two families re-derive from raw every measured value, exclusion level and sizing row. Text
   that sets no boundary, member, exclusion, value or order needs one executing reader. A diff-only gate after an audit
   is allowed only when the audit's values are re-executed by script at the registered head.
5. **Pre-arm triple audit (#416).** Unchanged: three families, once per frozen head.
6. **Real-program rehearsal.** A live machine test only for collector, driver, controller, smoke-prepare or launchd
   changes; otherwise the replay harness on stored archives. A new registration's smoke runs the exact registered pin's
   committed bytes and reruns if any pack byte changes after it.
7. **CI.** Blocking: tests, the strict CLI smoke, `repin --check` for every kind-P pin family, the executing-review row
   test, the orphan-process census. Advisory: docs freshness, gen_state, historical-receipt semantics, gate-ledger format.
8. **Envelopes.** A malformed bridge envelope whose final envelope line is present is FLAGGED; the lead accepts the
   work only after its own diff read and replay. A missing body or envelope line is a failure.
9. **Real-data analysis hosts.** One heavy job per host. Dry run and determinism run on the same host and absolute
   paths. Any wall-deadline firing is a tooling refusal and a rerun. No agent can read a restricted folder (separate
   account, not prose).
10. **Measurement Mac.** No agent process, ever. Remote work into the Mac only as scripts it pulls at a desk.
11. **Pruning tally.** Each session record ends with a table: gate, ran, caught_number, caught_session_refusal,
    evidence. A gate with no catch in three sessions is proposed to Ed.
```

---

## 4. Parallelism, cadence and machines

### The DAG from a session's end to released numbers

```text
MEASUREMENT MAC (serial, physics only)
 session N chain ─► harvest + desk (88-101 + ~7 min) ─► attempt line + loop mail ─► PRECHECK/smoke ─► session N+1 ...
                         │ (desk, loop held ≤1 h, script not agent)
                         └─► package+hash block-5 (and later block-6) items ─► iCloud JouleWise-transfer ─► Air verify

CLOUD (any time, in parallel)
 L9 fault injection (N3) · merged Fable+Opus executing stage (ED3) · comparator (N6) · index/FILL scripts (N4,N5)
 block-5 erratum judge+refuter · block-6 §17 + S-15 + refuter · block-6 driver (N9) · block-6 recompute (N10)
 BYTES pass-2 flip (BY-2) · BYTES A1 campaign · KB code · CI · councils

AIR (one heavy real-data job at a time, non-agent account)
 [today] cached full-size test_dry_run (6b condition 2)
 B5: dry run ─► second blind run ─► recompute ─► comparator ─► (release event) ─► step-12 seat ─► BLOCK-5 NUMBERS
 B6 (if the Air is free before the Mac): 6 floor units (A r3 first) ─► 3 GAMMA units ─► second run ─► recompute ─► comparator
                                          └─ after block-5 release: cross-block phase x2 + S-16 ─► BLOCK-6 NUMBERS

MAC AFTER BYTES COLLECTION CLOSES (quiet, keys local)
 KB hour (if not done in a gap) ─► blinded agreement ─► fit release ─► stage 1 + twin ─► DC/rest ─► COMMIT
   ─► held-out agreement ─► stage-2 release ─► stage 2 + twin ─► BYTES RESULT
 (block-6 real runs here instead, if the Mac is free first)
```

### Where each kind of work runs

- **Measurement Mac.**
  - Sessions, PRECHECK, smokes, harvest, desk.
  - BYTES key releases and, after collection, BYTES stages 1-2: the keys live at `/Users/edr/night-b6/loop-bytes/packs/bytes/blinding` (`bytes_pack_v1.md:342,346` (V)), and the Mac is the fastest idle host then.
  - The known-bytes hour.
  - Block-6 real runs if it is free before the Air.
  - Nothing else, and no agent.
- **MacBook Air (24 GB, M4, 198 GiB free (V)).**
  - All of your interactive Claude and Codex work and `codex update`.
  - The Codex Cloud login relay and fallback Sol seats (L10).
  - Block-5 dry run, second run and recompute under 6b.
  - Optionally block 6.
  - The macOS whole-suite subsets and the replay harness on non-claim archives (H, BY-H2, machine tests); timing probes (N12).
  - Real data lives only under a separate macOS account no agent uses.
  - **Caveat (V):** this synthesis and the earlier segment agents ran on the Air during today's condition-2 run (load average 2.76-3.38 at 13:03). The recompute auditor reported load 5 during a test run. If that run fires the deadline, rerun it once with nothing else on the Air before concluding the Air is too slow.
- **Cloud.**
  - All code, reviews, councils, refuters, judges, CI, synthetic runs, and the comparator and recompute builds.
  - Never real or blinded block 5, block 6 or BYTES data. A session is about 43 GiB against about 30 GB of seat disk (cadence plan:15), and the blinding council found the blinded export readable to about ±6% (4b350f47 RECORD:26-36).
  - This is "as much in the cloud as possible" without moving restricted data there.

### Per-session analysis as data lands

- **Paper A:** everything is collected, so per-session scheduling buys nothing [recompute R3/cad]. Run the recompute over all block-5 windows plus BETA a1/a4/a5, and later all nine block-6 sessions, **in one batch** on the analysis host. Never act on a recompute mismatch by re-collecting. The fix is re-reduction; re-arming would be a selection made on the data [recompute R3/sci].
- **Block-6 runs** as a two-level DAG: 6 floor units, A r3 first because it feeds G r2 and G r3, then 3 GAMMA units. Restore each session **once** on the analysis host for the whole run. No restore and recompress per unit, which would race on a shared A r3 [b6 B6-03/sci; B6-13/cad]. Pool workers ≤ P-cores.
- **BYTES:** after BY-3 and BY-4 are decided, a per-session blinded-stage run of the export (CLI patched for fewer than 3 fit points, synthetic agreement suite rerun, a counting check added). It runs on the Air's analysis account and outputs **comparer counts only**, which front-loads export-ingress refusals [bytes A2/sci]. It is optional and lower value than N11-N13.

### Stopping stray agent processes from killing sessions

1. No agent ever runs on the measurement Mac: no interactive Claude or Codex, no headless magistrate, no `codex update`, no ChatGPT-app Codex. The only agent residue left was the daemon from an interactive `codex update` (RS 78; a46602ae RECORD:4).
2. Uninstall the Codex app or CLI and the ChatGPT desktop Codex from the measurement Mac, and turn off its auto-updater (exact setting INFERRED).
3. A `~/.zshrc` guard on the Mac that refuses `codex`, `claude` and `codex update` while any `~/night-b6/loop*/collection.active` exists (block6_collection_draft.md §6.3 item 1; your file).
4. No inbound ssh or rsync into the Mac while `collection.active` exists. The census matches the full argv (`pgrep -a -lf '[c]odex|[c]laude'`, `bytes:joulewise/hazards/arm.py:65-70`), so paths like `claude-501` trip it, and smaller loads go in unflagged [collect C17/sci]. The Mac pushes state by mail or git. Mac-side jobs such as packaging run as scripts the Mac pulls (its launchd watchdog polls a git ref) at a desk [gov G21/cad].
5. Keep the arm census, the 600 s resume and the 7,200 s stop unchanged; they are registered (`agent_pause.py:11-13`). A loop auto-kill of launchd-reparented daemons is decision 8. Recommended: not unless a stray recurs after steps 1-3, and then with a whole-process-group kill, a re-census and a window flag [collect C13/sci].
6. The session-end orphan-process census runs on the Mac and on the Air. A leaked hazard monitor once moved c_q from 0.54 to 0.73 (1a1261a5 RECORD:20,26).

---

## 5. Critical path, with dated estimates (all INFERRED unless marked)

BYTES slot arithmetic, assuming a ~10.5 h t0-to-t0 cycle and no Mac holds:
- t0 slots at about 10-27 15:00; 10-28 01:30, 12:00, 22:30; 10-29 09:00, 19:30; 10-30 06:00, 16:30; 10-31 03:00, 13:30; 11-01 02:00 PST, 12:30, 23:00.
- That is 13 slots before 11-02 00:00 PST, with no t0 in the DST window (RS 69(e); `RUN_STATE.md:329` (V)).
- 8 counting sessions are needed. At pass 1's attempt loss rate (2 of 6), about 12 attempts. That is why I recommend BY-1.

| Milestone | Estimate | Gate |
|---|---|---|
| Cached full-size `test_dry_run` on the Air finishes (L9 acceptance run; 6b condition 2) | 10-27 evening (running since about 12:48 (V)) | none |
| BYTES pass-2 flip committed and cherry-picked at a desk | 10-28 morning | BY-2, L2 |
| N3 per-site fault injection | 10-28 | cloud seat |
| Merged Fable+Opus executing stage on L9-2, launched | 10-28 | ED3 |
| Block-5 erratum (judge+refuter); block-6 §17 + S-15 + refuter | 10-28 to 10-29 | L8 |
| Block-5 packaging at Mac desks, iCloud, Air verify | 10-28 to 10-29 | ED2 |
| BYTES pass 1 complete (s1-p1, s6-p1 retries) | about 10-28 | L1 |
| Review dispositions, delta passes, L9 merge, comparator reviewed | 10-29 to 10-30 (plus 1 day per blocker) | |
| `B5-TRANSFER: GO` | 10-29 to 10-30 | ED2 conditions |
| Block-5 blind dry run on the Air | 10-30 (plus about 1 day per cure round) | |
| Second blind run, recompute, comparator, release-event record | 10-31 | B5-1..5 |
| **Block-5 numbers** (release event plus the step-12 replacement seat) | **about 11-01 (range 10-31 to 11-03)** | |
| BYTES collection closes | about 10-31 with 0 losses, about 11-01 with 3; later only if losses use BY-1's days | |
| Known-bytes hour | a quiet gap after pass 1 (DST window if free), else after the last desk; status of BY-KB tooling unknown | N14, L9 |
| **BYTES stage 1** (commitment) | **about 11-01 to 11-02** (stage-1 wall time unmeasured; N12) | N11-N13, L7 |
| **BYTES stage 2** | **about 11-02 to 11-03** | |
| Block-6 driver integrated; known-answer run; two-family stage | 10-31 to 11-02 | L3, L9 merge |
| Block-6 per-session blind runs x2, recompute, comparator | 11-02 to 11-03, on whichever host is free | B6-1..7 |
| **Block-6 numbers** (cross-block phase + S-16 + release record) | **about 11-03 to 11-05** | block-5 release |

The longest path is the L9 review stage. Each blocker it finds adds about a day to both blocks. That is why it should launch tomorrow in parallel, not after the dry run.

---

## 6. Rejected proposals, and why

| Proposal | Why rejected (concrete failure mode) | Evidence | Instead |
|---|---|---|---|
| Harvest on the Air while the Mac collects (collect C19, C20, C21 pending state; outcomes E09) | The Air's records root lacks the BYTES key, so `_stored_or_draw` draws a new factor and pass 2 is blinded with a different one, silently. A deadline firing in re-reduction becomes `member.reduction_mismatch` (EXCLUDE_MEMBER), not a fault. The async verdict skips "fix before the next session of any pack". The Mac cannot hold two uncompressed sessions | `bytes:joulewise/b6/blinding.py:88-134` (V); `harvest.py:4094-4099`; `loop.py:317-320,579-596`; `bytes_pack_v1.md:342` (V) | Harvest stays on the Mac; revisit after GOV-1 with one key custody |
| Smoke harvest on the Air (C6) | Same blinding-key draw | as above | none |
| Skip pass-2 smokes by dropping pack_id from the fingerprint (C4; bytes C3; E04 item 4) | Registered for each sub-pack's first session; the p2 trees are new; the loop smokes per pack_id; pin commits also change `code_commit` | `bytes_pack_v1.md:450` (V); `fingerprint.py:40-60,75-99`; `plan.py:676-696` | Keep; fix the smoke itself after BYTES |
| Cut the in-chain bound derivation (C10) | `chain.py` requires it (number-bearing); the harvest validates its artifact; without it every session gets `neg8.bound_not_derived` | `chain.py:436-442`; `harvest.py:4449-4552` | none |
| Loop writes STOP into a running chain on zero yield (C15, E07) | No loop-to-chain channel exists; an external kill risks ledger and pin custody; zero in stage 1 can still leave a countable session | `loop.py:457-469`; `desk_lane.py:34-46` | Alert only (PR-2); cooperative stop at next freeze (GOV-2) |
| Magistrate polling the Mac over ssh (C17 as written) | The full-argv census or unflagged load during runs | `arm.py:65-70` | Push and pull model |
| Corpus early stop (C9) | Already implemented; the saving does not exist | `compose.py:115-117` | none |
| Loop timing tweaks during BYTES (C1, C2 merge, C3, C5, C7 reuse) | During pass 2 every session smokes and the notice already overlaps the smoke, so the saving is about 0; mid-collection tooling risk | `loop.py:321-328,489` | PR-2 after BYTES |
| Real dry run not gated on the one cached full-size run (b5 P3/cad) | That run and the fixture test are the only checks of the cache and pool at full size; release equality compares two runs with the same code | E20/sci; ED-RULING:45 (V) | Keep (Ed-ruled) |
| One cold pass on L9, second family dropped (P7, recompute G2) | One family shares the builder's blind spots; the comparator does not see redaction, labels or rendering; ED item 3 says "the release still needs them" | ED-RULING:48-49 (V); PL:377 | Both families, early, in parallel (ED3) |
| Parallel ALPHA/BETA step 4, step 6 beside step 9, parallel step 10 (b5 S4, S6_S9, S10) | Contention next to the 120 s deadline before fail-closed is shown; a race on shared RunState; step 10 has never completed at full size | L9-2.md:129-130; dry_run.py:424-451,480-494 | Serial |
| Drop or digest-replace step 2 (b5 S2) | Cheap once cached; it anchors the analysis commit; another amendment for minutes | dry_run.py:474-479 | Keep |
| Lead reads dry-run numbers while release mode reruns (b5 R4 as proposed) | Numbers read before reproducibility is shown; the repair choice is then made with the outcome in view | plan:194-199 (V) | B5-1 |
| Step 12 cut to "one reviewer reads the comparator table", or cut entirely (b5 R5; recompute G1; gov G24; outcomes E22) | No comparator exists; recompute-only lines have no second computation; numeric bars miss words and rendering (C66 sign flip); AN-18 is unmet; the custody map names the reader, so it needs the §10 route | recompute:4-5,544-557; PL:183,328,455; reg:4901-4902 (V) | B5-2 via cold erratum |
| Recompute reads `.zst` directly (recompute R2) | Not needed once the data are unpacked; as written it skips per-file digest checks and loses CSV and meter inputs silently | `desk_compress.py:250,298-318`; `desk_restore.py:132-140` | Unpack on the analysis host; revisit with digest checks |
| "No second review pass unless the first finds a blocker" (recompute R19) | B1 (counts depending on output mode) came from a delta check after a "minor" cold round | d701302f | Gate policy 2 |
| Delta-round stop when "replay shows it cannot occur" (gov G05 rule b); single-seat deltas (E14) | #416 round 4's HIGH was missed by the 25-archive replay because no smoke archive existed; rounds 1-3 A catches each came from one family only | DISPOSITIONS-416 round 4; 7209d1b0 RECORD:106-111 | Gate policy 2 |
| Triple audit cut to two seats (gov G18; E15) | Astra alone found A3 and A4 in #416 and C18 in the seal audit | DISPOSITIONS-416; gates/31 A1 | Keep three |
| `repin` advisory except the estimator files (gov G09; E12) | The block-6 and BYTES kind-P pins would lose their only merge fence | `bytes:configs/pins/registry.json`; ci.yml:109-112 | Gate policy 7 |
| Renew TIER-01 on the empty log (gov G10) | The log is unmaintained, not zero | tier01_defect_log.md | PR-5 |
| Orchestrator on the Air with ssh into the Mac (gov G21) | Remote commands fall outside the watchdog's stand-down and may evade or trip the census | MAGISTRATE_WATCHDOG.md:34-36,103,149 | Pull model (ED7) |
| Smoke in parallel with the registration gate on a pre-correction commit (gov G13) | Gate corrections make a new commit, the same escape as s1-p1 | RS 71; registration flip 6731d5249 | Bind the smoke to the final pin |
| Block-5 erratum machinery cut (E19) | Sealed §10 binds block 5; a lead-line readmission of BETA a1/a4/a5 would be a post-collection roster change | reg:5144-5146 (V) | Lighten for future blocks only |
| Block-6 base 1706257c as it stands (b6 B6-01) | Lacks #573's cold-pass-corrected readers that steps 1-2 run | 903b5a2f; db9e8ab3 | L3 |
| Per-unit in-place restore under a concurrent DAG; recompute sharing the driver's restore or pairing index (b6 B6-03, B6-10, B6-14) | Recompress races a reader on shared A r3; shared inputs make S-13 common-mode | b6design:1597-1600,1635-1636 | Restore once per session; independent recompute (N10) |
| Drop block-6 full-size synthetic entirely; cap at one delta round (b6 B6-07, B6-09) | Only planted truth sees kept-unit errors; #416 late rounds found real HIGHs | recompute:4-6; 6b54a51d, 028f8c50 | B6-1, B6-2 |
| Block-6 on the Air with no conditions (b6 B6-12, B6-13) | Absolute-root bindings, unenforced custody, the deadline premise | b6design:287-293 | B6-6 conditions, or the Mac after BYTES |
| S-16 on a host without block-5 raw bytes (b6 B6-17) | It would silently print 0 for rules it cannot evaluate | REG S-9 row | B6-5 |
| Decouple the known-bytes measurement from stage 1, fill it in later (bytes C13) | Knee refusals, reruns and UNDETERMINED become choices made with the outcome in view; the rule already prints "not measured" | reading rule DRAFT:167 | Keep the order |
| Thermal decode-span rule as **primary** for s5-p2 (bytes C8/cad) | A model-specific rule chosen after seeing that model's exclusion pattern | a46602ae RECORD:8-10 | BY-4 labelled line, all models |
| Cut pass 2 to s5-p2 plus backups (bytes C10 option ii) | Drops the order-reversed pass for 7 models | bytes_pack_v1.md:105 (V) | BY-1 + BY-3 |
| Session pool for BYTES stages without a guard; DC/rest agreement after the commitment (bytes A5, A6 as written) | A deadline firing makes a fit unit `unusable` silently, and it is frozen into predictions | bytes_analysis.py:46,1001-1002,1016-1017 (V) | N12, N13, L7 |
| BYTES stage 1 "as soon as the fit set exists" (cadence plan:77) | Commits one-pass fit points, a WHAT change; R5 says after collection closes | bytes_pack_design.md:105-110 | Keep R5 |
| ED-RULING item 4 as worded (reduced-fixture release equality) | Infeasible: kept_units refuses cells without the registered 10/10 | L9-2.md:131-138 | B5-1 (ED3) |

---

## 7. Decisions only you can make

1. **Take every agent off the measurement Mac**, including your own interactive Claude and Codex use and `codex update`; uninstall the Codex app and its updater there; add the `~/.zshrc` guard; no remote commands into the Mac during collection. **Recommended: yes, today.** It is the largest October loss (E02) and costs no code.
2. **Say `B5-TRANSFER: GO` once these hold:** L9 acceptance plus the merged review stage; today's Air run passes (rerun it alone if it fires); N3 shows every deadline firing is a refusal; identical absolute paths; a non-agent account; one heavy job at a time; packaging by script; BETA a1/a4/a5 included. **Recommended: yes.** It frees about one BYTES slot and decouples block 5 from BYTES.
3. **Amend ED-RULING items 1, 3 and 4.** The parallel Fable+Opus executing stage, with a mutation mandate, counts as both the review and the cold passes; delta passes cover later commits; drop `test_docs_freshness`; replace the reduced-fixture release test with the second blind run. **Recommended: yes.**
4. **Release condition for blocks 5 and 6:** the B5-ERRATUM-R1 and §17 conditions, with no other cold gate. Drop the release cold gate the scout added "under the current user's instruction" (scout:206). If that request was yours, this is your call. **Recommended: yes.**
5. **BYTES end date: 2026-11-02 becomes 2026-11-05 00:00 PST,** declared blind now, with the BY-3 priority. Fix the "PDT" wording in ruling 6a. **Recommended: yes.** It costs nothing if pass 2 finishes early, and it protects s1 (the fit set) and s5-p2 (70B's only possible point).
6. **Custody on the Air:** restricted block-5 and block-6 bytes may sit on the Air only under a separate macOS account no agent uses, outside Spotlight and iCloud. Deny agent access to the JouleWise iCloud folders: they mirror to the Air, and RS 79 notes 128.8 GB of `JouleWise-backup` was downloaded there (V). BYTES raw data and keys stay on the Mac. No restricted or blinded data in cloud seats. **Recommended: yes.**
7. **Orchestrator placement:** the orchestrator runs in cloud sessions, plus the Air for interactive work, the Codex login relay and fallback seats. Mac-side steps run as scripts the Mac pulls at a desk. This is a hardware call (D-184 addendum). **Recommended: yes.**
8. **May the loop auto-stop launchd-reparented Codex daemons during a pause?** **Recommended: not now.** Revisit only if a stray recurs after decision 1, and then kill the whole process group, re-census, and log a window flag.
9. **Delete the four-model council (D-184).** It never ran (PL OP-8). **Recommended: yes.** You can still ask for one.