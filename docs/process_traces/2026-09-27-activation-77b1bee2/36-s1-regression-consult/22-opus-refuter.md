# S1-REGRESSION-01 — Opus 5.5 contract-lens refuter

Seat: Opus 5.5, paired contract-lens refuter to the cold Fable judge. I am not the Opus consult seat that wrote `13-opus-consult.md`. The session was read-only and ran from 17:12 to 17:30 PDT; every command ran in the foreground. There were no subagents, no Codex and no `claude -p`. Python was `/opt/homebrew/bin/python3 -B`. Scratch is under `/tmp/opus-s1reg-77b1bee2/`. `git status --short` on the integration tree printed 0 lines before and after every probe. This file is the only file I wrote in any repository.

**Contamination disclosure.** The harness loaded the global and project `CLAUDE.md`, `CLAUDE.local.md` and the memory index into my context before the task arrived. I used none of them for any finding. I did not open RUN_STATE, TASK_QUEUE, AGENTS, any memory file or any skill file. I read the charge, the scout report and inventory, all three consult seats, Final texts v1.1 §C–§E, and the code cited below. Section A was written to scratch (`/tmp/opus-s1reg-77b1bee2/sectionA.md`) **before** I opened the ruling. The ruling file had already appeared at 17:21, but I did not read it until Section A was fixed.

**Terms.** *Mock bundle*: its `config.json`, bound by `metadata.config_sha256`, names the synthetic `mock` telemetry backend. The window gate gives it the status `not_applicable`. *Window gate*: `authenticate_window_members` in `joulewise/bundle_read.py`. *Mock barrier*: the reason code `mock_telemetry_claim_ineligible`, added by the analysis loader and by floor extraction. *12a shim*: my probe-only `sitecustomize.py`. Because `sitecustomize` loads at interpreter start, the shim also reaches test subprocesses. It rewrites, in memory only, the refusal tail of the window gate so that a call whose every obligated member is `not_applicable` returns its verdicts. In `broad` mode it does this at every call site. In `ruled` mode it does it only at `run_campaign()` and at `aggregate.py` when called under `controller.py`, which reproduces the ruling's closed list.

---

## Section A — independent answers (fixed before the ruling was read)

### A.0 Executed evidence

| Id | Probe | Result |
|---|---|---|
| R1 | `sed -n 282,354p joulewise/bundle_read.py` | The window gate refuses `confounded`, `evidence_missing` and `not_applicable`. It returns `unobserved_historical` verdicts without refusing them. It has no claim/non-claim parameter. |
| R2 | Read `BundleReader._battery_verdict`; **executed** `/tmp/opus-s1reg-77b1bee2/mockpair.py` (builds S1's own `WindowMembersTests.pair_bundle` fixture) | Classification order: `not_reached`; then **pair present ⇒ `authenticate_bundle`, with no backend check**; then key absent with digest in the historical set ⇒ `unobserved_historical`; then digest-bound mock ⇒ `not_applicable`. The probe printed `bound config telemetry_backend = mock` and `gate verdict = pass`. **A mock-config bundle carrying a synthetic pair passes the gate as `pass`.** This is S1's own canonical passing fixture, although the controller never writes a pair for mock (text 7). |
| R3 | Scanned the 69 rows of `configs/battery_float/historical_bundles.json` for the backend of each source bundle | Two rows are mock bundles: `tests/fixtures/axi_valid_burst` and `tests/fixtures/legacy_reducer_current_behavior`. `test_analysis_claims.py:1079` and `test_floor_extraction.py:6048` push `axi_valid_burst` through `_read_bundle` and `_evaluate_member` and assert `mock_telemetry_claim_ineligible`. Both pass on S1 today. **So under the strict gate as implemented, the mock barrier is already the only guard for historical mock bundles.** |
| R4 | Compared `custody_telemetry_identity` (`whole_window.py`) with `_digest_bound_mock_config` (`bundle_read.py`) | Both test the same two things: `sha256(config.json bytes) == metadata.config_sha256`, and parsed backend `== mock`. The two functions differ, but in production they decide on the same basis. |
| R5 | Grep for mock handling across the eight text-12 consumers and `run_campaign` readiness | The barrier exists at `inputs.py:1944`, `:2890` and `floor_extraction.py:1990`. `whole_window._current_strict_summary` excludes mock from NEG-8 strict energy. **There is no mock reference** in `window_duration_margins.py`, `aggregate.py`, `mint_floor_artifact.py` or `extract_detection_floors.py` (the last two reach floor extraction's barrier through the extraction report). In `run_campaign`, `_member_readiness_reasons` treats mock as `production_predicate_exempt`, and `claim_readiness_for` can return **`ready_for_analysis` for a mock campaign**. Its note says "checks analysis inputs only; P2-037 decides claim outcomes". |
| R6 | Census of window-gate call sites, and the flow into each single-member call | Five literal single-member calls exist: `whole_window.py:3640`, `inputs.py:2824`, `aggregate.py:155`, `run_campaign.py:5350` and `mint_floor_artifact.py:378`. In every flow I traced, a whole-set call comes first: `aggregate:104→155`; `run_campaign:6288→6293`; `inputs:3195→3304`; `whole_window:3791→3856` and `:4078→4123/4155`; `mint:1020→1056` and `:458 (via 1844)→1874`. **The mint's "set" is one component's record rows, not the whole window.** |
| R7 | Ran the 94 distinct G2 test IDs under the **broad** shim | `Ran 94 … FAILED (failures=1, errors=37)`. 56 IDs pass with their assertions unchanged, including the subprocess ones that the consult seat's in-memory X6 could not reach. The 37 errors are all the next layer down, `CustodyUnreadable … metadata.json` (the G3 shape). The single failure (`test_repetitions_three_mock_cli_dispatch`) passes when run alone, so it is an ordering interaction. |
| R8 | Ran the 5 claim-writer test modules with the shim off and then on | Identical both times: `Ran 354 … failures=7, errors=100`. |
| R9 | Looked up the end-to-end mock-barrier tests in the inventory | `test_named_strata_manifest_preserves_terminal_mock_refusal`, `…derives_deterministic_fail_closed_artifact` (both with `_with_production_telemetry_identity` twins) and `test_mock_config_tail_pending_data_only_ruling` all fail on S1 with `not_applicable`. |
| R10 | Read `tests/test_bundle_read.py:563-588` | The §E fence runs `git diff --exit-code 1417c0c4 204424e6 -- <protected>`. **It is blind to every commit after `204424e6`.** |
| R11 | Read the §E S1 list (`…/21-coldgate-fable-addendum-ruling.md:155-183`) | It names 25 files and is marked "exhaustive; nothing inferred". **None of the roughly 40 failing legacy modules is on it**, not only the five §E-excluded files that the consult seat names. |
| R12 | Parsed `supply_map.json`; read `tests/fixtures/paper_custody/repin.py:24-31` | There are 5 `fixture.*` roles, each with `test_fixture_non_issuing` and `issuance_gate_id=None`, plus 2 `pending_roles`. `repin.py` overwrites `pending_roles` with the 1p7b role alone, which drops the 8B role. |
| R13 | Read `calibration_bracketing.py:1862-1911` and `test_run_campaign.py:8085-8097` | Battery classification ignores `mode` and runs before `_candidate_from_observation(…, mode=mode)`. Five G7 outcomes are `read_replay` relocation tests that assert `assertFalse(original.exists())`. **Astra's F1 holds.** |
| R14 | Read `arm_readiness_evidence.py:2446-2468` | S3's `THREE_WINDOW_REGRESSION` runs `tests.test_calibration_live_three_window` and binds `exact_test_count`. So G6 blocks S3's freeze. |

NOT EXECUTED: any claim writer driven end to end with a mock window (the analysis tests stop at G3 before they reach it); `window_duration_margins` with a mock member; the full suite.

### A.1 G2
- **Could 12a, as the consult seat drafted it, let a claim path through?** I found no path. But its protection is uneven, and its text overstates it:
  - The mock barrier covers analysis, floor extraction/mint and NEG-8 strict energy, and it fires on exactly the set that 12a admits (R4, R5).
  - `window_duration_margins` and `aggregate` have no barrier. `window_duration_margins` is protected in practice only because pack membership pins `config_sha256`.
  - `claim_readiness_for` can say `ready_for_analysis` for mock (R5).
  - "No claim artifact is built from a mock window" is false: the finalizer builds a fail-closed artifact (R9).
  - Mixed-window detection only covers the member set at each call site (R6).
- **Does strict lose real coverage?** Yes, and more than the Sol seat says.
  - 56 of the 94 G2 IDs pass unchanged under 12a (R7). Under strict they must become refusal tests or production-grade non-mock fixtures.
  - The end-to-end barrier tests for prospective mock bundles lose their subject (R9).
  - Strict is also not a uniform wall: historical mock bundles pass it (R3), and so do mock bundles that carry a pair (R2).
- **My position:** admit mock windows only where no claim can follow, keep every claim path strict, amend the 12a text, test the mixed-window case at every set call, and ban pairs on mock fixtures.

### A.2 G9
The pins are synthetic non-issuing fixtures (R12). The lead repins them at the bench, as the last commit, inside S1's own PR. `repin.py` must not be used (R12). The only edits allowed are `expected_sha256` values; the regeneration is checked in both directions; one refuter checks it.

### A.3 Scope
The grant must name every legacy module the repair touches (R11), plus the helper, the three §E-excluded test files and `supply_map.json`. The fence cannot see the repair range (R10). So the lead's path check must be `git diff --name-only c7593edb HEAD` ⊆ (S1 scope ∪ grant) over **all** paths. The G7 fix (R13) is a production edit to `calibration_bracketing.py`, which is already in S1's scope.

### A.4 / A.5
The order is: production rules first, then the helper, then disjoint seats, then the repin last. The full suite on the candidate merged with current main must be green, with skips equal to main's, before the delta refuter and before the new cold final pass. Opus should-fix S3 (G10 hermeticity) and S4 (skips) are in scope. S1 and S2 go to lanes. Neither a split nor abandonment is warranted.

---

## Section B — refutation of `21-coldgate-fable-ruling.md`

**Overall.** The ruling is sound, and on G2 it is better than my own Section A.
- Its keyword design has three parts: the default is strict, the closed list holds two flows, and a sweep test pins that list (12a (b), (c), (e)). That design removes the two weaknesses I found in the data-decided 12a. First, a mixed window is no longer detected only as widely as each call site's member set (R6). Second, the barrier-less consumers (`window_duration_margins`, the `aggregate` behind `make_figures`) stay strict (R5).
- I re-executed or confirmed its load-bearing facts:
  - E2: `42e2af3e` has parents `c7593edb daaff807`, and `e7c8bcc6` is NOT an ancestor. PR 436 touches three files, none of them in S1.
  - E6, E7, E13, E14, E16 and E19 match R1, R5, R12, R13 and R14.
  - Its grant covers every failing non-G9 module. I diffed the grant block against the inventory: none is missing, and the only extras are `supply_map.json` and the two helper files.
- I find **no blocker**. There are four should-fix items and three nits, all below.

### SHOULD-FIX

**SF-1. The ruling does not ban a battery pair on a mock-config fixture, and that pattern is the easiest way to turn the 42 "stay refused" tests green.**
- The evidence is executed (R2): S1's own `pair_bundle` fixture has a mock bound config and a synthetic pair, and the gate returns `pass`.
- The ruling's evidence-forward form (§3.4) asks for a *non-mock* config plus a pair. But nothing forbids a seat from keeping the mock config and just adding a pair. That shortcut would bring the analysis-integration stand-in tests to their old assertions with the battery gate "passing" on a bundle the controller can never write (text 7).
- The result: seat A's tests would pass for a reason that production cannot reproduce.
- **Fix:**
  - Add to check 2: "a battery pair written into a bundle whose bound `config.json` names `mock`".
  - Helper H's `write a passing pair` refuses a mock-config bundle, with a counterfactual self-test.
  - The reader's branch (i) admitting a pair on a mock config (text 8 does not check the backend) goes to a lane. It is not a claim risk, because the mock barrier still fires (R4), but it is the mirror image of T12a-6.

**SF-2. The ruling calls `run_campaign.py:7848` a claim path, but it is the AXI campaign's completion gate, the same thing as `:9032`.**
- I read `:7831-7900`. The gate runs before the attempt ledger is rendered and before the cooldown and idle-admission evidence. That is the same position that `:9032` holds in `run_campaign`, and `:9032` is admitted.
- Text 12 names only run_campaign's "final analysis and whole-window verdict".
- Executed: under the **ruled-shape** shim, `test_axi_runner_emits_campaign_wide_idle_admission_verdict` and `test_non_marker_axi_multi_entry_campaign_records_gate_before_entry_two` stay refused at `:7848`. Under the broad shim both pass unchanged.
- Their subject is AXI completion behaviour, not mock refusal. Making them evidence-forward needs non-mock bundles produced by the campaign's fake runner, which runs as a subprocess. §3.2 itself says that cannot be done without a new production hook.
- So they will come back as `NEEDS_RULING`, or else be rewritten, which is the coverage loss §3.2 gave as its reason for rejecting Sol.
- **Fix:** rule `:7848` now. Either add `run_axi_spec_campaign`'s completion call to 12a (c), with the same (d) obligations and a T12a-8 AXI row, or record why AXI completion is claim-bearing when campaign completion is not.

**SF-3. The condition in 12a (d) is met; it is not "NOT EXECUTED".**
- `claim_readiness_for` (`run_campaign.py:6687-6817`) returns `ready_for_analysis` for mock campaigns.
- Two G2 tests assert exactly this on mock fixtures (`write_strict_analysis_campaign` defaults to `telemetry_backend="mock"`, `test_run_campaign.py:1677`): `test_explicit_campaign_cooldown_evidence_allows_ready_for_analysis` and `test_existing_resume_provenance_does_not_shadow_invoked_cooldown_evidence`. Both pass unchanged under the shim.
- (d) therefore forces three things:
  - a production edit to readiness;
  - two R-list rewrites;
  - moving the subject of those tests (cooldown evidence enabling readiness) to a non-mock sibling, which meets SF-2's subprocess problem.
- It also reverses a documented main contract: `CLAIM_READINESS_NOTE`, and the comment "Mock telemetry stays version-exempt: it cannot bear claims regardless".
- **Fix:** decide it in the ruling. Either (a) keep main's readiness semantics for admitted mock windows, relying on the analysis loader staying strict under 12a so that a mock campaign can never reach an analysis artifact, and change T12a-8 to assert that; or (b) keep (d) and list the two tests on the R-list with their sibling plan. I prefer (a): it changes fewer production bytes and loses no protection, because the loader refuses mock by default.

**SF-4. Check 7 leans on a fence that cannot see the repair.**
- The protected-path test compares `1417c0c4..204424e6` only (R10). It stays GREEN whatever the repair does.
- Check 3 limits the *production* paths. No check limits the *test* paths of the whole diff.
- **Fix:**
  - Check 7 becomes: `git diff --name-only c7593edb HEAD -- <§E protected list>` prints exactly the three granted test files.
  - Add: `git diff --name-only c7593edb HEAD` ⊆ (S1 §E list ∪ the §6 grant ∪ `joulewise/envelope_gate.py` per SWEEPCLASS). One path outside fails.

### NIT

- **N-1.** "12a clears 56" (§3.4) is caveated but optimistic. Under the ruled-shape shim, 94 G2 IDs give **45** failing IDs, against 37 under the broad shim. The extra eight are:
  - 5 `test_experiment` tests that call `aggregate_experiment` directly and so need the keyword. The ruling should say explicitly that these count as "direct tests of the two admitted flows" in check 2.
  - the 2 AXI tests (SF-2).
  - `test_dirty_unknown_and_changed_provenance_are_hard_excluded_at_admission`, which sits at `inputs.py:2824` and is correctly strict.
- **N-2.** E10 says the floor extractor has no barrier. `extract_detection_floors.py` and the minter reach `floor_extraction._evaluate_member`'s barrier through the extraction report. The conclusion is unaffected, because both stay strict.
- **N-3.** Defect 2 in §3.2 ("decided by different code") is true of the functions, but on production inputs they decide on the same basis (R4). The argument holds on barrier count alone, which is enough.

### Residual risk (not a finding)

Seat A's evidence-forward conversion of about 36 analysis-integration stand-ins to non-mock fixtures turns on production predicates that mock skipped (`production_predicate_exempt`: reducer wire, environment refusals, provenance). The ten `_with_production_telemetry_identity` twins exist to avoid exactly that cost. Expect several `NEEDS_RULING` returns from seat A. The assertion census will catch any silent change.

### Disposition

I concur with Rulings 1 (as amended by SF-1 to SF-3), 1b (10a), 2, 3 (with SF-4), 4 and 5. Each should-fix is a sentence-level amendment the lead can bring to the judge before seat P is briefed. None changes the ruling's structure, and none weakens a claim path.

REFUTER: CONCUR
