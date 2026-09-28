# S1-REGRESSION-01 — Opus 5.5 blind consult seat

Seat: Opus 5.5, blind, read-only. I opened no other seat's answer and no RUN_STATE, CLAUDE, AGENTS, memory or skill file. The harness placed the global and project `CLAUDE.md` and the memory index in my context before the charge arrived. I used none of them for a ruling below. Scratch: `/tmp/s1-consult-opus-77b1bee2/`. `git status --short` on the integration tree printed 0 lines before and after every probe.

**What I read:** the charge; the scout report and inventory; the final-pass ruling (`51-fable-finalpass-ruling.md`), in full; Final texts v1.1 §2 and §C to §F (`21-coldgate-fable-addendum-ruling.md:36-233`); grep hits in the SWEEPCLASS and RETURNS rulings for `mock`, `not_applicable`, `non_claim` and `full suite`; the decompressed row-9 log; and the production lines cited below, read on `/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2` at `42e2af3e`.

## 0. Terms

- **Row 9.** The full test suite: 270 modules and 7,647 tests in six shards, run on the **integration tree**, meaning S1's head merged with current main. It gave 115 failures and 418 errors, and the log reports 108 skips.
- **Mock member.** A bundle whose `config.json` has `telemetry_backend == "mock"`. Its energy numbers come from a synthetic adapter, not from a meter. Text 8 (iii) has the reader admit it with status `not_applicable`. That decision uses only the `config.json` whose digest `metadata.config_sha256` binds.
- **Mock window.** A window in which **every** member that owes a battery pair has status `not_applicable`. A window that holds at least one mock member and at least one member of any other status is a **mixed window**.
- **Claim artifact.** Any output from which a paper number is taken, such as a whole-window verdict, a minted floor, a claim verdict or a scored reduction.
- **Evidence-forward repair.** A test is fixed by giving its fixture the evidence the gate now asks for (an authenticated pair, a bound config, real capture bytes, an injected probe runner), and **its original assertion stays unchanged**. The alternative is an **expectation rewrite**, where the assertion itself is changed.

## 1. Executed evidence (this session)

| Id | Probe | Result |
|---|---|---|
| X1 | `sed -n 282,354p joulewise/bundle_read.py` | `authenticate_window_members` appends every `not_applicable` verdict to `refused` (`:344-351`) and raises `WindowBatteryRefusal` (`:352-353`). The function has no parameter and makes no distinction between claim and non-claim use. The class docstring reads "Every named non-pass member in a claim-bearing window" (`:213`). |
| X2 | `sed -n 9018,9086p scripts/run_campaign.py` | The gate call at `:9032` comes **before** `claim_bearing` is computed (`:9043-9047`) and before `append_verdict` (`:9068`). `battery_float_members` is written from the verdicts (`:9083-9085`), but a verdict can never be `not_applicable`, because X1 raises first. |
| X3 | Frames of every `not_applicable` refusal in the row-9 log | 44 at `run_campaign.py:9032`, 34 at `inputs.py:3195`, 12 at `aggregate.py:104`, 3 at `inputs.py:2824`, 2 at `whole_window.py:680`, 2 at `run_campaign.py:7848`, 1 at `:6256`. |
| X4 | Grep for mock configs under `configs/` | Only `configs/examples/mock_*.json` and `mac_mlx_mock_telemetry.json`. The README quickstart (`README.md:188-198`) runs the mock target. |
| X5 | Grep for independent mock barriers | `inputs.py:170` `MOCK_TELEMETRY_CLAIM_REFUSAL = "mock_telemetry_claim_ineligible"`, appended at `:1944` and `:2890`. The code is registered as a reducer barrier (`claims.py:50`) and as a lock (`reason_kinds.py:64`). `whole_window.py:3557-3572` admits to strict claims only summaries that are non-mock by the custody-bound config. |
| X6 | `mockrule.py`: X1 wrapped **in memory only**, so that a window whose members are all `not_applicable` returns its verdicts and every other refusal still raises; the wrapper is installed into the eight consumer modules; then `tests.test_experiment`, `tests.test_corpus_strict_validation` and `tests.test_collector_analysis_manifest_id` are run | 58 tests, 7 failures. Those 7 all run the campaign in a **subprocess**, which the in-memory patch cannot reach. One was re-run and its traceback shows `WindowBatteryRefusal` with 40 labels, all `not_applicable`. The 12 G2 outcomes of `test_experiment` and the 3 of `test_corpus_strict_validation` passed. |
| X7 | `supply_map.json`, parsed | All five roles are `fixture.*`, with `mode = "test_fixture_non_issuing"` and `issuance_gate_id = null`. The two production roles are still in `pending_roles`. `docs/contracts/paper_supply_custody.md:196-202` says: "The fixed map currently registers five synthetic roles only… synthetic authentication controls." |
| X8 | `git log -- configs/paper_supply/supply_map.json` | Four earlier commits (`6e380f55`, `21331ac9`, `31f39466`, `6c34cfe6`) were "hash-only repin" commits made **in the same PR** that changed validator sources. |
| X9 | `paper_custody.py:846-858`, `:1288-1298` | The receipt digest is `sha256` over family, policy constants, and `inspect.getsource` of every census member and its whole owning module. Any byte change in `inputs.py` or `whole_window.py` therefore moves the three families' pins. That drift is by design. |
| X10 | `arm_readiness_evidence.py:2446-2466` | S3's `THREE_WINDOW_REGRESSION` derivation runs `tests.test_calibration_live_three_window` and records `PASS`. The row-9 log shows that suite failing on S1 (G6, 20 errors; G11 `EvidenceAuthoringError: focused suite refused: … errors=20`). |
| X11 | §E exclusion list compared with the inventory | The failing modules include `tests/test_mint_floor_artifact.py`, `tests/test_mint_floor_artifact_generalized.py` (G3 10 + G5 11 = 21) and `tests/test_calibration_bracketing.py` (G7 6). All three are in §E's "Excluded and asserted byte-identical by S1's pin test" list. `tests/test_calibration_live_three_window.py:61` imports `tests.receipt_corpus`, which is also excluded. `configs/paper_supply/supply_map.json` is not in S1's WRITE_SCOPE. |
| X12 | `test_run_campaign.py:5853-5876` and `run_campaign.py:9020-9032` | The fixture makes `(runs_dir / "incomplete").mkdir()`, an empty directory. Member selection takes it because it satisfies `bundle_path.is_dir()`, and the gate raises `CustodyUnreadable` on the missing `metadata.json`. The campaign exits without its verdict row (`KeyError: 'collection'`). On main that row records `invalid`. |
| X13 | `whole_window.py:4448-4454` | `BundleReader(path).measured_window()` now calls the gate first (text 8). Its `BundleReadError` is caught by the existing handler and reported as **`environment_admission_missing`**. That is why `test_whole_window_selection.py:1179`/`:1257` now see `('environment_admission_missing', …)`. |
| X14 | `controller.py:893-897` | `runner=self._battery_runner`, which defaults to `None` and so means the real `ioreg` probe. The 11 G10 tests therefore probed the laptop running the suite. |

**Not executed:** the full suite on main, and any repair. X6 only stands in for the G2 rule; it is not the rule. No claim writer was driven with a mock window: the barrier in X5 was read, not run.

## 2. G2 — what a mock member does at window scope

**What Final texts v1.1 says.**
- Text 8 (iii): the **reader** admits a bound mock bundle as `not_applicable`.
- Text 12: "Every consumer that builds a set of bundles **whose numbers are claimed** … refuses the whole set … on any … `not_applicable`". Its last sentence: "`unobserved_historical` and `not_applicable` are visible in every window-level output."
- Text 18: "a MOCK bundle reduces as today."
- Text 9: the scored reducer counts `not_applicable` as non-pass.
- M3 (`:42`): "text 12 refuses `not_applicable`".

**The contradiction, executed (X1, X2).** As implemented, the last sentence of text 12 cannot be met. Every window output built after the gate (`aggregate.py` `battery_float_members`, `run_campaign.py:9083`) is reached only when no member is `not_applicable`. So `not_applicable` is never visible in any window-level output. The text therefore presumes some window-level path that admits `not_applicable`. The only reading consistent with "whose numbers are claimed" is that this path is the set whose numbers **cannot** be claimed. S1 implemented one function with no such path. That makes every call of all eight consumers claim-bearing, which is stricter than the text and breaks its last sentence.

**The options.**
- **(A) Keep refusing and rewrite the 98 tests to expect refusal.** No production change. But it deletes the hermetic end-to-end coverage of everything that runs after the gate: collection-verdict classification, claim readiness, aggregate statistics, and the analysis-integration pipeline. That is weakening assertions at scale, not preserving them. It also breaks the README's mock workflow for `experiment` and campaigns (X4) and contradicts text 18's intent. **Rejected.**
- **(B) A caller-declared `claim_bearing` or `admit_mock` flag at each call site.** It touches about 20 call sites in 8 files, and the gate's strictness becomes a property of each caller. That is the idiom text 12 avoided. **Rejected** as more production change for less strictness.
- **(C) A rule decided by the data, in one function: the mock window.** **Recommended.**

**Proposed ruled text (12a), for the cold gate.**

> **12a. Mock window.** In `authenticate_window_members`, a window with at least one member that owes a pair, and in which every such member's verdict is `not_applicable` under text 8 (iii), is a **mock window**. The function returns its verdicts without raising, and each verdict appears as `not_applicable` in the window-level output (text 12, last sentence). In every other window, text 12 applies unchanged: a mixed window refuses on each `not_applicable` member, and `confounded`, `evidence_missing` and `CustodyFailure` refuse everywhere, mock window or not. Text 9 is unchanged: the scored reducer refuses `not_applicable`. No claim artifact is built from a mock window. The independent barrier is `mock_telemetry_claim_ineligible` (`inputs.py:170`, `:1944`, `:2890`), which comes from the same custody-bound config (`whole_window.py:3557-3572`).

**Why (C) keeps the gate strict for anything claim-bearing.** The battery gate exists because charging current confounds a *physical* energy measurement. A mock window contains no physical measurement to confound. Its numbers already carry a separate, config-bound claim lock (X5). Any window containing even one real bundle still refuses every mock member, so text 12's protection against mixing is intact. The status is decided from the digest-bound config (text 8 (iii)), so a bundle cannot become "mock" without changing `config_sha256` and with it `complete_bundle_sha256`.

**Size.** About 8 lines in `joulewise/bundle_read.py`, which is inside S1's WRITE_SCOPE. No call site changes. X6 shows the shape clears the G2 signature in-process.

**Owed with it (defect-shaped checks):**
- **(M-1) Mixed window.** One mock member plus one passing real member refuses and names the mock member.
- **(M-2) Mock plus historical.** A mock member plus an `unobserved_historical` member refuses.
- **(M-3) Empty window.** A window with no obligated member returns `{}`, as it does today, and is not treated as a mock window.
- **(M-4) Claim writers.** A mock window is driven through each claim-artifact writer (whole-window verdict writer, floor mint, analysis finalizer claim verdicts, scored `reduce`). Each must refuse with a named reason, `mock_telemetry_claim_ineligible` or text 9's code. **If any writer emits a claim artifact from a mock window, (C) is inadmissible for that consumer**, and that consumer passes a `strict=True` keyword, so the exception is carved per consumer rather than the rule weakened.
- **(M-5) Visibility.** `test_experiment` shows `battery_float_members` values equal to `not_applicable` for a mock experiment.

**Authority.** Rule 12a reinterprets a ruled text, so it goes to a cold gate. I recommend one packet for G2, G9 and the scope grant of §4. A lead ruling alone is not enough.

## 3. G9 — who repins the paper supply-map receipts, and when

**What the pins are (X7, X9).** They are digests of **synthetic, non-issuing fixture receipts**. Each digest covers the validator source code. It is a tripwire on code identity: it goes stale, by design, whenever an owning module changes. No production role has been issued, so **no real paper receipt is invalidated**. The receipts are close to claims because they belong to the paper-custody system. They are not claim artifacts.

- **Which PR.** The same PR as S1. Precedent: four earlier hash-only repins in the PR that moved the sources (X8). A separate PR cannot be correct before S1 merges, since the new digest needs S1's bytes. If it lands after S1, main is red in between.
- **Order.** The repin is the **last commit before the new final pass**. It follows every production change, including the 12a edit and any fixture-driven production fix, because any later byte in `inputs.py` or `whole_window.py` would make it stale again.
- **Who.** The lead, at the bench: the change is a regenerated hash and is smaller than the contract needed to delegate it. It needs a named WRITE_SCOPE grant for `configs/paper_supply/supply_map.json` (§4).
- **Review needed (mechanical; no content review, because no production role exists):**
  1. The diff touches only `expected_sha256` values in `fixture.d165_closeout`, `fixture.reported_energy_parents` and `fixture.whole_window_verdict` (receipt and inventory rows). Modes, `issuance_gate_id`, subjects, `pending_roles` and every other role are byte-identical.
  2. **Generator check, both directions.** The regeneration script reproduces **main's** current pins from main's source, and the new pins from the candidate's source.
  3. The 23 G9 outcomes turn GREEN, and nothing else in `test_paper_*` changes.

  One refuter checks 1 and 2 as part of the delta audit.
- **Standing note for the record.** The day a `production.*` role is issued, a source change will invalidate a **real** receipt. From then on, a repin is a re-issuance under that role's issuance gate, not a hash edit.

## 4. The fixture-repair plan (G1, G3–G8, G10, G11)

### 4.1 Scope collision first (BLOCKER B3)

§E excludes from S1 three failing test files and one helper that a repair must edit (X11), and it does not grant the supply map. §E is exhaustive. The final pass read it as limiting what **S1 writes**, and the repair lands on S1's branch. After 12a and the 204424e6 fence, no guard sees post-`204424e6` commits; only WRITE_SCOPE enforcement does. So the cold gate must grant **by name**:
- `tests/test_mint_floor_artifact.py`
- `tests/test_mint_floor_artifact_generalized.py`
- `tests/test_calibration_bracketing.py`
- `tests/receipt_corpus.py` (only if the G6/G7 seat shows it must change)
- `configs/paper_supply/supply_map.json`

The grant holds under the no-weakening rules of §4.3. The four raw-capture tripwire scripts stay excluded. `validate_powermetrics_fiducial.py` is imported by the G6 test and must stay byte-identical.

### 4.2 Ordered steps

0. **12a lands first** (bench or small seat: `joulewise/bundle_read.py` plus M-1 to M-5 in `tests/test_bfgs_window_consumers.py`). It clears about 98 outcomes and changes what the remaining ones look like, so the repair seats work against the real residue.
1. **Shared helper, one seat.** Extract `WindowMembersTests.pair_bundle` (`tests/test_bfgs_window_consumers.py:30-60`) into a new `tests/battery_fixtures.py`. It holds:
   - `write_passing_pair(bundle)` and `write_charging_pair(bundle)`: raw `ioreg` bytes plus `raw_stdout_sha256`;
   - `bind_config(bundle)`: rewrites `config.json` and `metadata.config_sha256` after a fixture mutates it;
   - `write_capture_evidence(dir)`: real `instrument_evidence.json` bytes with their digest, plus a capture pair;
   - `FLOAT_RUNNER`: a deterministic injected `battery_runner`.

   The helper's own tests are counterfactual: a helper bundle passes the gate; one raw byte flipped raises `CustodyFailure`; the charging pair gives `battery_float_confounded`; the config changed after binding refuses.
2. **Parallel seats**, with disjoint WRITE_SCOPEs and the helper read-only. Per-seat scope is exactly the listed test modules.
   - **Seat A, campaign and analysis:** `test_run_campaign`, `test_analysis_integration`, `test_analysis_finalizer`, `test_analysis_claims`, `test_collector_analysis_manifest_id`, `test_experiment`, `test_pipeline_smoke_tail`, `test_corpus_strict_validation`.
   - **Seat B, floor and mint:** `test_floor_extraction`, `test_mint_floor_artifact`, `test_mint_floor_artifact_generalized`, `test_floor_mint_estimator`, `test_detection_floor`, `test_d117_floor_qwen25_{1p5b,7b}_plan`, `test_uncertainty_p2029`, `test_aggregate`, `test_custody_mode_inventory`.
   - **Seat C, whole window and calibration:** `test_whole_window`, `test_whole_window_selection`, `test_d165_dominance_closeout`, `test_dominance_closeout`, `test_check_window_provenance`, `test_bracket_binding_cli`, `test_calibration_live_three_window`, `test_calibration_bracketing`, `test_epoch_continuation`, `test_p2038_production_path`, `test_window_duration_margins`, `test_phase_share`, `test_launch_window`, `test_arm_readiness_evidence_author`, `test_arm_readiness_dry_run`; also `tests/receipt_corpus.py` if granted. **G6 is on S3's critical path (X10).**
   - **Seat D, CLI and controller:** `test_cli_run`, `test_cli`, `test_audit_amplification`, `test_powermetrics`, `test_package_bundle_pack`, `test_partial_record_enclosure`, `test_paper_reported_energy` (G9 only; no edit expected).
3. **Seat-level stop rules.**
   - A test whose fix seems to need a production edit, or a new injection hook (for example a G10 test that runs the CLI in a subprocess, so no runner can be injected), returns `NEEDS_RULING`. It never adds an environment-variable hook.
   - A seat never adds a run ID to `historical_bundles.json`.
4. **G9 repin** at the bench (§3), last.
5. **Row 9** on the integration tree (candidate ⊕ current main), same `TMPDIR` form as main's reference run (scout F3). Required: 0 failures, 0 errors, and **skip count equal to main's** on the same host.
6. **Delta refuter** on the repair diff (`c7593edb..new head`), then the **new cold final pass**. The MERGE on `c7593edb` does not carry over, because its A4 composition premise did not cover the merged tree (`51-…:83`, `:386`).

### 4.3 How no assertion is weakened (mechanical, run by the lead, not the seats)

**Default: evidence-forward.** An expectation rewrite (**R-list**) is allowed only where the test's *subject* is the member state the gate now refuses. Each R-entry is listed by test ID in the seat report and approved by the lead. It must assert the specific exception type, the member label and the status. `assertRaises(Exception)` is never acceptable. When the old assertion covered logic *after* the gate, that coverage moves to a sibling test with evidence: **split, don't delete**. Two concrete cases:
- The five `KeyError: 'collection'` tests (X12) assert the refusal at campaign level. Their collection-classification assertions move to a direct `classify_campaign_members` / `collection_verdict_for` test.
- `test_whole_window_selection.py:1179`, `:1257` keep `()`: their fixtures get evidence. They must **not** be rewritten to expect `environment_admission_missing`, which is a mislabeled battery refusal (X13).

**Checks:**
1. **Assertion census.** An AST script counts `self.assert*` / `assert` calls and their literal expected arguments, per test function, main against the repair. Any decrease or changed literal outside the R-list fails.
2. **Banned-construct grep over the diff.** Patching or mocking any of `authenticate_window_members`, `_battery_verdict`, `BundleReader.metadata`, `battery_float.authenticate_*`, `HISTORICAL_BUNDLE_SET_SHA256`, `BFGS_HISTORICAL_*`; a new `_allow_unissued_fixture=True`; `skip*` / `expectedFailure`; `except` around an assertion; `assertRaises(Exception|BaseException)`.
3. **Production diff.** `git diff --name-only c7593edb HEAD -- joulewise scripts configs` equals exactly `{joulewise/bundle_read.py, configs/paper_supply/supply_map.json}`.
4. `scripts/build_battery_float_historical_bundles.py --check` prints `entries=69`, byte-identical.
5. **Counterfactuals, one per group.** A planted defect must turn a repaired test RED:
   - G1/G8: charging pair.
   - G4/G5: one config byte after binding.
   - G6/G7: evidence bytes swapped or deleted.
   - G10: runner removed and `ioreg` stubbed to exit 1.
   - G2: mixed window (M-1).
6. **Hermeticity (text 18).** The G10 modules and every module that reaches `_stage_reduce` stay GREEN with `ioreg` absent from `PATH`. Today their result depends on the charge state of the laptop running them (X14).

**Sizing.** One helper seat, then **four parallel seats** (A to D). One seat for about 300 residual outcomes across 40 modules would be slow and would dilute the per-module R-list judgment. More than four would collide on shared modules. The seats are high effort, not xhigh: the work is mechanical once the helper exists. Seat C's G6 work is judgment-dense (ledger, receipt and sequence digests), so escalate C alone if its first report shows it.

## 5. Process — the single change

**No refuter pass or cold gate may be charged on a head without a recorded row-9 run (full suite, candidate ⊕ current main) on that exact head. A MERGE verdict whose A4 rests on composition of targeted suites is invalid.**

The failure was structural, not bad luck:
- The scout found that V1/V2 selected none of the 42 failing modules (`62-…:137`).
- RETURNS §10 "expected… the main test suite passing" and never ran it (`60-s1-fix3/21-…:498`).
- SWEEPCLASS recorded "the full suite: NOT EXECUTED" (`30-…/21-…:466`).
- The final pass recorded the merged tree as NOT EXECUTED (`51-…:386`).

With the rule in place, the first refuter would have met 533 outcomes about five rounds earlier. The cost is about 1 hour of wall time per head (six shards, 13 to 59 min each, from the row-9 log), run in the background while the refuter reads. That is cheaper than "full suite on every fix head" and catches the same thing at every point where a verdict is issued.

## 6. Reasons not to merge S1 in its current form

- **`c7593edb` must not merge as it is (BLOCKER B1).** M4's "fix forward" assumed a few residual failures. 533 outcomes on main would:
  - turn every other stream's CI red;
  - break the README mock workflow;
  - **stall S3**: its `_v5` freeze runs the three-window suite (X10), and text 15 keeps transaction-pack windows unarmed until that freeze completes.
- **Do not split S1's production diff.** The reader gate, the energy-accessor gating and the eight consumer calls are one mechanism. Any split leaves an intermediate main where some consumers are gated and others are not. That is the ungated-route state A3 exists to prevent, and a split re-opens a closed review.
- **Merge S1 unchanged plus a separately audited repair delta**: the 12a lines, test and helper repairs, and the hash-only repin, as additional commits on S1's branch. It still merges by **merge commit** (M1; `204424e6` must stay reachable). The final pass's M2 text still applies, with two additions: the 12a ruling and the repin record.

## 7. Findings

| Tier | Id | Finding | Where |
|---|---|---|---|
| BLOCKER | B1 | Merging `c7593edb` with 533 failing outcomes is not recoverable by fix-forward. It blocks S3's freeze, and through text 15, transaction-pack arms. | row-9 log; `arm_readiness_evidence.py:2446-2466` |
| BLOCKER | B2 | Text 12's last sentence cannot be met as implemented. The mock/`not_applicable` window contract needs a cold-gate ruling (12a proposed). | `bundle_read.py:344-353`; `run_campaign.py:9032`, `:9083-9085`; `aggregate.py:104` |
| BLOCKER | B3 | The repair needs §E-excluded files and the supply map. A named grant is needed; it cannot be inferred. | §E (`21-…:188`); `tests/test_mint_floor_artifact*.py`, `tests/test_calibration_bracketing.py`, `tests/receipt_corpus.py`, `configs/paper_supply/supply_map.json` |
| SHOULD-FIX | S1 | Campaign completion aborts with no verdict row when a member directory lacks `metadata.json`. The failure is closed, which is safe for the science, but it drops main's recorded `invalid` verdict and is stricter than text 12 ("every **finalized** bundle"). Rule it: accept and split the tests as in §4.3, or record the refusal verdict before raising. Least change: accept, and open a lane for the record shape. | `run_campaign.py:9020-9032`; `test_run_campaign.py:5853-5876` |
| SHOULD-FIX | S2 | A battery refusal inside `measured_window()` surfaces as `environment_admission_missing`, which misleads an operator. Repair must not enshrine it in expectations; a lane fixes the label. | `whole_window.py:4448-4454`; `test_whole_window_selection.py:1179`, `:1257` |
| SHOULD-FIX | S3 | The G10 tests ran the real `ioreg` probe on the host, so their result depends on its charge state, which violates text 18. They must inject a runner, checked with `ioreg` absent. | `controller.py:893-897` |
| SHOULD-FIX | S4 | Row 9 must match main's skip count (108 in this log), so that no failure is hidden by a new skip. | row-9 `WORKERS SUMMARY` |
| NIT | N1 | Campaign completion lists some bundles twice, once by label and once by absolute path. This is harmless: the same bundle is gated twice. | `run_campaign.py:9020-9031`; row-9 G2 messages |
| NIT | N2 | The scout's F3: the window-duration test hard-links into `TMPDIR`. The rerun must use the same `TMPDIR` form as main's reference. | `62-…` F3 |

RECOMMEND: Do not merge `c7593edb`. Take G2, G9 and the scope grant to one cold gate. For G2, rule 12a: a window whose members are all mock returns its verdicts, a mixed window still refuses, and it is about 8 lines in `bundle_read.py`. Land 12a, then the shared battery-fixture helper, then four parallel evidence-forward repair seats under the mechanical no-weakening checks, then the hash-only G9 repin as the last commit, then row 9 green with main's skip count, then a delta refuter and a fresh cold final pass. From now on, require a full-suite run on the exact head before any refuter or cold gate is charged.
