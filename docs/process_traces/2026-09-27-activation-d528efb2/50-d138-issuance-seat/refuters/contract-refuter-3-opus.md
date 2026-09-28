REFUTER: DISSENT

# D-138 25G83 issuing transaction — fresh contract refuter (Opus 5.5), candidate `b953f4b0`

Candidate: read-only worktree `/Users/edr/code/JouleWise-wt-d138-contract3-d528efb2`, detached at `b953f4b0119f0e05bf02cb9ac206eaf4498b08e3`. It was still clean at the end (`git status --short` empty). I made no git writes, ran no capture or powermetrics, did not read the battery, and did not use sudo. All probes and outputs are in `/tmp/d138-contract3-d528efb2/`. Main-side runs used a `git archive` extract of `9eab16f8` (and of `8458f797`) under `/tmp/d138-contract3-d528efb2/arch/`.

Rulings applied: D138-25G83-DESIGN-01 with its addendum A1; HOLD-BY-CONSTRUCTION-01 (called "the ruling in force" below); HOLD-BY-CONSTRUCTION-01-A1 (called "the d079 addendum").

**Verdict in one paragraph.** Charges (1) and (5) pass completely. Charge (2) passes on everything §5.1 requires the tool to do. Its test P8, however, leaves out two of the four probes §5.1 names, and a mutant that allows an empty or missing `source_rulings` list survives the test module. The tool also still accepts many content substitutions that go beyond the letter of §5.1. Charge (3): no test from main was textually weakened except in ways the rulings cover, but **four test files from main that this branch does not touch now fail**. All four are GREEN at `9eab16f8` and at `8458f797`. Curing them means editing tests from main, which is outside the write scope. That makes it a BLOCKER for gate 6. Whether it also triggers the stop in §6.2 (its last row, "an assertion from main weakened") is for the cold judge to decide. Charge (4): the C-5 allowlist equals what its own search pattern finds. That pattern cannot see code that reaches a calibration file through the registry, and it misses the file whose route was F2. C-6 cannot see a second place that sets `status = "passed"` if that place uses a different variable name. **I found no route as §6.1 defines one.**

---

## BLOCKER

### B1 — Four test files from main fail at `b953f4b0`; they pass at `9eab16f8` and `8458f797`; none of them is in the branch diff

| Test (unchanged from main) | Cause | Evidence |
|---|---|---|
| `tests/test_floor_mint_pinsets_schema.py:66` `assertIsNotNone(screen)` for every registered id | The held new id's screen is `None` by design (E-6c; `acceptance_bracket_screen_s` is held) | `p3_pinset.out`: `screen(new) = None`; as-is `(1 run, 1 fail)`; control with `CLAIM_HELD_OS_BUILDS` emptied in memory `(1, 0)`. Also RED in the lead's in-progress suite `/tmp/d138-suite4-d528efb2/rc.txt` at `b953f4b0` |
| `tests/test_validate_powermetrics_fiducial.py` `ContinuedEpochPreflightTests` ×2 (`:178`, `:194`) | Identity seam: `scripts/validate_powermetrics_fiducial.py:1895` raises `parser.error("identity epoch test input requires --sampler-direct-for-test")`; these tests use the override on the derivation-only path without the test sampler | `mods/test_validate_powermetrics_fiducial.log` (2 ERROR, SystemExit 2) |
| `tests/test_powermetrics_fiducial.py` `FrozenProtocolTests.test_acceptance_artifact_refusals_are_distinct_and_emit_no_output` (cases missing/tampered/wrong_epoch) and `test_estimator_byte_drift_refuses_acceptance_as_stale` | Same seam | Executed here: at the candidate `FAILED (failures=1, errors=4)`, 4× the seam's `parser.error`; at the main extract `OK` |
| `tests/test_calibration_exits.py` ×4 (`test_parameterized_durable_public_cli_witnesses`, three `RefusalInventoryTests`) | Witness case `writer-derivation-standalone` (`:5395-5416`) passes `--identity-epoch-json-for-test` without `--sampler-direct-for-test`; argparse exits and no JSON refusal payload is written (`0 != 1 : expected one refusal/authorization payload`) | **Read from the lead's suite log** `/tmp/d138-suite4-d528efb2/mod/tests.test_calibration_exits.log`; I did not re-run this module myself |

Baselines: at the `9eab16f8` extract, the pinset module plus `ContinuedEpochPreflightTests` gave `Ran 13 … OK`, and so did the `8458f797` extract. The lead's suite at `8458f797` (`/tmp/d138-suite2-d528efb2/summary.txt`) had one failure, in `test_run_night`, and none in these four modules.

Why this is a contract finding, not only a suite result:
- None of the four files is in §4.5's WRITE_SCOPE. The lead's amendment rule in §4.5 allows test-file edits **only** "to patch the machine-build reader in a test that exercises S2 or S3". These failures come from the numbers-table hold (G1 by identifier) and from the identity seam, not from S2 or S3. The lead-owned census by execution (§4.5 step 3) prototyped only S2 and S3, so nothing prototyped the seam's effect before the seat ran.
- Every cure edits a test from main:
  - Pinset test: stop asserting a screen for held ids, or read the numbers through the unchecked path. This narrows the domain of a main assertion. It is the same pattern as the `continue` exclusions accepted in `test_calibration_bracketing.py`, but it is not ruled.
  - The seam tests: add `--sampler-direct-for-test`, or route the identity some other way. Either changes the input that a main refusal assertion exercises.
- §6.2's last row makes "an assertion from main weakened" a stop. §9 anticipated this for S2 and S3 ("If the lead's prototype shows that S2 or S3 cannot be added without changing what a test from main asserts, that is a stop under §6.2"). **The magistrate or cold judge must rule whether these cures count as weakening. The lead must not.** If each refusal assertion survives with only the sampler flag added, that looks like the "tests only" closing pass. If not, it is a stop.
- This is not a route. All four fail closed.

---

## SHOULD-FIX

### S1 — Census C-5 cannot see code that reaches a calibration file through the registry, and it misses F2's own file
`tests/test_claim_hold_census.py:72`. The pattern is `configs/calibration|_CALIBRATION_CONFIG_DIR|calibration_acceptance_|\b[A-Za-z_]\w*_ACCEPTANCE_BOUND_PATH\b`.
- The allowlist equals the pattern's result in the tree. I recomputed it independently with grep: 24 files, identical to `CALIBRATION_READERS` (`c5_found.txt`). **In that literal sense charge (4) passes.**
- These files do reach calibration bytes but are absent from the map:
  - `joulewise/arm_readiness_evidence.py` resolves `ISSUED_ACCEPTANCE_REGISTRY[...]["relative_path"]` and reads the bytes (`:897-921`, `:267`). This is the F2 route that motivated G1.
  - `joulewise/calibration_epoch_continuation.py` and `scripts/issue_epoch_continuation.py:324` read through the registry too.
- Planted in a scratch copy (`p7_census.out`):
  - N-a: a new `joulewise/reg_reader.py` doing `json.loads(b.ISSUED_ACCEPTANCE_REGISTRY[i]['path'].read_bytes())` leaves the census **GREEN**.
  - N-g: a `scripts/` reader over `R.values()['relative_path']` leaves it **GREEN**.
- The ruling's own examples all turn it RED: (a) RED c5, (b) RED c1, (c) RED c6, (d) RED c2. Runtime-assembled paths (N-f) stay GREEN, as §4.3 admits.
- Registry access is ordinary code, not evasion. It is exactly the "honest mistake" C-5 is meant to bound. Cure, test-only: add `ISSUED_ACCEPTANCE_REGISTRY|EPOCH_CONTINUATION_REGISTRY` to the pattern and add those three files to the map.

### S2 — C-6 cannot see a second pass site under another name
`tests/test_claim_hold_census.py:83-92` counts only `result["status"] = "passed"`, with the target named `result`. Planted in scratch:
- N-b, `bracket_out["status"] = "passed"`: **GREEN**.
- N-c, `result.update(status="passed")`: **GREEN**.
- N-e, guard neutralised as `if False and (…)`: GREEN. The route test E-2 is the behavioural backstop for N-e, not the census.

The ruling says "assignments of the string `passed` to a result's `status`". Keying that to the variable name `result` is narrower than the ruling. Cure, test-only: count any `Subscript` store with slice `"status"` of the constant `"passed"`, plus `.update(status="passed")`, in the module.

### S3 — Test P8 omits two of the probes §5.1 names; the tool's `source_rulings` check is unguarded
§5.1: "Test P8: the contract refuter's probes P5a, P5b, P5f and P5g, plus one hold with empty text". `tests/test_promote_calibration_candidate.py:81-94` has:
- present: P5a; a ruling-path pop; the network-time source digest pop (P5b in part); a preserved-log path pop; H5 with empty text;
- **missing: P5f** (delete `network_time_provenance.source_rulings`) and **P5g** (`holds = [{"id": "H1"}]`).

In-memory mutation of the tool (`p8_mut.out`). P3 and P7 fail in every row, including M0, because my exec copy is not reached by their `patch.object`; they are harness noise.
- **M1**, empty `source_rulings` allowed: **SURVIVES** the whole module.
- **M2**, the list check dropped: **SURVIVES**.
- M3, M4 and M6 are killed.

The tool itself refuses P5f, P5f2 (`[]`) and P5g (`p2_promote.out`), so the bytes are not in doubt. Cure, test-only: add P5f, P5f2 and P5g to P8.

### S4 — The promotion tool still accepts content substitutions beyond §5.1's letter
All executed in `p2_promote.out`. Each is ACCEPTED and yields different bytes:

| Probe | Substitution |
|---|---|
| N1 | Ruling A1's citation re-pointed to `README.md` with its true digest |
| N2 | Network-time `source_rulings` replaced by one README citation |
| N3 | All four hold texts set to `"x"` |
| N3b | H1 text changed to "H1 is lifted; claims allowed at 25G83." |
| N4 | `hold_enforcement = "x"` |
| N19 | `hold_enforcement` set to the obsolete `allow_claim_held` sentence, although §4.5 item 4 fixes that sentence "exactly" |
| N5 | `transaction` deleted |
| N6 | Extra record key `claim_hold_lifted` added |
| N6b | Extra hold H8 plus a duplicate H1 with empty text |
| N7 | D1..D7 texts set to `"x"` |
| N8 | D9 appended |
| N9 / N10 | Free-form `required_verification` and `reason` |
| N11–N13 | Network-time data fields changed: `per_member_state` emptied, `members_with_correction_during_capture` emptied, `authenticated_off_admission` flipped |
| P5j | Joint D8 replacement. Known since contract refuter 2 and still unruled |

- **The committed bytes are unaffected.** `p1_pins.out` shows the tool reproduces the committed file byte for byte, and the committed `hold_enforcement` equals the sentence of §4.5 item 4 exactly.
- The risk is on a future re-run from an edited `10-issuance-text.json`.
- The cure is code in the tool. The tool is not hold logic, but §6.2 bars further production edits in this transaction. Recommendation: record a named residual and open a post-merge lane that pins the sha256 of the issuance text in the tool beside `CANDIDATE_SHA256`. That one constant closes every N-case above at once.

### S5 — The records at the candidate state the superseded mechanism and digest
- `docs/decision_log.md:231` and `:12244` (D-185) carry digest `d6de84…d5ea`, the "three places" mechanism, `allow_claim_held=True` and `CLAIM_HELD_ACCEPTANCE_IDS`.
- `docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance/00-issuing-record.md:56`, `:279` and `:296` cite `d6de84…` at `8458f797`.
- `RUN_STATE.md` still cites `80c23036…`.
- The ruling in force (§7, "Record text") requires these to be replaced, and requires the d079 addendum's sentence about the bare `d079`.
- The activation record (items 81 and 95) shows this is planned. It must land before the pedagogy pass (step 8) and the cold final pass (step 10). I list it so the final pass checks the digest `d7076c78…` and the whole-file seal `d3e4da75…` in those texts.

---

## NIT

- **N-1** `tests/test_acc_25g83_rev5.py:211-215`: main's unpatched assertion "requires r7 predecessor" now runs only with the issuer's default patched to R6. This is ruled by §5.2 and strictly stronger against mutants that read the default. The unpatched case (real default) is no longer exercised; keeping both would cost two lines.
- **N-2** `tests/test_epoch_equivalence_check.py:78-81` patches, with `create=True`, names the tool no longer imports, so the patches do nothing. `p9_freeze.out`: a mutant that reads `calibration_bracketing.DEFAULT_ACCEPTANCE_BOUND_PATH` through the module attribute **SURVIVES**; the same mutant is KILLED once the source module's default is patched. This complies with the literal text of §5.2, which says "the tool's imported" names; it is weaker than the ruling's intent.
- **N-3** `joulewise/calibration_bracketing.py:236-238`: the default guard's message says "is claim-held" also when the path and id merely disagree (probe D4). It is correct as a refusal and misleading as a diagnosis.
- **N-4** `joulewise/claim_hold.py:15-18`: the hold matches the build string exactly. `" 25G83"` and `"25g83"` are not held (`p6_behaviour.out`, U1). `machine_os_build` strips, and G1 compares the file's build with the build table exactly, so I found no route. Noted for the hold refuter.
- **N-5** The C-5 scan covers only `joulewise/` and `scripts/`, as ruled. Twelve pack generators under `configs/campaigns/*/generate_configs.py` also name calibration paths; they name older files only, and any pack they write still meets the admission list.

---

## Charges that pass (executed)

**(1) Digest and pins** (`p1_pins.out`):
- The file's sha256 is `d7076c78ddab564c9b7eefa9a24b658bdbbdd29b685373de7cb66cf48c565c2e`. It equals `EPOCH_25G83_R1_ACCEPTANCE_BOUND_SHA256` and the registry pin.
- Input seal: the stored value, the recomputed value and the tool's `INPUT_SHA256` are all `e7363bdd…b011`.
- Whole-file seal: stored and recomputed are both `d3e4da75…420a`.
- Role `issued`, `claim_eligible` true.
- `promote(candidate, text)` equals the committed bytes, and the candidate's sha256 equals its pin `dbad7cc7…`.
- Build table: the keys of `REGISTERED_GENERATION_OS_BUILD` equal the registry's keys. For all 8 entries the file's own `identity_epoch.os_build` equals the table: seven are 25F84 and the new file is 25G83. Each file's id equals its key, and each relative path resolves to its path.
- `hold_enforcement` equals the ruled sentence exactly. `transaction` cites HOLD-BY-CONSTRUCTION-01 after A1.
- Nothing else in `joulewise/`, `scripts/`, `tests/` or `configs/` carries a stale file digest.

**(2) The checks §5.1 requires of the tool**, all REFUSED (`p2_promote.out`):
- P4a–P4f;
- P5a, P5b, P5f, P5f2, P5g;
- H5 with empty text;
- P5k, P5l, P5m;
- N15 (a fifth ruling), N16 (rulings reordered), N17 (wrong `derivation_sha256`), N18, N20.

The gaps are S3 and S4.

**(3) Tests from main not weakened.** I read `git diff 9eab16f8 b953f4b0 -- tests/` line by line:
- 12 files; 18 lines removed in total.
- Every removal is one of:
  - comment rewording;
  - `self.assertEqual(author_return_code, 0)`, which gained a message argument;
  - the two `"issued": "d079"` fixture lines, ruled by the d079 addendum;
  - the rev5 assertion moved under the patch (N-1, ruled by §5.2);
  - `continue` or inspection branches for the new id only, in `test_calibration_bracketing.py:3346-3350`, `:3363` and `:4252`. The id was not registered at main, so every assertion over main's inputs is kept;
  - the `test_floor_mint_pinsets_schema.py:60` set, extended by one name;
  - `verify_calibration_acceptance_corpus.py`, which gained an optional `--corpus-root` (the default is unchanged, and containment is still enforced);
  - `test_gen_state.py`, where the live-id set and count follow the queue: `WALLCLOCK-STEP-SOURCE-01` is DONE in `TASK_QUEUE.md:104`, and the exact-set assertion is kept.
- No test file was deleted, and no skip or expectedFailure was added.
- `test_arm_readiness_lifecycle.py` also gained a `machine_os_build` patch returning 25F84. That is allowed by the amendment rule in §4.5.
- **The breach of charge (3) is B1**: tests from main that were left untouched and now fail.

**(4) Census.** C-1..C-8 are GREEN in the tree. The four planted routes the ruling names each turn it RED. C-5's map equals what its pattern finds. The gaps are S1 and S2.

**(5) Default** (`p5_default.out`, `p6_behaviour.out`):
- The loader with no argument returns R7 at 25F84. The loader and the authenticator return `None` for the new file.
- The inspection function returns the new file with the hold's name and `file_sha256 d7076c78…`.
- The numbers table and the screen give `None` for the new id; R7's screen is `0.009724`.
- `_issued_d079`:
  - admits R7;
  - refuses the new id, both mixed shapes, the bare `d079`, a list value and a foreign selection.
- G1 by identifier refuses R7's bytes when its build entry is wrong or missing, and refuses R7 when its build is held in memory.
- Modified-source imports of the module:
  - (R7, R7) and (R6, R6) import;
  - these refuse with RuntimeError: the held file as the default; id R7 with the new file's path; id new with R7's path; id R7 with R6's path; an unregistered id; a `..`-spelled path.

## Test runs on the candidate (this seat)

- `test_claim_hold_census`, `test_claim_hold_routes`, `test_promote_calibration_candidate`, `test_calibration_dispositions`, `test_acc_25g83_rev5`, `test_epoch_equivalence_check`, `test_floor_mint_pinsets_schema`, `test_gen_state`, `test_epoch_continuation`: 203 tests, **1 failure** (the pinset test, B1).
- `test_reissue_calibration_acceptance`, `test_calibration_bracketing`, `test_mint_floor_artifact`, `test_mint_floor_artifact_generalized`, `test_arm_readiness_lifecycle`, `test_arm_readiness_evidence_author`, `test_arm_readiness_schemas`, `test_detection_floor`, `test_issue_calibration_acceptance_generation`, `test_run_campaign`: all rc=0.
- `test_validate_powermetrics_fiducial`: rc=1 (B1).
- The rest of the suite is the lead's `/tmp/d138-suite4-d528efb2` run at `b953f4b0`, still running when I finished. It had 257/271 modules done with exactly these four non-zero: pinsets, powermetrics_fiducial, validate_powermetrics_fiducial, calibration_exits.

## Limits

- I did not re-run `test_calibration_exits`. That row rests on the lead's log and my reading of `:5395-5416`.
- I did not run the whole suite.
- The mutation probes exec modified source in memory; they did not touch repository files.
- Hold routes (§6.1) belong to the hold refuter. I found none incidentally.
