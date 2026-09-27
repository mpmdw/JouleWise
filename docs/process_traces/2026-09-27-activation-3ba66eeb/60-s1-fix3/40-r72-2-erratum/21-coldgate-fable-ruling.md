# Cold gate S1-R72-2-ERRATUM-01: ruling on one test row's stated counterfactual

Judge: Fable 5.1, cold session. Tree: `/Users/edr/code/JouleWise-wt-r722-1c3b3ac9`, detached at `00b0dc68`. Session clock: 07:42 to 07:51 PDT, 2026-09-27 (inside the 20-minute budget). Scratch: `/tmp/cg_r722/`. No repository file was edited (`git status --short` empty after every probe).

## 0. Contamination disclosure (written first, before any read)

The harness put three texts into this session before my first action: the global `CLAUDE.md`, this worktree's `CLAUDE.md`, and the index of the memory store (one line per entry). I did not open any of them and did not read `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAUDE*.md`, `AGENTS.md`, the decision log, or any memory or skill file. The index holds one line that touches this gate: it says the S1 commit `00b0dc68` "needs R72-2 erratum". It states no preferred outcome. Everything ruled below rests on the three sources I read (the ruling, the seat report, the code) and on probes I ran.

One protocol deviation, disclosed: my third probe command ran past the tool's 120 s limit and the harness moved it to the background. I stopped it at once and confirmed no process was left. The part of it that had finished is used below (E5). The part that had not finished is marked NOT EXECUTED (§7).

## 1. Terms used here

- **Aborted attempt.** A run that stopped during its idle measurement, before any workload ran. It holds no energy result.
- **Salvage license.** The record that `inspect_preworkload_abort` returns for an aborted attempt. A campaign uses it to treat that attempt as excluded.
- **Summary.** The file `summary_metrics.json` of an attempt. In an aborted attempt, every result field in it is `null`.
- **Measurand name.** One of the 17 result field names listed in `_MEASURAND_FIELDS` (`salvage_dangler.py:153-173`), for example `gross_energy_j`.
- **Guard A, the null test.** The check at `salvage_dangler.py:778-779`. It refuses if any measurand name holds a value.
- **Guard B, the unknown-field test.** The check at `salvage_dangler.py:780-789`. It refuses if any summary key holds a value and is not one of six allowed names.
- **Refuses.** Raises `SalvageAuthorizationError`. No license is returned.
- **Row.** One line of a ruling's test table: a production site, an input, an expected result, and a counterfactual.
- **Counterfactual.** The specific wrong implementation under which the row's test must fail. The test **goes RED** when it fails and is **GREEN** when it passes.
- **Mutant.** A scratch copy of the production module with one deliberate wrong edit, made outside the repository, used to show that a test goes RED.
- **The seat.** The model session that implements the test changes. **The refuter.** The model session that checks the result.

## 2. The question

Row R72-2 of the ruling S1-FIX3-RETURNS-01 (§4, line 179) states this counterfactual:

> a function without the test of `_MEASURAND_FIELDS`, which returns a license for an attempt that holds energy.

The seat showed that removing that one test does not return a license, because a second, independent test still refuses. The row's author (the earlier gate) marked the mutation NOT EXECUTED, so the stated outcome was never checked. The seat asks which of two repairs holds: accept a RED that is pinned to the refusal message, or amend the counterfactual to remove both guards.

## 3. The two guards, quoted from the tree

`joulewise/salvage_dangler.py:776-789` at `00b0dc68`:

```python
776    if summary.get("status") != "failed":
777        raise SalvageAuthorizationError("summary status is not failed")
778    if any(summary.get(field) is not None for field in _MEASURAND_FIELDS):
779        raise SalvageAuthorizationError("failed attempt contains measurand bytes")
780    unknown_nonnull = {
781        key
782        for key, value in summary.items()
783        if value is not None and key not in _ALLOWED_FAILED_SUMMARY_NONNULL
784    }
785    if unknown_nonnull:
786        raise SalvageAuthorizationError(
787            "unknown non-null failed-summary fields: "
788            + ", ".join(sorted(unknown_nonnull))
789        )
```

Guard A is lines 778-779. Guard B is lines 780-789. The six allowed names (`:174-183`) are `status`, `failure_message`, `failure_reason`, `idle_baseline`, `measurement_quality`, `summary_provenance`.

**Why they overlap.** Guard B refuses every key that holds a value and is not one of the six. None of the 17 measurand names is among the six (E1: the two sets share no name). So every input that guard A refuses, guard B would refuse too. Guard A runs first, which is why its message is the one seen on the tree.

## 4. Executed evidence

All probes ran in the foreground with `/opt/homebrew/bin/python3` (3.14.7), `PYTHONDONTWRITEBYTECODE=1`, against the module at `/Users/edr/code/JouleWise-wt-r722-1c3b3ac9/joulewise/salvage_dangler.py` unless a mutant is named. Scripts: `/tmp/cg_r722/probe.py`, `make_mutants.py`, `row_r72_2.py`, `row_current.py`.

**How a guard is switched off inside a test.** The test replaces the module constant the guard consults, for the length of one call: guard A by setting `_MEASURAND_FIELDS` to an empty set, guard B by adding the input's name to `_ALLOWED_FAILED_SUMMARY_NONNULL`. E4 shows this gives the same results as deleting the guard's lines from the source.

**E1. Set overlap.** `measurand n: 17 | overlap with allowed set: []`

**E2. The seat's probe, reproduced and extended.** Input: a copy of the fixture `tests/fixtures/salvage_dangler/r5a_idle_abort`, prepared as the committed test prepares it, then `gross_energy_j: 12.5` added to its summary.

| Probe | Guards in force | Result (exact) |
|---|---|---|
| P0 | both, **no energy added** | a license: failure at 100.0 s, telemetry 99.8 s to 100.171 s, teardown 0.171 s, `licensed: true` |
| P1 | both | refused: `failed attempt contains measurand bytes` |
| P2 | guard A off | refused: `unknown non-null failed-summary fields: gross_energy_j` |
| P3 | guard B off | refused: `failed attempt contains measurand bytes` |
| P4 | both off | **a license**, key for key the license of P0 |
| P5 | both, after the patches ended | refused: `failed attempt contains measurand bytes` |

P1 and P2 are the seat's two lines. The seat's probe is confirmed.

**E3. All 17 names.** The four cases P1 to P4 were repeated with each measurand name in turn set to 12.5. All 17 gave the same four results as `gross_energy_j`, with the name in guard B's message changing to match.

**E4. Source mutants.** Seven scratch copies of the package under `/tmp/cg_r722/mut/`, each with one edit to `salvage_dangler.py`. Two test forms were run against each: the row as committed at `00b0dc68` (`tests/test_bfgs_consumer_sweep.py:1439-1450`, copied to `row_current.py`), and the replacement row ruled in §6 (`row_r72_2.py`).

| Mutant | The wrong edit | Does it license an attempt that holds energy? | Row as committed | Replacement row |
|---|---|---|---|---|
| `M_A` | guard A's two lines deleted | no (guard B refuses) | RED, on the message | RED, 17 of 17, on the message |
| `M_B` | guard B's `if` block deleted | no (guard A refuses) | **GREEN: not detected** | RED, 17 of 17: `SalvageAuthorizationError not raised` |
| `M_AB` | both deleted | **yes** | RED: `SalvageAuthorizationError not raised` | RED, 17 of 17, same |
| `M_allow_gross` | `gross_energy_j` added to the six allowed names | no (guard A refuses) | **GREEN: not detected** | RED, 1 of 17 |
| `M_drop_gross` | `gross_energy_j` removed from the 17 | no (guard B refuses) | RED, on the message | RED, 1 of 17, on the message |
| `M_move_gross` | `gross_energy_j` moved from the 17 to the six | **yes** | RED: not raised | RED, 1 of 17 |
| `M_move_energy_request` | `energy_request_j` moved from the 17 to the six | **yes**, for that name | **GREEN: not detected** | RED, 1 of 17 |

**E5. Tree result of both forms.** Row as committed: `OK`. Replacement row: `Ran 1 test in 0.033s, OK`.

**E6. An existing test of guard B.** `tests/test_salvage_dangler.py:283-290` adds the key `future_measurement` and expects a refusal matching `unknown non-null`. Read, not run (§7).

## 5. Findings

**F1. The seat is right on the fact.** With guard A alone removed, no license is returned (P2, `M_A`). The outcome the row states cannot occur under the counterfactual the row states.

**F2. One sentence of the brief put to me is wrong, and I correct it.** The brief says "the tree's failed-attempt fixture already carries measurand bytes". It does not. The fixture's summary holds `null` in all 17 measurand names, and the unmodified fixture is licensed (P0). The seat's probe line reads `tree` followed by the refusal message `failed attempt contains measurand bytes`; that is the result for the input **with** `gross_energy_j: 12.5` added, on the unmodified tree code. The seat's report is accurate. The sentence is a misreading of its label.

**F3. Neither of the seat's two options is sufficient alone.**

- *Accept the message-pinned RED only.* The defect the row exists for is a license returned for an attempt that holds energy. Under this option no test ever shows that outcome, and the row's text keeps a statement that is false. E4 also shows the committed form misses three wrong edits, one of which (`M_move_energy_request`) is the defect itself.
- *Remove both guards only, and loosen the expectation to any refusal.* Then deleting guard A alone passes unseen, and the project is left with one guard where the allowlist's reason text claims two tests ("each measurand is null, each other key is null or named in `_ALLOWED_FAILED_SUMMARY_NONNULL`").

**F4. What travels when the defect occurs.** With both guards off, the license returned is identical to the license of the attempt with no energy (P4 equals P0), and it does not hold the value 12.5. So the defect is not that a number leaks into the license. It is that an attempt which did measure something is certified as having measured nothing, and the campaign then excludes it. The row's text must say this, because "an energy value reaches a license" would send a reader looking for a field that is not there.

## 6. Ruling

**The row carries three counterfactuals. The defect's RED needs both guards removed and is pinned to the outcome. Each guard alone is pinned separately, guard A to its message.**

### 6.1 Replacement text for row R72-2 (replaces line 179 of the ruling's §4 table, all five columns)

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R72-2 | `salvage_dangler._inspect_preworkload_abort`: the null test at `:778-779` and the unknown-field test at `:780-789` | the fixture of R72-1, with one of the 17 names of `_MEASURAND_FIELDS` set to `12.5` in its summary; repeated for each of the 17 names, which the test writes out as literals | `SalvageAuthorizationError` whose whole message is `failed attempt contains measurand bytes` | **(a) The defect.** A function with neither test. It returns a license (`licensed` is `True`) for an attempt that holds a result. RED is pinned to the outcome: no `SalvageAuthorizationError` is raised. **(b)** A function without the null test only. It still refuses, with the message `unknown non-null failed-summary fields: <name>`. RED is pinned to the message. **(c)** A function without the unknown-field test only. It still refuses with the expected message, so the tree assertion stays GREEN; the RED comes from the row's second assertion, which switches the null test off and expects the refusal of (b). GREEN on the tree and RED under (a), (b) and (c): executed (S1-R72-2-ERRATUM-01, E2 to E5). |

### 6.2 Answers to the three points put to me

1. **One guard or both?** Both, for the RED that shows the defect (a license is returned). One, for each of the two REDs that show a guard has gone missing.
2. **What is each RED pinned to?** (a) to the outcome "no exception, and the returned license has `licensed` equal to `True`". (b) to the exact message of guard B, including the field name. (c) to the absence of guard B's refusal when guard A is off.
3. **Is the seat's existing message-pinned RED accepted?** Its fact is accepted. Its form is replaced: `assertRaises(AssertionError)` around a message match passes both when another guard refuses and when a license is returned, so it cannot tell a second line of defence from the defect. That is why it missed `M_B`, `M_allow_gross` and `M_move_energy_request`.

### 6.3 Why the input widens from one name to 17

The defect is stated for any result value, and the allowlist's reason names "the 17 names". With `gross_energy_j` as the only input, moving any of the other 16 names from the measurand set to the allowed set licenses an attempt that holds that result, and the row stays GREEN (`M_move_energy_request`, E4). The names are written as literals in the test so that removing a name from the production constant cannot also remove it from the test. Cost on the tree: 0.033 s for all 17 (E5).

### 6.4 What is not changed

The allowlist row for this read, its class `non_claim` (i), its reason text, the count of 119 rows, rows R72-1 and R72-3, and every other amendment. No production code.

## 7. The seat's next step (test-only)

**WRITE_SCOPE** (the closed list of files the seat may edit): `tests/test_bfgs_consumer_sweep.py` only. `tests/test_salvage_dangler.py` is not needed and is not in scope.

**Step 1.** In `test_salvage_non_claim_rows`, replace lines 1439-1450 (from `summary_path = changed / "summary_metrics.json"` through the end of the `patch.object` block) with the block below, at the same indentation. It is the body of `/tmp/cg_r722/row_r72_2.py`, which ran GREEN on the tree and RED on all seven mutants.

```python
            summary_path = changed / "summary_metrics.json"
            clean_summary = json.loads(summary_path.read_text(encoding="utf-8"))
            measurands = (
                "decode_latency_s", "energy_bound_terms_j", "energy_output_token_j",
                "energy_request_j", "energy_token_j", "energy_uncertainty_status",
                "energy_variance_terms_j2", "gross_energy_j", "idle_mean_uncertainty",
                "idle_subtracted_energy_j", "inter_token_throughput_tokens_s",
                "phase_energy_j", "suite_metrics", "throughput_tokens_s", "ttft_s",
                "uncertainty", "window_evidence_precheck",
            )
            self.assertEqual(len(set(measurands)), 17)
            measurand_refusal = r"^failed attempt contains measurand bytes$"
            for name in measurands:
                with self.subTest(measurand=name):
                    summary_path.write_text(
                        json.dumps({**clean_summary, name: 12.5}), encoding="utf-8")
                    unknown_refusal = r"^unknown non-null failed-summary fields: " + name + r"$"
                    no_null_test = patch.object(
                        salvage_dangler, "_MEASURAND_FIELDS", frozenset())
                    no_unknown_test = patch.object(
                        salvage_dangler, "_ALLOWED_FAILED_SUMMARY_NONNULL",
                        salvage_dangler._ALLOWED_FAILED_SUMMARY_NONNULL | {name})
                    with self.assertRaisesRegex(SalvageAuthorizationError, measurand_refusal):
                        inspect_preworkload_abort(changed)  # R72-2 GREEN
                    with no_null_test:  # R72-2 (b), (c): the unknown-field test refuses alone
                        with self.assertRaisesRegex(SalvageAuthorizationError, unknown_refusal):
                            inspect_preworkload_abort(changed)
                    with no_unknown_test:  # the null test refuses alone
                        with self.assertRaisesRegex(SalvageAuthorizationError, measurand_refusal):
                            inspect_preworkload_abort(changed)
                    with no_null_test, no_unknown_test:  # R72-2 (a) RED: a license is returned
                        with self.assertRaises(AssertionError):
                            with self.assertRaises(SalvageAuthorizationError):
                                inspect_preworkload_abort(changed)
                        self.assertIs(inspect_preworkload_abort(changed)["licensed"], True)
```

One difference from my scratch run, stated so the seat is not surprised: in the committed test the directory `changed` also has every `power_w` multiplied (row R72-1). My scratch copy left the trace as it was. Row R72-1's GREEN on the tree shows the multiplied trace is licensed the same, so the last assertion should hold; if it does not, the seat returns that with the output and edits nothing else.

**Step 2.** Show GREEN on the tree: the test method `ConsumerSweepTests.test_salvage_non_claim_rows`, then the seat's two whole-suite checks and both builder checks as in round 3b.

**Step 3.** Show RED under source mutants (a), (b), (c): three scratch copies of the package outside the repository, with guard A's lines deleted, guard B's `if` block deleted, and both deleted. `/tmp/cg_r722/make_mutants.py` builds them; the seat may reuse it or write its own. Report the failing assertion's message for each.

**Step 4.** Return. Commit nothing; the lead commits.

**Next gate, under the ruled stop rule:** one refuter pass on the merge candidate. No further cold gate is called for by this erratum.

## 8. Not executed

- **The committed test method on the tree** (`tests.test_bfgs_consumer_sweep.ConsumerSweepTests.test_salvage_non_claim_rows`). Tried twice: once inside the command the harness moved to the background, once under an 80 s cap, which it exceeded (exit 142, killed by the timer). I saw no pass and no failure. The R72-2 lines of it were run as a scratch copy (E5); the seat's report states the whole suite was green.
- **`tests/test_salvage_dangler.py`.** Not run. Line 283-290 was read only.
- **The replacement block inside the real test file.** It ran in a scratch file with its own copy of the fixture preparation, not spliced into `tests/test_bfgs_consumer_sweep.py`.
- **Whether a campaign that receives a license for an attempt holding a result does exclude it.** The call path beyond `inspect_preworkload_abort` was not read in this session; the statement in F4 about exclusion rests on the earlier ruling's definition of the license.
- **Values other than `12.5`.** Guard A tests `is not None`, so `0`, `0.0`, `false`, `""`, `{}` and `[]` should be refused too. Read from the quoted line, not run.

## 9. Summary for Ed

1. A test was written on the claim that deleting one safety check would let the salvage code certify a run as "stopped before measuring anything" even though its results file holds an energy number; I re-ran it and that claim is false, because a second independent check still refuses (both checks quoted, all 17 result field names tried).
2. Ruling: the test row now states three wrong implementations it must catch: both checks gone (a certificate is wrongly issued; the failure is pinned to that outcome) and each check gone alone (pinned to which refusal message appears). The old form missed 3 of 7 deliberately broken copies of the code; the new form catches 7 of 7 and passes on the real code.
3. Next: the implementing model replaces about 12 lines in one test file (no production code), then one checking model reviews the merge candidate. One item I could not finish in the time limit is the full committed test method, which ran longer than 80 seconds; it is listed as not executed.
