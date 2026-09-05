# Delta re-audit — PR #292 CI-fix commits `f5abdea0..e1690f20` (fresh non-author, contract lens)

**Verdict: DEFECTS — 1 blocker, 0 should-fix, 4 nits.**

Reviewer: fresh Opus seat, no authorship of any commit in this range. Read-only in
`/Users/edr/code/JouleWise-wt-fb-metadata` at `e1690f20af2bd9122353713b54195121bb1ad2ae`; tree clean.
No file in the repository was edited except this report. Every digest quoted below was re-derived by
this seat in its own Python snippets (hash functions retyped locally, not imported from the fixture),
not copied from report 51.

Delta scope (`git log --oneline f5abdea0..e1690f20`): `c8ab5efb`, `c56e3e5c`, `e1690f20`.
`git diff f5abdea0..e1690f20 --stat`: `docs/paper/round7/dependence-sensitivity.md` (4 ±),
`tests/test_mint_floor_artifact_generalized.py` (68 ±), `tests/test_single_count_discipline_matrix.py`
(+65), five trace files. **No production module is touched by this delta.**

---

## BLOCKER

### B1 — the ruling-50 condition-4 comment amendment breaks the closed single-count reader census; CI is red

`tests/test_mint_floor_artifact_generalized.py:1294` (added by `e1690f20`) reads:

```
# single-count discipline object (ruling 50). SYNTHETIC_COMPONENT_SHA256S
```

`tests/test_single_count_discipline_census.py:25` defines
`MARKERS = re.compile(r"single_count_discipline|single.count.discipline|…")`, and
`scan_source` (`tests/test_single_count_discipline_census.py:293-295`) records a `<grep>` event for
every line matching it, in every `.py` under the scan roots. `assert_inventory`
(`tests/test_single_count_discipline_census.py:309-321`) requires the event multiset to equal the
reviewed `MANIFEST` exactly. `MANIFEST` has **no row for
`tests/test_mint_floor_artifact_generalized.py`** — because that file previously had zero marker
matches.

Executed:

```
$ R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_single_count_discipline_census
FAIL: test_closed_inventory_and_no_raw_bypasses (…SingleCountCensusTests…)
  File ".../tests/test_single_count_discipline_census.py", line 321, in assert_inventory
    raise AssertionError(f"reader census drift; added (with lines): {added}; stale: {stale}")
AssertionError: reader census drift; added (with lines):
  [(('tests/test_mint_floor_artifact_generalized.py', '<grep>', 'grep',
     '# single-count discipline object (ruling 50). SYNTHETIC_COMPONENT_SHA256S'), 1, [1294])]; stale: []
Ran 6 tests in 10.445s
FAILED (failures=1)
```

Introduced by this delta, proven by marker count at both ends:

```
$ git show f5abdea0:tests/test_mint_floor_artifact_generalized.py | grep -cE '<MARKERS>'   → 0
$ grep -cE '<MARKERS>' tests/test_mint_floor_artifact_generalized.py                        → 1
```

Why it reaches CI: `.github/workflows/ci.yml:66` shards over `shard_tests.discover_test_modules()`,
so `tests.test_single_count_discipline_census` runs. This delta exists to make CI green and instead
substitutes one red module for the ten it fixed. Report 51's acceptance list (ruling 50) named four
targets and did not include the census module, so the seat never saw it; the four named targets do
all pass (see Closure below).

Note the mechanism: `helper_source` (`tests/test_single_count_discipline_census.py:92-111`) strips
test-method bodies for `tests/` files but retains module-level text, so the *comment* mandated by
ruling-50 condition 4 is precisely the thing that is scanned, while the old-constant literals added
inside the test bodies are exempt.

Two cures, both cheap; the choice is the magistrate's because the census manifest is a reviewed
artifact: (a) add the one `('tests/test_mint_floor_artifact_generalized.py', '<grep>', 'grep',
'<that exact line>', 1)` row to `MANIFEST`, or (b) reflow the comment so no line contains the marker
phrase (e.g. break after "PR #292 v2") while keeping condition 4's content. (a) is the honest option:
the comment genuinely is a discipline reference.

---

## Q1 — CLOSURE against ruling 50's five conditions

**Condition 3 (oracle discipline) — SATISFIED, independently re-derived.** I built the fixture and
hashed with locally retyped copies of the two oracles (indented+sorted+`\n` for artifacts; compact
canonical for producers), never with mint code:

```
COMPONENTS(my oracle): ('dae1d432…91e7', 'c12749cc…5b9c')   PINNED: identical
PRODUCERS(my oracle) : ('0a9d4d5f…8100', 'a15195aa…f09a')   PINNED: identical
PRODUCER_SET(my)     : 02fca6e419bc2506a8595987bc0680f8fa86b09b8afce51ccb9ca3ddd1ff8f26  PINNED: identical
```

Also re-derived the two CLI pins from the real build captured under
`test_legitimate_report_reaches_legacy_authentication_after_preparse`:
`5d0b4baf…dc03`, `7cfc66ae…671f` — identical to `CLI_COMPONENT_SHA256S`
(`tests/test_mint_floor_artifact_generalized.py:1310-1313`). And the eighth pin, the phase-0 whole-file
digest, reproduced exactly (below). Not copied from mint output: the fixture *injects* these
constants into the pinset (`freeze_synthetic_v2_pinset`,
`tests/test_mint_floor_artifact_generalized.py:1337-1349`) and production then recomputes and compares,
so a copied-from-output pin would be tautological only if production and oracle shared code — they do
not, and I confirmed the two agree today (`generalized._artifact_sha256` returns the same two values).

**Condition 1 (per-constant byte diff) — SATISFIED, and independently reversible.** For every moved
pin I applied a discipline-only revert (the matrix test's `versioned(…, VERSIONS[0])`,
`tests/test_single_count_discipline_matrix.py:56-68`) and recovered the *old* constant exactly:

- components → `8ac980a5…0495`, `a8c19555…0d70` (the pre-delta values) ✔
- CLI components → `6325b71a…2cf6`, `258b512b…59ca` ✔
- producers: producer plans contain **no** discipline object (verified by string search); substituting
  only the old component hash into each plan yields `1d9bd87a…d74c` / `509e6b38…009d1` ✔
- producer set → `fe9c031e…7065` ✔

**Condition 2 (acceptance unchanged, asserted in code) — SATISFIED for the constants at issue.**
`tests/test_mint_floor_artifact_generalized.py:6274-6312` deep-copies the producer plans, restores the
old component hash, and asserts old pin, new pin, and byte-identical `calibration_acceptance` for both
the before and after plan (`acceptance_id d079_calibration_acceptance_v2_n17_r6`,
`artifact_sha256 0227bca3…`, `derivation_sha256 18d09aa9…`). See N2 for the scope caveat.

**Condition 4 (comment amended, not replaced) — SATISFIED in substance**
(`tests/test_mint_floor_artifact_generalized.py:1285-1301`): the D-079 sentence is kept, the amendment
names the date, PR, ruling, which constants moved and why, and which oracle each family uses. It is
also the line that trips B1.

**Condition 5 (counterfactual regression) — SATISFIED** (see Q3).

**Acceptance run (all executed by this seat, one target at a time, `R7F_CORPUS_ROOT` set):**

```
tests.test_mint_floor_artifact_generalized                       Ran 83 tests in 33.971s  OK (skipped=2)
…test_arm_readiness_dry_run …survives_repository_relocation      Ran 1 test in 53.423s    OK
…test_launch_window …accepts_relocation_and_refuses_content_change Ran 1 test in 136.883s OK
tests.test_single_count_discipline_matrix                        Ran 12 tests in 3.475s   OK
tests.test_dependence_sensitivity                                Ran 29 tests in 4.468s   OK
tests.test_single_count_discipline_census                        Ran 6 tests in 10.445s   FAILED (failures=1)  ← B1
```

---

## Q2 — the phase-0 floor pin is justified, and I reproduced its justification

The report's per-constant diff for `phase-0 base floor bytes`
(`docs/process_traces/2026-09-04-peer-audit/51-fb-v2-ci-fix-3-report.md:525-720`) shows eleven
discipline objects plus one other field: `provenance.calibration_plan.sha256`
`543329fd…8182` → `b44a28e5…7554`.

I verified this end to end without the report. Replicating
`test_phase0_base_floor_bytes_are_pinned` (`tests/test_mint_floor_artifact_generalized.py:6995-7044`)
— including its load-bearing fixed path `/tmp/joulewise-test-d165-phase0-floor-pin`, cleaned up after —
and hashing the written `floor.json`:

```
v2 file sha            : 9d3c2984fcd719a4f7292668cdb247faee7ac77c53302d84473989cddb22dd8f  (== new pin, line 7042)
pinset-sha substitutions: ['/provenance/calibration_plan']   (exactly one)
reconstructed v1 sha   : 9127a51d5f3cb53263c90afd5c63c94d29442a3f9127f11aa25d0498e3c72400  (== old pin)
```

That is: v2 bytes, with every discipline object reverted to v1 and that single embedded digest
reverted, reproduce the old pin bit-for-bit. Nothing else in the file moved — no acceptance field, no
numeric value, no path. The embedded digest is itself derived, not a literal: the phase-0 pinset's
self-hashes are computed by `_repair_v2_pinset_self_hashes`
(`tests/test_mint_floor_artifact_generalized.py:1316-1326`, called at three sites inside
`freeze_mixed_estimator_v2_pinset`), and I confirmed both producer plans of that fixture carry the
unchanged r6 acceptance bytes. So the phase-0 constant is justified. See N1 for a wording defect in how
report 51 labels it.

---

## Q3 — consequences for production

**No production file is in the delta.** `git show --stat` for all three commits: only
`docs/paper/round7/dependence-sensitivity.md`, the two test modules, and trace files. So no path in
`joulewise/arm_readiness_evidence.py`, `scripts/mint_floor_artifact_generalized.py` or launch_window
accepts or refuses anything differently as a result of these commits. The only indirect channel is
that the mint test module *is* evidence executed by `_derive_mint_trust`; the eight re-pins are all
exact v2 counterparts of the old values (Q1), so no assertion was loosened. No assertion was deleted
either — the mint-test diff is additive apart from one hasher swap (N4).

**The new regression is real, not hollow.**
`tests/test_single_count_discipline_matrix.py:158-222`,
`test_arm_readiness_evidence_derive_mint_trust_run_suite_rejects_v1_fixture_bytes`:

- It calls the real `evidence._derive_mint_trust`, so the production test-id selection
  (`joulewise/arm_readiness_evidence.py:2141-2148`) is real, and the `execute` seam asserts the
  affected id is among the ids production chose.
- Two seams only, both disclosed in the docstring: `_execute_unittest_suite_subprocess` (replaced by an
  in-process run of *the same real tests*) and `_committed_artifact`. Everything else in `_run_suite`
  (`joulewise/arm_readiness_evidence.py:746-786`) stays real, including the executed-module requirement
  and the `if not result.passed` refusal at lines 780-785 — which is the exact message the test asserts,
  `"focused suite refused: failures=0, errors=1"`.
- The counterfactual is production-shaped: it patches the *production builder*
  `generalized._build_v2_artifacts` to emit v1 discipline bytes, and the failure arrives through the
  production mint hash gate (`"aggregate/component hash mismatch"`), not through a test-side
  comparison. This satisfies the mutation-cure counterfactual rule — the input is v1 bytes, the call
  site is `_derive_mint_trust → _run_suite`.
- Failures inside the `execute` seam cannot be swallowed: `_run_suite` wraps them into a differently
  worded `EvidenceAuthoringError`, which the `assertRaisesRegex` would then reject.
- The embedded pin assertion (`tests/test_single_count_discipline_matrix.py:213-219`) checks the v1
  revert of the *real* build against the historical component pins, so it is a second independent
  witness of the Q1 reversibility.

---

## Q4 — dependence sheet regeneration is citation-only

`git diff f5abdea0..e1690f20 -- docs/paper/round7/dependence-sensitivity.md`: exactly two changed lines
(14 and 36), each a single `claims.py`, line `257` → `258` citation. No formula, number, threshold,
alpha, t-critical, or prose token changed. Verified against the tree:
`joulewise/analysis_engine/claims.py:258 def evaluate_claim`. Every other citation in the sheet is
still exact — `estimators.py:224 _ci_t_critical`, `estimators.py:450 estimate_paired_blocks`,
`distributions.py:48 _beta_continued_fraction`, `distributions.py:131 student_t_quantile`,
`distributions.py:166 two_sided_student_t_p_value`, `scripts/dependence_sensitivity.py:785
_model_result`. `tests.test_dependence_sensitivity` (29 tests) passes. No other doc under
`docs/paper` or `docs/contracts` carries a `claims.py` line citation, so no sheet was left stale.

---

## Q5 — other findings (nits)

**N1 (nit) — report 51 mislabels the one non-discipline field in the phase-0 diff.**
`docs/process_traces/2026-09-04-peer-audit/51-fb-v2-ci-fix-3-report.md:43` asserts "Every
removed/added field outside a discipline object is a component or producer-set hash proved by the
preceding independent oracle", and line 39 calls it "the producer-set digest". The field is
`provenance.calibration_plan.sha256` — the pinset **file** digest, one hop further out than the
producer-set hash it contains. The chain is real (I reproduced it), but a future reader checking the
claim literally will not find a producer-set hash there. Correct the wording in the ruling record.

**N2 (nit) — condition 2 is asserted in code for the synthetic producer set only.** The r6 acceptance
byte-identity assertion lives in `test_default_only_v2_output_remains_byte_identical_to_golden_oracle`
and covers the two synthetic plans. The mixed-estimator fixture behind the phase-0 pin also has two
producer plans carrying the same r6 acceptance, and its component hashes also moved; their acceptance
stability rests on report 51's diff, not on a code assertion. I checked them by hand and both are
byte-identical to `acceptance_bytes`. If condition 2 is meant to bind every plan whose pin moved, one
more assertion in the phase-0 path would close it.

**N3 (nit) — the v1 golden constants now live in two files with no cross-reference.**
`tests/test_mint_floor_artifact_generalized.py:6276-6285` and
`tests/test_single_count_discipline_matrix.py:215-217` each hardcode `8ac980a5…` / `a8c19555…`. The
amended comment points at report 51 but not at the matrix-test copy, so a future re-pin will find only
one of the two. A one-line pointer in the comment would fix it.

**N4 (nit) — the golden test no longer compares the *production* hasher to the pins.**
`tests/test_mint_floor_artifact_generalized.py:6272` changed `generalized._artifact_sha256(row)` to
`_fixture_artifact_sha256(row)`. This is what condition 3 asks for and is not a defect, but it removes
the only direct equality between production's hasher and the golden constants. Coverage survives
indirectly (the mint gate compares its own `_artifact_sha256` output against the literal pins injected
into the pinset), and I confirmed the two functions agree today. Worth a sentence in the comment so the
next reviewer does not re-litigate it.

**Not a defect, recorded for the file:** `docs/paper/fill-rehearsal/dominance-reproduced-*.json` still
carry `attribution_floor_plus_claim_side_bound.v1`. These are historical rehearsal artifacts consumed
as fixtures, the v1 id remains a live constant in `joulewise/detection_floor.py`, and nothing in this
delta touched them.

---

## Recommendation

Do not merge on this head. B1 is a one-line cure in a reviewed manifest; after it lands, re-run
`tests.test_single_count_discipline_census` plus the four ruling-50 acceptance targets, and take a
delta over the cure. Everything else in `f5abdea0..e1690f20` verifies: all eight pins independently
re-derived, all eight reversible to their historical values under a discipline-only revert, acceptance
bytes unmoved, the counterfactual regression genuinely exercising the production call site, and the
dependence sheet limited to two source-line citations.
