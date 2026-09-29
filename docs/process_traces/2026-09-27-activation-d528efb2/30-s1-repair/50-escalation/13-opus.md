SEAT: Opus 5.5 — S1-REPAIR-ROUTE-01

Code at `5283d7d0`. Probes: `/tmp/s1route-d528efb2/opus/probe1-5.py`. All ran under the guard, and the guard log stayed at 61 lines (0 battery-probe attempts). "Inference" means not executed.

## 1. Diagnosis: one coupling, not ≈100 separate gaps

**Terms.**
- **Bound config:** the SHA-256 of `config.json` equals `metadata.config_sha256`.
- **Exempt bundle:** `custody_telemetry_identity(...).production_predicate_exempt` is true. This happens exactly when the config is unbound, or is bound with the `mock` backend (`joulewise/whole_window.py:989-999`, `:1073-1085`).
- **Current-mint predicates:** the production checks that exempt bundles skip.

**The coupling.** On main, the failing tests drove claim paths with exempt fixtures:
- floor bundles with **no `config.json`** at all (`tests/test_floor_extraction.py:398-416`);
- a mock integration corpus;
- hand-built campaign members with an unbound config (`tests/test_run_campaign.py:8028-8111`).

The evidence-forward form (ruling §3.4) gives a fixture a battery pair only after binding a non-mock config. **Binding a non-mock config is exactly what switches the exemption off.** So every fixture made battery-passable also becomes subject to every current-mint predicate that main let it skip. These are:
- `joulewise/analysis_engine/inputs.py:205` (whether an anchor-fallback member is usable);
- `joulewise/floor_extraction.py:1903` (environment admission);
- `scripts/run_campaign.py:4559`, `:6615`, `:6623`;
- the telemetry-triangle check (config, metadata and summary must name the same backend), which binding switches on (`floor_extraction.py:2021-2023`).

**Executed proof (probe3).** I used the scenario of `test_full_coverage_has_no_membership_refusal`: main's hand-built members, plus a bound powermetrics config, agreeing backend labels and an authentic pair.
- Gate: `pass` for all 3 members.
- Every member is excluded, for exactly two reasons: `anchor_fallback_member_unusable` and `environment_admission_missing`.
- With the exemption forced true (probe only): `all_cells_extractable = True`, no reasons, gate still `pass`.
- Without agreeing labels (probe2): `bundle_strict_invalid` is added, from the triangle check.

**Discriminator (probe5).** Seat A's two neg8-derivation test IDs already had a bound non-mock config on main (`test_run_campaign.py:8378-8386`), so they were never exempt. `write_passing_pair` alone (plus `run_id` added to metadata) gives `Ran 2 tests … OK`. The rule that follows:
- **not exempt on main → the pair alone repairs the test;**
- **exempt on main → the test hits the coupling.**

**What each later predicate needs, and whether production code can produce it in a test process:**

| Predicate | Needs | Produced in-process by production code? |
|---|---|---|
| Battery pair, strict validation | a controller run with an injected battery runner | Yes (probe1: strict `[]`, gate `pass`) |
| Environment admission (bundle) | campaign policy, preflight, snapshot, guard observations | Partly. `_produce_admission_powermetrics_bundle` (`tests/test_controller.py:770-836`) writes it, at about 11 s per bundle on the real clock. `environment_admission_missing` still remains (probe1 "clean"); cause not isolated. |
| Clock anchor bounded, cadence ratio, anchor-energy envelope | sampler timestamps that agree with the controller's clock stamps within ±1 s (`joulewise/uncertainty_evidence.py:257-330`; `reduce.py:983-996`) | No existing producer. Both give `clock_anchor unknown` and `cadence_ratio_below_threshold` (probe1). Inference: a new sampler timed on the fake clock could. |
| Adapter continuity, CPU-admission core, idle-admission core, neg8 verdict | a campaign: neg8 start and end members, drift bound, attempt ledger, calibration bracket | Only by driving `run_campaign` end to end. No test does this. Main's own test stubs `validate_bundle`, the calibration bracket and launch lineage (main `test_run_campaign.py:10670-10690`). |
| Floor custody | a real member bundle under each floor evidence root (S1's gate, `inputs.py:1894-1899`) | Yes: materialise the members first, then build the floor records from them. This is the gate itself, not the coupling. |

None strictly needs hardware (probe outputs are injectable), but the full chain needs at least three unbuilt layers.

**Gate property (probe4).** A bundle carrying a pair gets `pass` even when its config is **deleted**, or **rebound to `mock`**. The reason: `bundle_read.py:483-487` sends any pair-carrying bundle to `authenticate_bundle` (`battery_float.py:1026-1068`), which never reads the config. Both of those bundles are also exempt. The mock barrier after the gate (`inputs.py:2889`, `floor_extraction.py:2028`) still stops the mock case on those two paths. The minter, the window-duration margins and the aggregate have no such barrier (ruling §3.2(1)).

## 2. Routes

| Route | Soundness | Size (seat-rounds) | Risk of a third round with the same signature |
|---|---|---|---|
| (a) builder produces claim-ready bundles end to end | Good (production writers). It cannot keep hand-set numbers, so numeric assertions move. | 4–6; slow tests (≈11 s per admitted bundle; corpora of 10–80 members) | **High.** Three unbuilt layers were found by executed probes; each is another discovery round. |
| (b) committed claim corpus, generated once and pinned by digest | Same as (a), provided a test re-validates it under current code. Otherwise a digest is trusted instead of the predicates. | Generating it ≈ (a); plus a repin every time a writer changes | High, during generation |
| (c) re-scope (assert the refusal; move the subject to a sibling test) | Good | 1–2 | Moderate. Much of the inner logic is inline (seat A F3: the mock barrier has no callable function), so it needs production edits, which means new NEEDS_RULING returns. |
| (d) split S1 | **Leaves claim paths un-gated**, which #421 forbids. Skipping the ≈100 tests instead is banned by check 2. | — | — |
| (e) **exemption parity** (defined below) | The battery gate stays real everywhere. The test's subject keeps exactly main's coverage. Such a test can pass on a bundle that has no environment admission. So could main's version (it was exempt), and each stubbed predicate keeps its own direct tests. | ≈2 | **Low.** The stub list is fixed by what main skipped. Any refusal left after parity is by definition a different cause. |
| (e′) pairs on config-less fixtures (gate property) | **Unsound:** no real window lacks `config.json`. | — | — |

**Exemption parity, defined.** A test-only context manager in helper H. It replaces a closed list of named functions with stand-ins that report no refusal. The list is exactly the functions that consult `production_predicate_exempt`, for example:
- `anchor_fallback_member_unusable`;
- `_cpu_admission_bundle_reasons`;
- `_current_member_environment_refusals`.

It never touches battery functions, `custody_telemetry_identity`, or any name that check 2 bans. The triangle check is not stubbed: the fixture meets it with agreeing labels.

Main already does this (`strict_validator=lambda…: []`, `tests/test_analysis_integration.py:651` ff.; floor stubs, `test_floor_extraction.py:419-450`).

## 3. Recommendation

**Plan, in order.**

0. **Lead, at the bench.** Triage every outcome ID on **main's** tree, using a read-only spy on `custody_telemetry_identity` that records and alters nothing. Sort each ID into one class:
   - **T1** — the pair alone (never exempt on main);
   - **T2** — parity (exempt on main; the subject is not mock refusal);
   - **T3** — form 2 of ruling §3.4 (the subject is mock refusal or the barrier);
   - **T4** — materialise the floor members first, then treat as T1 or T2.

   Land the two neg8 IDs as T1.
1. **Cold gate** rules R1–R5 below.
2. **Parity helper**, built by seat H3 or the lead, with its pin and planted defects.
3. **Seats A and B**, in parallel, repair per ID. Then the lead runs the checks, then A3's R2-4.

**What must be ruled before any seat starts.**
- **R1. The parity text and its closed list.** A sweep test asserts that the set of functions under `joulewise/` and `scripts/` that reference `production_predicate_exempt` equals the list. Planted defect: drop one entry, and the sweep must go RED. Parity is granted by test ID only. It is never granted to a test whose subject is a stubbed predicate.
- **R2. The mock-barrier sibling (seat A F3).** On claim paths the gate runs before the barrier (`inputs.py:2824` before `:2889`). Choose one:
  - (i) the sibling builds a mock-config bundle that carries a pair, and asserts the barrier fires. This tests the barrier's one remaining job.
  - (ii) if R3 closes the gate property, the sibling requirement is retired, with that reason written down.
- **R3. The gate property.** I lean towards closing it inside S1: a pair gives `pass` only on a bound, non-mock config. That is about 3 lines in `bundle_read.py`, which is already in check 3's set. Planted defect: remove the check, and a mock-config bundle carrying a pair must pass the gate. Otherwise it goes to a lane, because under #421 it is a question of whether a number is true.
- **R4. Floor fixtures (T4).** Build the member bundles first and derive the floor records from them. Pins move only under A3's leaf-diff rule.
- **R5. The golden report:** regenerate from rebind-plus-pair members under parity; A3's leaf-diff rule unchanged. Not executed for the golden itself (probe3 shows such members admitted, values kept).

**Stop conditions.** Return to a cold gate, with no fourth round, if any of these holds:
- any test needs a stand-in outside R1's list;
- more than 3 tests are refused by the same predicate that is neither exemption-gated nor the gate;
- more than 10 inventory outcomes still fail after the round;
- any assertion changes outside the R-list.

**Lane:** CLAIM-CHAIN-CANARY-01, a single test that runs the whole claim chain on fully produced evidence. Main never had one, so it is not a merge condition.

## 4. Where A3 is wrong

1. **§4.1 names the wrong cause** (a missing builder, not the coupling); a bundle-level builder cannot supply campaign or floor evidence, so stop condition (3) was predictable.
2. **§5.5 item 3 cannot be met:** produced members cannot carry hand-set values, and current-mint predicates refuse them (probe1).
3. **"Not written by hand" draws the wrong line.** Helper H already places pairs into hand-built bundles, and main hand-writes environment admission (`test_run_campaign.py:8075-8111`). The line that protects #421 is: never fake **battery** evidence, and never stub the predicate that is the test's own subject.
4. **§5.3's sibling is unexecutable as written.** The barrier is inline code, and on claim paths it sits behind the gate.
5. **A3 missed the gate property**: a pair gives `pass` on an unbound or mock config.
