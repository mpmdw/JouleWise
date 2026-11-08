# Block 6 design and registration audit: Fable 5.1 seat

**Date:** 2026-11-07. **Seat:** Fable 5.1 (high), independent of the Opus seat on the same brief.
**Repo state read:** `origin/main` at `ca2d1ee97` (worktree `jw-wt/fable-b6-audit`); the block-6 collection line
`lane/2026-10-17-b6-packs-registered` at `1706257c4` (collection pin `f31aca19f`); the block-6 analysis design
`lane/2026-10-22-b6-analysis-design` at `578685ec3` (PR #537); the S-9/S-11 fill `lane/2026-10-22-b6-s9-s11` at
`c37614f71` (PR #529); the block-6 driver draft `lane/2026-10-27-b6-analysis` at `10b2b679c`.
**Blinding:** no `/Users/edr/jw-b5-*`, `night-*`, custody, archive or `restricted/` path was opened; no block-5 or
block-6 energy, interval, contrast, outcome word or verdict was read or inferred. Every number quoted below is a design
constant, a count, a wall time or a line number. Tests run: `tests.independent_recompute.test_comparator` (the three
S-13 bar-set tests, `JW_B5_SYNTHETIC_ONLY=1`, `nice -n 19 taskpolicy -b`, TMPDIR under `/private/tmp/jwburn-fable-b6`):
2 selected tests OK. No real data, no model weights, nothing on the measurement Mac.

Citations are `path:line @ commit`. Aliases: **REG** = `docs/registrations/block6_replication_DRAFT.md` (bytes
identical at `2a4e5149c` and `ca2d1ee97`, per `docs/registrations/block6_freeze_by_commit_addendum.md:5-6`);
**DLE** = `docs/analysis/b5/DEVIATION-LOG.md`; **LEAN** = `docs/analysis/b5/LEAN-COVERAGE-AUDIT.md`;
**TRACE** = `docs/run_reports/2026-11-07-b5-release-hold-trace.md`; **RESUME** =
`docs/handoff/2026-11-07-account-retirement/RESUME.md`; **DESIGN** = `docs/design/b6_analysis_additions.md` (on
`578685ec3` only); **I** = `scripts/independent_recompute_b5.py`; **C** = `scripts/compare_b5_recompute.py`.

---

## 0. One correction to the brief, and the verdict in three sentences

The brief says to list amendments needed "BEFORE any Block 6 data exists". Block 6 finished collecting on
2026-10-21: nine counting sessions, alpha r1/r3/r4, beta r1/r2/r3, gamma r1/r2/r3 (addendum `:24-25`;
`RUN_STATE.md:203` item 59). The data exist, sealed and unanalysed. REG §12.4 (`:1168-1173`) therefore governs: no
change to registered arithmetic; a rule found wrong may change while block 6 is blinded, by a dated §17 entry checked
by one executing refuter. The real deadline is not "before data" but **before block 5 is unsealed**: REG §12.3 item 2
(`:1150-1151`) says block-6 values estimate the same quantities as block 5's, so any block-6 analysis decision taken
after the block-5 unseal is taken with the block-5 outcomes in view. Every amendment below should land before the
block-5 unseal OK.

Verdict. (1) Block 6 has **two incompatible, unregistered production plans** for its analysis (the L9-based DESIGN of
10-22 and DLE-2's lean-recompute production path of 11-06); REG §17 has had no entry since 2026-10-17 (`:1382-1406`),
and DLE-2 itself says its block-6 entry "is owed" (DLE `:167-168`). (2) The registered agreement tolerance S-13 is
**not well defined**, because it is "half a unit of the last printed digit" and block 6 registers no printed
precision; the only block-6 bar set in the tree is marked `placeholder` and the comparator ignores that key. (3) Of the
block-5 lessons, D1-D4 and D6 are in main's recompute and comparator, but **D5's cause fix is in no pinned commit**,
block 6 exercises exactly that binder three times over cross-session floor pairs, and the seven DLE-2 uncovered families
recur in every one of nine sessions with no block-6 producer or comparator row.

---

## 1. What block 6 is, as registered, and what exists in code

| Registered element | Where | State on `ca2d1ee97` |
|---|---|---|
| Registration + analysis plan, REGISTERED 2026-10-17 | REG `:3`, `:1382-1406` | unchanged since; §17 last entry 2026-10-17 |
| Estimators 1-4: block 5's, per counting session, no pooling | REG §9 `:899-1006` | L9 and recompute exist for one window per pack only (F7) |
| §9.5 labelled lines (8 items), §10 summary, §11.1-11.4 reporting | REG `:1007-1120` | no producer on main; `summary.py` and an 89-line `scripts/b6_analyze.py` on `lane/2026-10-27-b6-analysis` against a fake L9 adapter (`.codex-report/B6-AN-1.md` @ `10b2b679c`) |
| Release condition: close, block-5 release, blind dry run over every session with no tooling refusal, recompute within S-13 | REG §12.3 `:1146-1166` | no block-6 release program; `scripts/release_b5.py` pins the block-5 bar set only (`:58`, `:61`) |
| Analysis commit S-14, whole-machine definition S-15 | REG `:1207-1208` | OPEN |
| S-9 (P*), S-11 (T_phase), due before the blind dry run | REG `:1203`, `:1205` | OPEN on main; filled in PR #529 (`c37614f71`), unmerged since 10-22 |
| Collection code, catalog, acceptance, pack files | REG S-1..S-4 `:1194-1197` | **not on main**: `f31aca19f` is not an ancestor of main; `configs/b6/` and `joulewise/b6/` are absent from `ca2d1ee97`; tag `b6/collection` exists (`RUN_STATE.md:872` item 149) |
| Hidden offsets divided out before printing | REG §12.1 `:1138` | `joulewise/b6/blinding.py`, `export_runs.py:149` @ `1706257c4` apply factors only at the export table; raw bundles are unaffected, so the recompute's raw reads are safe |

Two facts about the collected archives that the registration did not anticipate (both from DESIGN §0 items 7-8
`:42-85` @ `578685ec3`, confirmed in the lane code):

- **Every block-6 archive stored its calibration bracket with block 5's acceptance** (s_bracket 14.531 ms instead of
  the registered 10.818 ms, REG `:368-369`). The harvest entry point calls the shared `joulewise.b5.harvest.harvest`
  with the b6 catalog (`scripts/harvest_b6_session.py:14`, `:43-47` @ `1706257c4`).
- **Every file of 1 MiB or more under the runs roots, custody and `sources/` is desk-compressed to `.zst` after the
  harvest** (`joulewise/b6/desk_lane.py:243-244` @ `1706257c4`; `joulewise/desk_compress.py`). The raw sampler plists
  the recompute integrates are among them.

---

## 2. Findings

### F1. Two production plans, neither registered (BLOCKER for the §17 entry)

- REG §13 (`:1175-1188`): "The programs are block 5's analysis programs (lane L9 ...) at their release tag, plus the
  block-6 additions ... The analysis commit is pinned before the blind dry run ... after the release the analysis
  re-runs from identical bytes and every output digest must equal the dry run's."
- DESIGN (PR #537, 10-22) builds exactly that: an `AnalysisBlock` binding seam on L9, one L9 chain per GAMMA unit over
  three sessions, in-place restore of the compressed bytes, a cross-block phase after the block-5 release
  (DESIGN `:42-85`, `:1138-1204`).
- DLE-2 (11-06, `:140-197`): "For blocks 6 onward, the lean recompute ... is the production path"; L9 runs once per
  block as an off-critical-path audit; collection-time judgments are bound by content hash. DLE-2 then lists what it
  owes: the §17 entry, coverage of the seven families, the agreement gate "on the first counting block-6 session", the
  audit-unfinished rule, and blinding at signing (`:166-193`).
- Consequences the registration text now gets wrong under DLE-2: §12.3 item 4 reads "the independent recompute agrees
  with the analysis programs", which is vacuous when the recompute *is* the analysis program; §13's post-release
  byte-identical re-run was dropped for block 5 by DLE-1 (`:71-137`) and has no block-6 counterpart; §1.10's
  definition of "independent recompute" (`:275-276`) names it a check, not a producer.
- The DESIGN's open issue list also records that the driver "has no release mode" (B6-AN-1 report, lead ruling 2).

### F2. S-13 is not a well-defined tolerance (BLOCKER for the release comparator)

- REG S-13 (`:1206`) and §12.3 item 4 (`:1154-1155`): 1 mJ per run phase energy, "and half a unit of its last printed
  digit for every printed quantity". Block 6 registers no printed digits anywhere; the derivation at `:1156-1160`
  addresses only the 1 mJ phase-energy bar.
- The only block-6 bar set, `tests/independent_recompute/bar_sets/s13_block6.json`, says in its own `source` field that
  its decimals "are PLACEHOLDERS ... They must be replaced by the ruled precision. Not adopted for block 5". The
  comparator reads `printed_decimals` (C `:153-155`, `:191-192`) and never reads `placeholder` (no match in C), so the
  set would bind silently if pinned.
- Block 5 settled its own precision question the other way: the coded 1e-6 bars bind block 5, "S-13 is block 6's and
  stays there", and "block-5 printed precision is then not needed" (`RUN_STATE.md:342-343`, item 83 rulings 1-2). So
  block 6 inherited the dependency on an unruled precision.
- Coverage of the set: it names 11 families (`run_phase_energy_j, floor_j, floor_gate_j, dominance_ratio,
  reported_cell_j, contrast_j, contrast_p, descriptive_ratio, per_token_j, b_op_s, count`); the block-5 release set
  `configs/analysis/b5/recompute_bars.json` names 16, adding `machine_j, meter_j, meter_w, rho, window_edge_s`. Whether
  the comparator requires those five when meter rows exist was not verified here.
- Half a printed unit is a weaker bar than block 5's for most families (a 4-decimal `contrast_p` tolerates 5e-5 in p,
  which can straddle the Holm threshold; DLE-2 `:180-181` names the FS3 tie rule for block 5 only).

### F3. The comparator does not cover every registered family, and block 6 adds families with no producer or row

- The seven uncovered families (LEAN §2 `:70-80`; DLE-1 `:111-128`): monitor cost, arm/host and anchor summaries,
  battery phase/subject summaries and discharged energies, stage battery temperature, reference/corpus/NEG-8 history,
  all-attempt history with yield and G10, selection and eligibility. None has a recompute implementation on
  `ca2d1ee97` (LEAN `:53`, `:56-62`; I has no monitor or temperature family). REG §9.5 (`:1007-1011`) requires each
  counting session to print B5-PLAN §8.1's disclosures, "the attempt history of the pack, now block 5's and block 6's
  attempts; battery, thermal, contention and clock counts; reference drift ...; monitor cost". So the seven recur nine
  times, and under DLE-2 nothing on the production path computes them unless the §17 entry names them "supplied by the
  heavy audit run" (DLE `:174-175`).
- Block-6-only printed quantities with no comparator family and no recompute code on main: §10 mean and s_Q; §11.1 Δ
  and per-session differences; §11.2 replication word; §11.4 flagged-inclusive line; §9.5 item 6 (new G/F consistency
  test); item 7 (block-5 codes carried); item 8 (waited-runs line); §8.3 item 3's desk P* exclusion and S-8's E_add
  alternative; §9.5 item 5 (whole-machine per phase with rails' share, S-15).
- Two §9.5 lines exist only on the recompute side: item 3 scaled allowance (I `:83`, `:2718-2744`) and item 4
  single-step reconstruction (I `:82`, `:2206-2283`). Item 4 is registered as "computed by the independent recompute"
  (`:1024`), so it is a single-source diagnostic by design; item 3 is not so labelled.

### F4. The D5 lesson is not yet in any pinned commit, and block 6 hits the same binder harder (BLOCKER for S-14)

- D5 cause (RESUME `:27-29`): `joulewise/analysis_engine/inputs.py` `_order_member_ids(..., campaign_log=True)` counts
  the GAMMA campaign log's campaign-level evaluation row as executed members; every calibration bundle then appears
  twice and `component_evidence_root_disagreement` leaves all four GAMMA floor cells unbound. The evidence itself was
  intact. RESUME says an r4 PR "b5 analysis r4: L9 campaign-log member parse (D5 cause), DLE-4" is in flight; at audit
  time no open PR or origin branch carries it (`gh pr list` searches for "r4" and "campaign-log"; `git branch -r`).
  The three probes are in `docs/handoff/2026-11-07-account-retirement/tools/probe_d5_*.py` @ `ca2d1ee97`.
- Why block 6 is more exposed: REG §6.2 (`:483-505`) binds each GAMMA session's floors to an ALPHA and a BETA session
  from other archives, and with the actual counting set the pairing is GAMMA r1 ↔ (ALPHA r1, BETA r1), GAMMA r2 ↔
  (ALPHA r3, BETA r2), GAMMA r3 ↔ (ALPHA r3, BETA r3), ALPHA r4 floor-only (DESIGN §5 worked example 1 `:603-639`,
  derived from `RUN_STATE.md` item 59 counts). So the binder's campaign-order, ABBA-tag and "every calibration bundle
  exactly once" checks run three times over cross-session roots produced by `f31aca19f` code, whose campaign-log shape
  the block-5 fixtures never covered.
- Failure mode if unfixed: a binding refusal prints as a registered scientific outcome (`not_estimable` after D5b,
  `not_resolvable` before it), step 9b exits 3 as a D-189 outcome class, and the dry run "completes" (DLE-3
  `:334-347`). REG §12.3 item 3 ("no tooling refusal") would then be satisfied by a tooling defect. The only stop is a
  comparator disagreement against a recompute that takes the armwise maximum without binding (TRACE `:298-300`).

### F5. D1-D4, D6 are carried in main's tooling, but two block-6 shapes are untested

- On `ca2d1ee97`: D1 key fix (DLE-3 item 1), D2 idle-attempt file selection and D4 `no_measured_request` (DLE-3 item 4;
  TRACE §5), D3 `descriptive_unanchored`, D6 condition `neg8_survivor_terms` (C `:952`, `:1399`, `:3300`),
  `trace_plist_missing` is a STOP flag (I `:64-68`; DESIGN §15 step 10's audit F4 fix has landed).
- D2 in block 6: waiting admission ends the stream and tries a fresh baseline for up to 1,500 s (REG §3.2 item 1
  `:332-337`), so re-measured idle baselines are the designed response to disturbance, not an occasional retry. The D2
  fix reads `environment_admission.attempts[*]` and `rich_telemetry_idle_attempt_N.jsonl`; its tests
  (`IdleAttemptTests`) use block-5-shaped fixtures. Whether the block-6 driver at `f31aca19f` writes the same metadata
  and file names is unverified.
- D4 in block 6: new member states `idle.wait_cap_skip`, `idle.wait_budget_skip` (EXCLUDE_MEMBER in
  `configs/b6/flag_catalog_b6.json` @ `1706257c4`), runs skipped before sampling. The `no_measured_request` rule should
  cover them; no block-6 fixture exercises it.
- D6 in block 6: REG §9.5 item 7 (`:1041-1050`) keeps the bracket bar bytes and makes the decision disclosure-only, so
  the conditional comparison is the right shape. But the stored bracket's b_op is under the wrong acceptance (section 1
  above). The recompute "recomposes b_op from pre/post plus allowance, compares stored b_op, and falls back to it if
  captures missing" (LEAN `:115`); for block 6 the fallback target is wrong, and the comparator's `b_op_s` family would
  compare two programs that may both read the stored value.

### F6. The exclusion re-derivation and counting source will refuse or misjudge every block-6 session as written

- The recompute re-runs the exclusion function against block 5's sealed catalog (`CATALOG_PATH =
  configs/campaigns/v5_claim_25g83/flag_catalog.json`, I `:73`), and `exclusions_rederivation_mismatch` and
  `kept_units_disagree` are STOP flags (I `:65-68`). Block 6's catalog is `configs/b6/flag_catalog_b6.json` (259 codes;
  S-3 digest `b5bce6c6…`, REG `:1196`), 25 of block 5's 32 session-removing codes are flags (REG `:594-600`), and the
  GAMMA midpoint reason is dropped (REG `:600-602`).
- `RUN_STATE.md:169` item 53: r2-gamma's `derived/exclusions.json` says `claim_usable: false`
  (`neg8.midpoint_lost_primary`) while the loop counted it under REG §8.2. The consumer must take counting from the
  acceptance record, never from `claim_usable` (DESIGN §4.5-4.6 `:434-519` gives a rule; nothing on main implements it).
- Both programs therefore need: the b6 catalog by digest, the sealed `joulewise.flags.exclusions.compute` with no
  pack-scoped window reasons, counting from `derived/b6-acceptance.json`, and a refusal when the two disagree.

### F7. One window per pack is hard-wired; nine sessions and the pairing need a driver, and the wall time follows

- I `main` takes `--ALPHA/--BETA/--GAMMA`, one archive each (`:3148-3161`); `MODELS` constants (`:44-45`).
  `joulewise/b5_analysis/dry_run.py` `PACKS=('alpha','beta','gamma')` (`:232`), `select_analysed_attempts` picks one
  analysed attempt per pack and refuses a window harvested twice (`:707`, `:1649`, `:1711`); C `PACKS` (`:104`).
- Units: six floor sessions and three GAMMA units (ALPHA r3 serves two). Pairing rule 2 is well defined for GAMMA r2
  (no ALPHA in round 2 because r2-alpha never ran). The registration has no tie rule for two counting sessions of one
  pack in one round (DESIGN D16 supplies "earlier t0"); unreachable with the nine, but it should be in the registration.
- Wall time. Block 5 r3's real dry run took 1 h 40 min for one three-window set (RESUME `:26`); step 1 strict
  validation is about 920 s of that and "frozen CPU", step 5 about 970 s
  (`docs/run_reports/2026-11-07-b5-robust-fullchain.md:80-87`). A heavy L9 audit over six floor sessions and three
  GAMMA chains is about 3× if floor sessions are extracted once and units run serially: **about 5 h**, plus in-place
  restore and re-compression of the desk-compressed bytes per unit (a GAMMA unit is about 109 GiB plain, DESIGN §0
  item 8). The lean path measured 8-13 min end to end per three-window set on a free host with 10 workers
  (`docs/analysis/b5/RELEASE-RUNBOOK-lean.md:148-161`): **about 30-40 min** for block 6. The 1 h 40 min target holds
  only on the lean path, or on a heavy path that runs the three GAMMA units in parallel and skips step 1 by hash
  binding, which DLE-2 kept for the audit and did not adopt (DLE `:200-210`).

### F8. Is the recompute hash-independent? Yes on values, with three caveats

- It shares no code with L9 (`test_no_l9_import`, `tests/independent_recompute/test_comparator.py:805`), re-integrates
  raw power records under stored clock inputs, and the comparator verifies L9's output digests
  (`l9_output_digest_differs`). Under DLE-2 item 2 it binds anchors, fits, exclusions and the NEG-8 record by content
  hash rather than re-deriving them; the audit run is then "the only check of those judgments for block 6" (DLE
  `:185-188`).
- Caveat 1: `Reader.raw` reads bytes and records names; it does not authenticate them against the harvest or seal
  manifests (LEAN `:121`). Caveat 2: every block-6 raw plist is `.zst`; with `trace_plist_missing` a STOP flag the
  recompute stops on every session until it reads through `desk_compress.read_bytes` or runs inside the in-place
  restore (DESIGN §15 step 10). Caveat 3: the b_op fallback of F5.
- D-188's exact-equality standard (`docs/decision_log.md:12239-12250`) is for L9 versions against the r1 reference; it
  does not apply across lean and L9, where S-13 governs.

### F9. Estimand definitions: mostly sound, four gaps

1. **§9.5 item 5 / S-15.** REG says the per-phase whole-machine definition is "the one committed for block 5"
   (`:1030-1035`); B5-PLAN §8.2 is request-level and says "the harvest computes no phase-level figures"
   (`configs/campaigns/v5_claim_25g83/analysis_plan_block5.md:653`). The per-phase line exists only in the recompute
   (`machine_member`, `phase_machine_mean`). So S-15 cannot be filled by pointing at block 5, and today this line has
   one producer. DESIGN §8 (`:802-856`) is a written candidate definition (meter-only, battery at request level,
   edge-shift sensitivity δ = b_op + r_max, four corners).
2. **§10 edge cases.** The registration does not say what the summary prints when a session's Q is not computable, when
   n = 1, or when block 5 did not compute Q (for example the per-phase whole-machine value, which block 5's L9 never
   printed and which DESIGN §8 proposes to compute from block 5's archives after the release, a new block-5 number).
   B6-AN-1 ruling 1 and DESIGN §10 (`:866-890`) fix wordings; none is registered.
3. **§11.2 with `not_estimable` block-6 sessions.** "Otherwise not replicated" covers it, but a block-6
   `not_estimable` caused by a binding defect (F4) would print as "not replicated". The dry-run completion criterion
   must exclude that case.
4. **§8.3 item 3 / S-8 / S-9 / S-11.** The desk P* exclusion and the E_add alternative enter kept units, hence every
   estimand. PR #529's replay says 0 of 840 science runs reach the line (counts only, blind), so no number is expected
   to move; the registration still requires the computation and its S-9/S-11 values, and on main both slots are OPEN.
   All of P_x, T_phase, E_add and the counts are hazard structure, releasable now under §12.1 (`:1129-1133`).

### F10. Durability of the block-6 inputs

Block 6's collection code, catalog, acceptance, identity pins and pack registrations live only on a draft lane (PR
#502, CI-only, last updated 10-18) and the `b6/collection` tag; main was pruned on 11-06
(`archive/pre-prune-2026-11-06`). The analysis commit S-14 should carry `configs/b6/registration/*` and
`flag_catalog_b6.json` byte-identical to the S-3/S-4/S-18 digests, so that no analysis step depends on an unmerged
branch, and the §17 entry should cite the tag.

---

## 3. Registration amendments needed before any block-6 analysis (and before the block-5 unseal)

Each is one dated REG §17 entry under §12.4, signed blind with the DLE signing statement extended to block 6 (DLE
`:182`), checked by one executing refuter. Ordered by what blocks what.

| # | Amendment | Resolves | Changes registered arithmetic? |
|---|---|---|---|
| A1 | **Production program and agreement gate.** Name the program that prints (lean recompute per DLE-2) and the program that audits (L9 heavy, once). Replace §12.3 item 4's wording with: L9 and the lean program agree on every family of A3 within A2's bars; replace §13's post-release byte re-run with DLE-1-style digest re-verification; add the audit-unfinished rule (hold, or release labelled provisional) and the strict-refusal surface of the audit (DLE `:189-191`); state the dry-run completion criterion (exit 0, or a D-189 exit 3 whose refused floor resolutions a structure-only probe shows are not binding failures). | F1, F4, F9.3 | No (program and check only) |
| A2 | **S-13 made definite.** Either (a) adopt block 5's coded bar set (1e-6 relative J/W/ratios, 1e-6 absolute rho and p, exact counts and words) with the 1 mJ phase-energy bar as the registered ceiling, or (b) register a printed-decimals table per family. Add the five meter/machine families and every A3 family. Strike the `placeholder` set, and make `load_bars` refuse any set carrying `placeholder: true`. Register the FS3 tie rule for block 6. | F2 | No |
| A3 | **Printed-quantity table.** For every quantity of §9.5-§11.4 and the seven DLE-2 families: producer(s) (lean / L9 / both), comparator family, bar, and the label "not independently recomputed" where there is one producer (as RS item 83 ruling 3 did for block 5). Name the audit run as the supplier of any family the lean program does not print. | F3, F9.1 | No |
| A4 | **S-14 contents.** The analysis commit contains the D5 cause fix (campaign-log member parse) and D5b; the blind dry run runs step 9's floor binding on all three GAMMA units with their real paired sessions and prints per-cell bound flags (structure only) before the comparator; "all serving cells unbound" is a tooling refusal class, never an outcome. | F4 | No |
| A5 | **b_op for block 6.** Both programs recompose b_op from each session's stored captures under `acceptance.json` `ea130c87…` (s_bracket 10.818 ms); the harvest's stored bracket (block-5 acceptance) is disclosed beside it and enters no number; a difference beyond S-13 between stored captures and recomposed b_op is a refusal, not a fallback. | F5, section 1 | No (it restores the registered value) |
| A6 | **Exclusions and counting.** The exclusion function is the sealed `joulewise.flags.exclusions.compute` with catalog digest `b5bce6c6…` and no pack-scoped window reasons; counting is `derived/b6-acceptance.json` `counting` (and the loop record); `claim_usable` is never read; both programs refuse on disagreement. Tested on r2-gamma's structure. | F6 | No |
| A7 | **Session index and pairing table, registered as structure.** The nine session ids, rounds and t0 order; the pairing table of F4 (fixed by counting alone, REG §6.2); the tie rule (earlier t0). | F7 | No |
| A8 | **S-15 fill.** Adopt a written per-phase whole-machine definition (DESIGN §8 is the candidate), name both producers, and label block 5's per-phase value as computed after the block-5 release by the block-6 code. | F9.1 | New disclosure line only |
| A9 | **§10 and §11 edge cases.** Non-computable Q left out with n reduced and named; n = 1 prints "not defined"; "block 5: not computed"; per-token summarised per session. | F9.2 | No |
| A10 | **S-9 / S-11 / S-8.** Merge PR #529's §17 entry or re-enter it; register that P_x, T_phase, E_add and the removal counts are hazard structure computed and reported before the dry run; name the E_add code as part of S-14. | F9.4 | No (0 of 840 on replay) |
| A11 | **Inputs and reading.** Cite tag `b6/collection` (`f31aca19f`) and the S-3/S-4/S-18 digests; vendor those files into S-14; both programs read desk-compressed files through `desk_compress.read_bytes` or inside a verified in-place restore, and `trace_plist_missing` stays a STOP. | F8, F10 | No |
| A12 | **Fixtures.** The eleven production-shaped synthetic sessions generated by the measurement code at `f31aca19f` (DESIGN §16), covering re-measured idle baselines, wait-cap skips, compressed files and a cross-session GAMMA unit, are required before S-14 is cut. | F5 | No |

Timing recommendation under A1: run the three GAMMA units in parallel and extract each floor session once; keep
step 1 strict validation in the audit only. Expected: lean path about 30-40 min for all nine sessions; heavy audit
about 5 h plus restore I/O, off the critical path.

---

## 4. Open questions for the lead

1. Has the r4 PR (D5 cause) been opened? Nothing on GitHub or origin carries it at audit time; S-14 depends on it.
2. Does DLE-2 supersede DESIGN B6-1's L9-based build for block 6, or do both run with the lean program printing and
   L9 auditing? A1 needs that decision; the B6-AN-1 driver was built on a BYTES draft base and has no release mode.
3. Did the block-6 harvest's member-level phase checks (REG §8.3: "the timing bound is small against the phase length,
   and the attribution bound is at most a quarter of the phase energy") use the stored b_op under block 5's acceptance?
   DESIGN §0 item 7 says counting is unaffected; a counts-only replay of the phase checks under the registered b_op
   (hazard structure, blind) would settle whether any kept-unit set differs.
4. Who rules block 6's printed precision (A2 option b), or is option a preferred? The brief's "hash-independent" and
   "fast" goals are both better served by option a, which is already tested at full size.
5. Should block-6 amendments be permitted after the block-5 unseal at all? Given §12.3 item 2's rationale, I would
   register "no", which makes the A1-A12 window the next few days.

---

## 5. Lessons checklist (brief items, one line each)

| Lesson | Carried into block 6? |
|---|---|
| Monitor cost | No producer on the production path; no comparator row (F3) |
| Arm hazards | Same |
| Battery (phase/subject, discharged energy) | Same; plus `battery.assist_outside_request` new in the b6 catalog |
| Battery temperature | Same |
| Reference / corpus / NEG-8 | Gross terms recomputed; history and screen not; D6 conditional landed |
| Attempt history (block 5's and block 6's, REG §9.5) | Not recomputed; L9 history check is against the block-5 index only |
| Selection | Pairing and counting are registered rules but no program implements them on main (F6, F7) |
| D1 L9 key bug | Fixed in r3 |
| D2 idle attempt | Fixed in recompute; untested on block-6 driver shapes |
| D3 unanchored members | Fixed |
| D4 no measured request | Fixed; wait-cap skips untested |
| D5 campaign-log parse | Cause found; fix in no pinned commit; block 6 triples the exposure (F4) |
| D6 NEG-8 protocol | Fixed; stored-bracket acceptance mismatch is the block-6 analogue (F5) |
| Estimands well defined | Estimators 1-4 yes; S-15, §10 edge cases, S-13 precision no (F2, F9) |
| Recompute hash-independent | Yes on values; input authentication, compressed reads and b_op fallback are the caveats (F8) |
| Comparator covers every family | No (F3) |
| Runs fast | Lean path yes (30-40 min); heavy path about 5 h unless parallel per unit (F7) |
