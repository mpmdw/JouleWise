# Claude build brief B6 (BYTES; magistrate activation 4ec5d597, 2026-10-20)

Code: the public JouleWise clone at /tmp/jw. Fetch every branch, then
`git -C /tmp/jw checkout -b docs/2026-10-20-bytes-registration d924e7acf` (B1's verified head on `lane/2026-10-20-bytes-integration`; stop if the
commit is missing). You can push only to this JouleWise-data repository, so deliver the JouleWise-side work as commits
on that local branch, exported with `git -C /tmp/jw format-patch d924e7acf..HEAD -o <this repo>/ports/b6/`
and committed on your report branch; the lead applies the series to `docs/2026-10-20-bytes-registration` on JouleWise. Re-export after every commit
you keep. The patches must apply cleanly with `git am` on d924e7acf.
Test with JW_B5_SYNTHETIC_ONLY=1 and a fresh TMPDIR (the setup script sets both). Run only the modules you touch plus
the registry tests. Environmental failures (zombie PID in the orphan census, /private/tmp, launchd) are listed, not chased.

Context: the brief below was written by a status audit (this repo, branch `claude/bytes-status-c634`,
`reports/bytes-status-c634/BYTES-STATUS.md`; read its §1-§3) and checked by the lead. B1 is finished: read its report
(branch `codex/bytes-b1-report`, `reports/bytes-b1/REPORT.md`), in particular decision 5: the CLI stage names are
`--stage blinded`, `--stage fit` (stage 1) and `--stage heldout` (stage 2). B2, B4, B5 run in parallel as Sol seats
on lanes `lane/2026-10-20-bytes-analysis-a8`, `lane/2026-10-20-b6-blinding-group`, `lane/2026-10-20-bytes-mac-kit`.

Decide anything the governing texts determine and list it under "decisions I made". NEEDS_RULING only for a choice that
changes which data count or a printed number; record it with the evidence and continue with the rest. Report file:
`reports/b6/REPORT.md` with commits, tests run with counts, decisions I made, NEEDS_RULING (or "none").

The blinding ruling is in (below): state it in the registration as ruled, with its item 6 replacing Addendum 7's
"including the blinded one" for held-out models. Write correct, plain prose a reader can rebuild the analysis from:
every term of art is defined at first use, every number carries its source or derivation. B2's coverage numbers and the
estimator sha256 are not ready: use marked slots `⟦B2: …⟧` and `⟦MAC: …⟧` as the brief says.

## Lead ruling on BYTES blinding (2026-10-20, two blind seats agreed; you build it, you do not re-rule it)

Problem: every H1 word is unchanged by a common factor, so only the configuration factor U(0.97, 1.03) hides the
words; configuration ratios stay visible to about ±6%, while the MoE hypotheses differ by factors of 8 to 19, so the
active-or-resident answer is readable from the blinded export before the predictions are committed.

1. A held-out configuration's rows never enter the analysis export before the stage-1 hash is recorded. They are
   written, already blinded, to a withheld store under the pack-group records root; the export sidecar records only
   counts and key digests of withheld rows.
2. Timing closure: pre-commit visible rows carry no `run_start_utc` or other clocks that would let
   reference-to-reference gaps reveal a withheld module's duration; any ordering the analysis or twin needs uses the
   registered pass identity (pass id, position in the registered plan tree), not clocks.
3. Before the stage-1 commit, the blinded agreement (analysis vs twin) covers the fit set, references and NEG-8 on real
   data; held-out paths are exercised on production-shaped synthetic campaigns. After the stage-1 commit and before
   held-out keys are released, both implementations run on the real held-out blinded rows. No sealed pass/fail
   agreement script is built.
4. A missing withheld file prints as a flag and the model prints as `missing`; it is never a refusal (project doctrine:
   only a physical hazard refuses; everything else is a recorded flag).
5. Wider blinding factors are rejected.
6. The registration's agreement statement replaces Addendum 7's "including the blinded one" for held-out models.
Out of scope here: `idle_power_w` is scaled by the configuration factor, so its ratio to reference rows estimates the
factor. That leak is queued for every block-6 pack separately; do not change idle-power handling in this round, but if
your work touches it, record what you saw.
NO SILLY NUMBERS (project rule, binding): every tolerance, threshold, comparison bar or test assertion on a measured or
derived quantity carries its derivation in a comment beside it, from the quantity's physics (about 1 J attribution
limit per run, the meter's resolution, the sample interval) or its printed precision. An agreement bar sits between
1e6 times float noise and 1% of the smallest printed uncertainty; where a cell has a half-width, 1% of it (Addendum 8
uses 1% of (h + B) for energies). With no half-width, 1e-6 relative or absolute in the column's unit. Exact equality
only where bit-identity is the real property (integers, hashes, labels, identical code on identical inputs). A method
difference that is small on synthetic data is caught by making the synthetic world exercise it above the bar, never by
tightening the bar. You do not choose your own bar: use the ones stated here and in §5 below.
### Rules common to every brief

Paste these with each brief.

- **Repository.** JouleWise, public clone. Seat setup: `bash tools/cloud/seat_setup.sh /tmp/jw && source /tmp/jw-seat.env` (JouleWise-data). Fetch every branch.
- **Branching.** Work on the branch the brief names. Never push to `main`, to a `lane/2026-10-14-b6-*` branch or to `integration/*`.
- **Authority order.** Unless a brief says otherwise, use this order. A higher entry wins over a lower one, and a later BYTES addendum wins over an earlier one and over R1-R8:
  1. BYTES ruling Addendum 8, then 7, 6, 5, 4, 3, 2, 1, then R1-R8 (`docs/design/bytes_pack_design.md` @ `298a292a7`).
  2. The block-6 registration (`docs/registrations/block6_replication_DRAFT.md` on main, "Registered"), for anything that changes behaviour on the replication packs alpha, beta and gamma. Those packs must behave byte-identically.
  3. Block-6 design `docs/design/block6_collection_draft.md` §14-17.
  4. Block 5's registered arithmetic (`configs/campaigns/v5_claim_25g83/analysis_plan_block5.md` and its library). This one wins on arithmetic: Addendum 1.1 and Addendum 7 D8 both defer to it.
- **Safety switch.** Run every test with `JW_B5_SYNTHETIC_ONLY=1` (it is in `/tmp/jw-seat.env`). Never point a harvest or analysis test at a real archive or key directory.
- **Synthetic data end to end.** Generate production-shaped synthetic data (`tests/fixtures/bytes/campaign.py`: full-size modules, 50 runs per model per pass, start/midpoint/end references, a 10 Hz meter stream). Run it end to end through the real stage chain: harvest export (`joulewise/b6/export_runs.export`) → blinded export → `scripts/bytes_analyze.py --stage blinded` → stage-1 release → `--stage 1` → stage-2 release → `--stage 2`. No stage may be bypassed by a direct function call in the end-to-end test.
- **Tests.** Run only the modules you touched, plus the registry tests below: `python3.13 -m pytest <modules> -q`. Do not run the whole suite (it is run on the Mac, Addendum 2). If PyPI is blocked, use `PYTHONPATH=/root/.local/share/uv/tools/pytest/lib/python3.13/site-packages`. Environmental failures (`/private/tmp`, launchd, powermetrics, fixture `git commit` exit 128) are listed, not chased.
- **Registries.** If you add a module, or a raise, exit or refusal to a scanned module, run `python3.13 -m tests.hazards.refusal_census` and add each printed entry to `configs/gates/hazard_refusals.json`. Category is PHYSICS, NUMBER_INTEGRITY or INTERNAL; never BASELINE.
  - A new module imported by a scanned module goes into `scan.modules`, or into `scan.not_scanned` with a reason from `not_scanned_reasons`.
  - Always run: `tests/hazards/test_refusal_allowlist.py`, `tests/hazards/test_import_graph.py`, `tests/test_fixture_orphan_census.py`, `tests/test_digest_pin_census.py`, `tests/test_schemas.py`.
  - Never edit a path in `joulewise/b6/registration.py` `NUMBER_BEARING_PATHS`. If a change there seems needed, stop and report NEEDS_RULING: such a change would need an executing review entered in `configs/b6/executing_reviews.json`.
- **Bars.** Every tolerance you add states its derivation in a comment (§5). The bar sits between 1e6 × float noise and 1% of the smallest printed half-width, or 1% of the cell's (h + B) where the cell has one (Addendum 8).
- **Decisions.** Decide anything the governing texts determine, and list it in your report under "decisions I made". Use NEEDS_RULING only for a choice that changes which data count or a printed number.
- **Report.** Write it on the JouleWise-data report branch the lead names. Its first line is your model id. It holds: commits, tests run with counts, decisions I made, NEEDS_RULING (or "none").

### B6. Registration prose: `docs/registrations/bytes_pack_v1.md` (blocker L, and F's slot)

- **Goal.** Write the registration as prose that replaces the ruling.
  - **Contents.** R1-R6 as amended by Addenda 1-8, the two-stage unblinding, the multiplicity (k = 9, 9, 11), the one-pass fallback (Addendum 7 D9), the agreement bar (Addendum 8), and the dependencies Addendum 4.8(e) and 4.11 require stated.
  - **Notes.** Addendum 5.5's notes: HF snapshot symlinks, 8B-8bit group size unverified, the s5/s6 midpoint, fixed packs bypassing the 265-min cap.
  - **Printed precision.** Fix the printed decimals of every table (§5 F13). The Addendum 8 bar for quantities without a half-width depends on them.
  - **Mac slots.** Every Mac-dependent value is a marked slot `⟦MAC: …⟧`: the manifest hash and KV values, 8B-8bit kept or dropped, C4 pins, C5 gates, test 7 outcomes, contention level. The same goes for `estimators` (the sha256 of `bytes_analysis.py` at the agreeing pin, from B2/B3).
  - **Blinding.** If the lead's ruling on finding B is in, state it. Otherwise leave a NEEDS_RULING slot.
- **Branch.** `docs/2026-10-2x-bytes-registration`, from B1.
- **Governing texts.** The common order. The ruling text is the content. Block-6 design §14 defines what a pack registration contains, and §14 wins on form.
- **WRITE_SCOPE.** `docs/registrations/bytes_pack_v1.md`. `configs/b6/packs/bytes-s*-p*/registration.json` only for `estimators` and `draft_notes` text, regenerated through `scripts/bytes_plan_trees.py`. Tests: `tests/b6/test_bytes_packs.py`.
- **Done when.** Every R and Addendum item maps to a paragraph, as a table at the end. No number appears without its source or derivation. Mac slots are listed.

## 5. Tolerances: proposals and flags

### Scales used

| Quantity | Value |
|---|---|
| Float noise | ε = 2.2e-16 relative |
| Decode energies E | ≤ about 1e4 J (70B: about 64 s × ≤ 100 W at the pilot rate) |
| 1e6 · ε · E | ≤ 2.2e-6 J |
| Smallest printed half-width | 0.013 J, 1.7B rails (Addendum 8) |
| 1% of it | 1.3e-4 J |
| Admissible window for an absolute energy bar | [2.2e-6, 1.3e-4] J; per cell, 1% of (h + B) |

### Proposals

| # | Bar | Derivation |
|---|---|---|
| P1 | Agreement (B3): 1% of the cell's (h + B) for energies; 1% of the half-width for P̄ and HC3 coefficients; exact for words, counts and labels | Addendum 8.1/8.5. At the smallest cell, 1.3e-4 J ≥ 1e6·ε·E. |
| P2 | Blinding round trip (B4): \|x′ − x\| ≤ 1e-9·\|x\| | The round trip is 2 roundings per degree. Noise is ≤ 4.4e-16 relative (degree 2, `_j2`/`_w2`), and 1e6 times that is 4.4e-10 < 1e-9. At the upper end, 1e-9 × 1e4 J = 1e-5 J < 1.3e-4 J, the 1% of the smallest half-width. This is not Addendum 8's objection: it is one implementation's multiply and divide, not two summation orders. |
| P3 | D3 exercise (B2): the method gap is ≥ 0.10 · B_rest in every rest cell | 10× the 1% bar (Addendum 8.4), so a method difference sits ≥ 10 bars above the threshold. |
| P4 | Synthetic recovery (B2): \|estimate − truth\| ≤ the cell's own (h + B), judged as coverage over campaigns, not per cell | That is the interval's claim. Coverage bar 0.93 = 0.95 − 2·√(0.95·0.05/400) = 0.928, the binomial 2-SE floor for the 400-draw harness. This supplies Addendum 4.5's missing derivation. |
| P5 | Manifest W, R, KV: integer bytes, exact | They are counts of stored bytes (R4). The printed GB is derived from them. |
| P6 | C5 sizing margin: the largest measured run-to-run spread of request seconds in the R8.6 session (max/min − 1 over its 5 runs, 12 for soaks) | Replaces Addendum 5's planning "20%" with a measured quantity. |

### Numbers already in the BYTES code or ruling without a stated derivation

| # | Where | Number | Issue | Fix |
|---|---|---|---|---|
| F1 | `tests/test_bytes_analysis.py:1167,1170` | `places=13` (5e-14 J), slack `1e-12` | Below the 1e6·ε floor for J-scale values (about 2e-10 J at 1 J). It would fail on a summation-order change (Addendum 8.3). | 1e6·ε·\|x\|, or 1% of the cell's B |
| F2 | `tests/test_bytes_analysis.py:328` | `delta=.03` on λ = 0.4 | No derivation | λ's HC3 half-width in that world |
| F3 | `tests/test_bytes_analysis.py:186-187` | `delta=.00005` on interval endpoints | No derivation | Printed precision, or 1e6·ε·\|x\| |
| F4 | `tests/test_bytes_analysis.py:420` | `delta=1e-3` J, meter = 2·rails | No derivation | From the generator's 10 Hz integration error |
| F5 | `tests/fixtures/bytes/campaign.py:102` | `rel_tol=1e-7`, reducer vs. generator | No derivation | — |
| F6 | `tests/test_bytes_analysis.py` (throughout) | default `assertAlmostEqual`, 7 absolute places | Magnitude-blind. Acceptable only on O(1) worked examples, and that should be said. | — |
| F7 | `joulewise/bytes_analysis.py:124,164` | `1e-12` absolute pivot and leverage guards | No derivation | A relative guard n·ε·max\|a\| on the scaled matrix, or a stated reason |
| F8 | `tests/fixtures/bytes/campaign.py:73` | Synthetic decode noise 0.2% (`gauss(0,.002)`) | Not tied to a measured spread | Block-5 repeat CV, or the pilot's |
| F9 | Addendum 4.5 | Coverage threshold 0.93 | Derivation not stated | See P4 |
| F10 | R6, and `joulewise/b6/registration.py` `cell_unit_minimum: 5` | At least 5 kept units per stratum | Inherited from block 6; the BYTES text gives no derivation | The registration cites its source |
| F11 | Addendum 5 and pack `draft_notes` | 20% planning margin; s4's 11 min of headroom | Planning only | Replaced by C5 (P6) |
| F12 | R6 | 150 GiB disk reserve | Operational (design §15), no derivation | Cite as operational |
| F13 | Addendum 8.5 | Durations to 1 ms; VIF to 2 significant figures | "Printed precision" is undefined: `bytes_analysis` writes full-precision JSON and no table fixes decimals | B6 fixes printed decimals; the bars follow |
| F14 | `joulewise/b6/blinding.py` | Pack U(0.8, 1.25), configuration U(0.97, 1.03) | Sized for replication contrasts, not BYTES's 8-19× MoE splits | Finding B, lead's ruling |
| F15 | R1 | "32-fold" and "69-fold" ranges | Derived from the pilot column | Recompute from the frozen manifest before the registration prints them |

Derived, and no flag needed:
- `bytes_analysis.py:839` `2.262157162798205` is t₀.₉₇₅,₉, mirroring the block-5 library.
- R6's P_limit = F_min/(4·T_max) is derived in the ruling.
