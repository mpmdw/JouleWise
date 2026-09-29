HOLD: OPEN — 1 route(s)

# D-138 hold refuter 2 (Opus 5.5, fresh seat): candidate 8458f797

Worktree: `/Users/edr/code/JouleWise-wt-d138-hold2-d528efb2`, detached at `8458f797`. It was clean before and after this seat (`git status --short` printed 0 lines). No repository file was modified. No capture, no powermetrics, no battery read.
Probes are in `/tmp/d138-hold2-d528efb2/`: `probe_routes.py`, `probe_ledger.py`, `probe_mint.py`, `probe_fix.py`, each with a matching `.out` file, plus `hr_tests.out`. Every probe ran with `/opt/homebrew/bin/python3 -B` and imported the candidate tree.
Held file sha256 as re-hashed: `d6de84b854a4c5d7f6d73dfde2ae0f14d71a483355c7289a36882e0dfcccd5ea`. This equals the pin at `joulewise/calibration_bracketing.py:151`.

## Words used here

- **Held file**: `configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json`, id `d079_calibration_acceptance_v2_n12_25g83_r1`. It is listed in `CLAIM_HELD_ACCEPTANCE_IDS`.
- **Keyword**: `allow_claim_held=True`, the non-claim opt-in on `load_calibration_acceptance_bound`.
- **Admission list**: `_issued_d079` in `joulewise/arm_readiness.py:6205-6220`. It decides whether a pack's declared calibration is an issued D-079 generation. If it says no, arming requires the "successor acceptance" row, and the evidence author always refuses that row.
- **Evidence author, ACCEPTANCE_OWNER**: `_derive_acceptance_owner` in `joulewise/arm_readiness_evidence.py:895-970`. It is the arm-evidence row that reads the pack's calibration bytes and certifies them.

## Route table

| # | Route probed | Evidence | Result |
|---|---|---|---|
| 1 | Loader with no path (every default consumer: `whole_window.py:508`, `analysis_engine/inputs.py:1625,3123`, `run_campaign.py:4819`, `mint_floor_artifact.py:965,1743,2036`, `calibration_bracketing.py:2098`) | probe_routes A2: returns R7. probe_ledger "F default": at a 25G83 identity the bracket fails `calibration_acceptance_bound_stale`, artifact R7, `stale_fields ['os_build']` | closed |
| 2 | Loader given the held path without the keyword. All 20 loader call sites in `joulewise/` and `scripts/` were found by grep; none passes the keyword | A3 `None`. probe_mint: the mint core, `epoch_equivalence_check`, `reissue_calibration_acceptance`, `issue_calibration_acceptance_generation` and `issue_epoch_continuation` all bind the same loader object, and the mint core loader(held) returns `None` | closed |
| 3 | Places the keyword could be set (code, CLI, env, config, default) | `git grep allow_claim_held`: outside tests, only the definition (`calibration_bracketing.py:1200,1205,1218`). No argparse flag or `os.environ` read touches it. The default is `False`. HR-6 passes | closed (see S-2: the census is weak) |
| 4 | Capture preflight at a 25G83 identity naming each of the 8 registered files | probe_ledger E: 6 older files `acceptance_artifact_stale`; R7 `acceptance_artifact_epoch_mismatch ['os_build']`; held `acceptance_artifact_unauthenticated` | closed |
| 5 | Bracket evaluation at 25G83 with each registered artifact passed explicitly | probe_ledger F: all 8 `failed`/`calibration_acceptance_bound_stale`. The held one gives reason `acceptance_artifact_claim_held` and artifact `None` | closed |
| 6 | Allowance projection and mint | probe_mint: `issued_calibration_allowance_projection(held)` returns `None`. `mint_floor_artifact_generalized.py:3596` goes through the loader and gets `None`, which raises MintError | closed |
| 7 | **R-7:** can a valid ordinary endpoint at 25G83 reach the ledger while the default is R7? | The ordinary writer preflight refuses at 25G83 (row 4; `validate_powermetrics_fiducial.py:2126-2135` refuses FROZEN_PROTOCOL_INVALID). `--derivation-only` requires a declared derivation-kind session (`:2099-2125`). Even if such an endpoint existed, R7 refuses it on `os_build` (row 5) | closed |
| 8 | Can a derivation-night capture become a bracket endpoint? | probe_ledger G: a row in a derivation session is derivation-kind, and a row naming an unknown session is `unresolved-session`. Both are skipped by `discover_calibration_candidates` (`calibration_bracketing.py:1914-1925`) and by the `registered_valid` count (`:2822-2826`) | closed |
| 9 | Consumers that read `configs/calibration/*.json` by path, bypassing the loader | The only production `json.loads` of an acceptance file is `_load_calibration_source_config` (`validate_powermetrics_fiducial.py:850-866`). It reads the DEFAULT path for a launch-marker tag and no numbers. `promote_calibration_candidate.py` is the governance writer. No glob over acceptance files exists | closed |
| 10 | Callers that skip the loader and call `_acceptance_bound_from_authenticated_bytes` directly | probe_routes B1: held bytes authenticate and return the held artifact. Callers: `arm_readiness_evidence.py:341` (row 12) and `scripts/calibration_ledger_bootstrap.py:158`. The bootstrap is locked to the D-079 import-only cutoff (`:167-181`), so it cannot build from the held file | bootstrap closed; arm evidence open (row 12) |
| 11 | Registered operatives table (`acceptance_generation_operatives`, `acceptance_bracket_screen_s`) | B2/B3: returns the held numbers (screen `0.013701`) with no hold check. Its consumers (`detection_floor.py:2536`, `floor_mint_estimator.py:156`) only see an acceptance that the mint already authenticated through the loader | closed today (S-3) |
| 12 | **Admission list reads a different field than the evidence author** | **Executed, see B-1** | **OPEN** |
| 13 | Epoch continuation making R7 judge 25G83 | probe_mint: `EPOCH_CONTINUATION_REGISTRY == {}`. Adding an entry needs a code change | closed today (S-4) |

The candidate's own hold tests pass: `tests.test_claim_hold_routes`, 8/8 OK (`hr_tests.out`).

## BLOCKER

### B-1. A claim-bearing pack that names the held file passes the admission list and gets its arm evidence certified

**Mechanism.** `_issued_d079` (`joulewise/arm_readiness.py:6211-6220`) resolves the pack's declared calibration in this order: `policy["issued"]`, then `issued_acceptance.acceptance_id`, then `issued_artifact_id`. It stops at the first one present.
The evidence author reads the bytes it certifies from a different place: `issued_acceptance` (path and sha), or `issued_artifact_id` for the flat shape (`arm_readiness_evidence.py:897-913`). It never reads `issued`.
The evidence author then authenticates those bytes with `_acceptance_bound_from_authenticated_bytes` (`:335-341`). That call skips the loader, and the loader is where the hold lives (`calibration_bracketing.py:1214-1220`).
So a pack can put R7 in `issued` and the held file in `issued_acceptance` (or in `issued_artifact_id`):
- the admission list sees R7 and admits the pack;
- the successor row is therefore NOT_APPLICABLE;
- ACCEPTANCE_OWNER reads the held bytes, authenticates them, and certifies them.

**Executed** (`probe_routes.out`, rows C and D):

```
C issued=R7 + nested held -> _issued_d079 = True
C issued=R7 + flat held   -> _issued_d079 = True
D issued=R7 + nested held (path+sha) admitted= True ACCEPTANCE_OWNER facts= {"desk.acceptance_owner.v1": {"active_acceptance_artifact_authenticated": true, ... "domain_owner_verified": true, ... "writer_test_status": "PASS"}} checks=[{"check_id": "acceptance_domain_owner_probe", "status": "PASS", "evidence": {"acceptance_id": "d079_calibration_acceptance_v2_n12_25g83_r1", ...}}]
   successor row required? False
D issued=R7 + flat held admitted= True ... "status": "PASS" ... "acceptance_id": "d079_calibration_acceptance_v2_n12_25g83_r1"
   successor row required? False
D nested held only admitted= False ... successor row required? True     <- the shape the hold tests cover
```

**Why this is a route under the charge.** The charge counts "an armed claim window" as a claim-bearing result. The addendum's enforcement point (3) says the admission list "refuses a pack that names it". The issued bytes assert the same sentence (`calibration_acceptance_d079_v2_n12_25g83_r1.json:1082`, `hold_enforcement`). As built, that sentence is false for these two pack shapes. The held file's bytes are read, authenticated and certified as the pack's calibration in the arm evidence.
Three limits on what I showed:
- A grep of `joulewise/` and `scripts/` finds exactly two arm-time readers of `acceptance_policy`: `arm_readiness.py:6206-6216` and `arm_readiness_evidence.py:897-946`. Both are passed.
- Every other arm row does not depend on the calibration file, so such a pack arms exactly where the same pack naming R7 would arm (and HR-1 admits R7 packs).
- I did not execute a full arm. That needs a complete pack fixture and t0 on the machine.

**What it does not reach, stated plainly.** No number. At runtime nothing reads the pack's declared calibration: every capture and every bracket uses the default, R7, and refuses at 25G83 (rows 1, 4, 5, 7). The capture writer's launch-lineage binding (`validate_powermetrics_fiducial.py:900-924`) would also refuse a marker-bearing capture whose pack names a path other than the selected config. So the window is armed but produces no result. Grading this below BLOCKER is the magistrate's call. The charge's parenthetical puts it here, so I do not downgrade it.

**Not covered by the tests.** HR-1, HR-2 and H-T1 to H-T3 (`tests/test_claim_hold_routes.py:109-113`; `tests/test_arm_readiness_evidence_author.py:365-389`) only build policies from the `issued` key. None of the 9 committed packs uses that key; they use `issued_acceptance` or `issued_artifact_id`. Mixed shapes are untested.

**Cure. It is inside the §8.2 write scope** (`joulewise/arm_readiness.py`, `joulewise/arm_readiness_evidence.py` is NOT in scope, see below):
1. `_issued_d079` collects every declared id (`issued`, `issued_acceptance.acceptance_id`, `issued_artifact_id`). It admits only when exactly one distinct id is declared, that id is in `_ISSUED_D079_IDS`, and none is held.
   - Sketch executed in `probe_fix.py`. Both mixed shapes are refused, and all 9 committed packs are still admitted:
   ```
   candidate True | sketch False | issued=R7+nested held
   candidate True | sketch False | issued=R7+flat held
   committed pack d117_* (9 of 9) candidate True sketch True
   ```
2. Defence in depth: ACCEPTANCE_OWNER refuses when the authenticated `acceptance_id` is in `CLAIM_HELD_ACCEPTANCE_IDS`. This closes the loader skip at `arm_readiness_evidence.py:341`. That file is outside §8.2, so the lead must amend the scope in writing, or rely on item 1 alone.
3. Tests:
   - both mixed shapes: `_issued_d079` returns False and the successor row is REQUIRED;
   - RED on `8458f797`, per probe C/D above;
   - one committed-pack shape (`issued_acceptance`) naming the held file is refused.

## SHOULD-FIX

- **S-1. The loader is not the single gate** (addendum R-3: "the one point every route passes"). `_acceptance_bound_from_authenticated_bytes` is exported and called directly at `joulewise/arm_readiness_evidence.py:341` and `scripts/calibration_ledger_bootstrap.py:158`. It returns the held artifact (probe B1). Today only the first caller is reachable (B-1). Either move the hold check into `_acceptance_bound_from_authenticated_bytes`, or add both callers to a census test. Note that moving it needs a keyword pass-through for the governance tests.
- **S-2. The HR-6 census only catches the literal `allow_claim_held=True`** (`tests/test_claim_hold_routes.py:172-185`). Executed (probe_ledger H): these forms all escape it:
  - `allow_claim_held=flag`
  - `**{'allow_claim_held': True}`
  - `allow_claim_held=1`
  - `allow_claim_held=bool(os.environ.get('X'))`

  Addendum R-4 forbids any flag or environment variable setting the keyword. The census as written would not see one. Tighten it to any `allow_claim_held` keyword, or any `**` expansion, at any call in `joulewise/` or `scripts/`.
- **S-3. The registered operatives are not held.** `acceptance_generation_operatives` and `acceptance_bracket_screen_s` (`calibration_bracketing.py:597-638`) return the held file's screen `0.013701` and rule `max(observed_drift_s,0.013701)` (B2/B3). No hold check applies. The floor-artifact validator (`detection_floor.py:2536-2539`) and the mint estimator (`floor_mint_estimator.py:156-166`) take numbers from here by id alone. Today they are reached only after the loader has authenticated the acceptance, so a held id cannot get this far through a mint. But a floor artifact whose producer block names the held id would validate its screen. Add the hold check here, or record why none is needed.
- **S-4. The hold is keyed by file, but H1 is keyed by epoch.** H1 forbids claim-bearing results at epoch 25G83. The code refuses one file id. Two later changes, both expected by the cap-council plan, would bypass H1 unless someone remembers to add them to the table:
  - the interim re-issue registered in `ISSUED_ACCEPTANCE_REGISTRY`;
  - any `EPOCH_CONTINUATION_REGISTRY` entry that extends R7 to 25G83.

  An explicit-path consumer (the mint's `calibration_acceptance` manifest path, `mint_floor_artifact_generalized.py:3596`) would then accept a 25G83 file. Add a census test: while H1 is open, every registered generation whose `identity_epoch.os_build == "25G83"`, and every continuation to 25G83, must appear in `CLAIM_HELD_ACCEPTANCE_IDS`.

## NIT

- **N-1.** `CLAIM_HELD_ACCEPTANCE_IDS` is a plain mutable `dict` (probe_ledger I). The tests' `patch.dict` needs that, so no change is required. State it in the comment.
- **N-2.** The R-2 import guard (`calibration_bracketing.py:222-223`) checks `ACTIVE_ACCEPTANCE_ID`, not `DEFAULT_ACCEPTANCE_BOUND_PATH`. A default path moved to the held file while the id stays at R7 would import cleanly. It stays harmless because the loader checks the artifact's own id and returns `None`, so every consumer refuses. A one-line path check would make the guard say what the comment says.
- **N-3 (pre-existing on main, not a held-file route, not executed).** `--identity-epoch-json-for-test` (`validate_powermetrics_fiducial.py:2046-2064`) is not gated to the test sampler. Only `--projection-cell-budget-for-test` requires `--sampler-direct-for-test` (`:2029-2034`). A live capture on a 25G83 machine could therefore record a declared 25F84 identity and pass the R7 preflight. From reading the code, a bracket also needs the measurement bundles' bindings to match, so this alone gives no result. I record it for the lane owner, outside this transaction.

## Summary

1. Every route from the held file to a NUMBER is closed on the candidate, by execution:
   - the default is R7 and refuses at 25G83;
   - the loader hides the held file from all 20 production call sites;
   - no keyword setter exists;
   - preflight, bracket evaluation, allowance projection and mint all refuse;
   - derivation-night rows cannot be endpoints;
   - no valid ordinary 25G83 endpoint can be written while R7 is the default.
2. One route reaches an ARMED CLAIM WINDOW, which the charge counts as a result. A pack with `issued` = R7 and `issued_acceptance` (or `issued_artifact_id`) = the held file is admitted by `_issued_d079`, and its held bytes are certified PASS by the ACCEPTANCE_OWNER evidence row, which skips the loader. That makes enforcement point (3), and the `hold_enforcement` sentence inside the issued bytes, false as built.
3. The cure is small and within scope (a consistency rule in `_issued_d079` plus tests; sketch executed, 9/9 committed packs unaffected). Per §8.1 step 8 the transaction stops until it lands. S-1 to S-4 harden the "single gate" claim and the future re-issue path.
