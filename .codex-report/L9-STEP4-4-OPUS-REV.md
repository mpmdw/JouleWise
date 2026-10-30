VERDICT: ACCEPT_WITH_FIXES

# L9-STEP4-4 delta review, seat L9-STEP4-4-OPUS-REV

I reviewed `c2ecb9588`, the only code commit after `901956944` (merge `492a30f42` excluded), from branch
`review/2026-10-30-l9-step4-4-opus-rev` at `a7e00c9f7`. I read `.codex-report/L9-STEP4-4.md` as claims to check.
Synthetic data only: I did not open or search any real block-5, block-6 or BYTES data. Evidence is in
`.codex-report/l9-step4-4-opus-rev/`.

The commit does what the lead ruling says, and does nothing more:

- exactly `window_evidence_precheck_missing`, `campaign_cooldown_evidence_missing` and `idle_window_suspect` are added to `r3`;
- the classifier logic is unchanged (only a docstring);
- the regenerated table is the blind generator's output plus `HEADER` and `RULING`, byte for byte;
- no exit-1 report can reach `ok`, the p42 exit or an outcome class through the change.

Both fixes below are test-strength gaps, not wrong behaviour. Each could let a future change silently break the
ruling's premises.

## Findings (ranked)

**F1 (fix, low-medium). The static proof for the claim-gate codes only scans the generator's 11 modules, but step-4
cell reasons also come from modules outside that list.**
`tests/b5_analysis/test_step4_reason_table.py:197` walks only `self.table['modules']`. The same file shows the gap:
`R3_PINS` pins `calibration_acceptance_bound_stale` to `joulewise/calibration_bracketing.py` (`:82`), a producer of
step-4 cell reasons that is not among the 11. The extractor also imports `joulewise/b5_analysis/kept_units.py`,
`joulewise/dominance_closeout.py`, `joulewise/calibration_ledger.py` and `joulewise/cli.validate_bundle`, and
`scripts/extract_detection_floors.py` drives it. None of these is scanned.

Mutant M11 (`mutants_results.txt`) makes `calibration_bracketing.py` return `("calibration_acceptance_bound_stale",
"paired_block_incomplete")`. It survives every test, including the claim-gate test.

The claim is true today. A repo-wide grep finds the two literals only in four places:

- `joulewise/analysis_engine/__init__.py` (the claim gate, lines 562-1015);
- `joulewise/analysis_engine/claims.py`;
- `inputs.py:3590` and `:3746`, both as the code argument of `stop_if_member_code_on_kept_unit`;
- `scripts/run_campaign.py:8846-8865`, the campaign runner, which is not on the step-4 path.

So the test proves "not in the 11 blind modules", which is narrower than its name and the report's claim ("cannot
reach a step-4 cell").

Fix: scan every `joulewise/**/*.py` plus `scripts/extract_detection_floors.py`, with an explicit allowlist for
`joulewise/analysis_engine/__init__.py` and `joulewise/analysis_engine/claims.py` (the claim-gate modules). The
alternative is to scan the import closure of `scripts.extract_detection_floors`. Either way, keep the stop-argument
exemption, and assert that `paired_block_incomplete` occurs at least once as a stop argument, so the walk cannot pass
vacuously.

**F2 (fix, low-medium). Nothing tests behaviourally that two of the three codes actually reach a cell.**
The ruling's premise is "member-level codes that can reach a step-4 extractor cell". The only evidence for it is a
comment (`test_step4_reason_table.py:84-86`: "the extractor extends every member's reasons with them, only
cooldown_cap_hit is filtered"). r14 (`test_floor_kept_units.py:946-974`) wraps `fe._evaluate_member` and injects the
reason itself, so it does not exercise the precheck-forwarding path.

I mutated the forwarding filter at `joulewise/floor_extraction.py:2243` so that it also drops a code
(`forwarding_mutants_test_floor_extraction.txt`, mutant M12):

| Code dropped by the filter | Result |
|---|---|
| `window_evidence_precheck_missing` | survives the targeted step-4 tests and all 145 tests of `tests/test_floor_extraction.py` |
| `idle_window_suspect` | survives `tests/test_floor_extraction.py` |
| `campaign_cooldown_evidence_missing` | killed (3 failures, e.g. `test_missing_campaign_evidence_fails_the_whole_cell`) |

Fix: add a test with no seam, under `tests/b5_analysis/`, on synthetic bundles through `extract_cells`:

- one member whose summary has no `window_evidence_precheck` root;
- one member with `measurement_quality.idle_window_suspect: true` and an `energy_request_j` metric.

Assert that each code is in the refused target cell's `refusal_reasons` and that
`classify_step4_exit(1, report, spec) == 'extraction_cell_r3_refusal'`.

**F3 (note, for the ruling; extends NEEDS_RULING 3). Tooling-origin causes now go the R3 cure route.**
`window_evidence_precheck` (`joulewise/analysis_engine/inputs.py:4061-4079`) emits `window_evidence_precheck_missing`
in five cases:

- the precheck root is missing;
- `reasons` is malformed;
- a raw reason is not reducer vocabulary;
- `eligible` is not a boolean;
- the input is legacy (`claim_eligibility`).

`campaign_cooldown_evidence_missing` (`:4097-4101`) fires whenever the campaign-level cooldown evidence is not
verified, which includes a wiring fault in `campaign_cooldown_evidence(runs_root, manifest_id)`
(`floor_extraction.py:3170`). All of these now send the analysis to an Ed ruling rather than fix-and-rerun. This is
plan-literal and stop-side, so nothing passes. Worth one line in the ruling text.

**F4 (note). The registered JSON does not record the -4 amendment.**
`configs/analysis/b5/step4_reason_classes.json:1981` still reads "L9-STEP4-3 lead ruling, RUN_STATE items 132-133 and
138". The amendment lives only in the test docstring and the report (report decision 3; the R1 shape test pins the key
set). Someone auditing the JSON alone cannot see why `r3 ⊄ mask`. Fix, optional: amend the `ruling` string, which is a
value not a key, so the shape test is unaffected. Change `RULING` to match and the regeneration test stays green.

**F5 (note).** `test_R2_p42_cell_reasons_are_irrelevant_to_the_registered_exit`
(`test_step4_exit_classes.py:240`) uses only `kept_units_below_minimum` as its R3 code. My differential covers all
three new codes on p42 cells (no change), so this is cosmetic. Adding one new code to the loop would cost nothing.

## Execution

**(1) Classification of every code, before and after** (`classification_diff.txt`, `classify_all.py`).

- I probed each of the 1942 codes (the table's 42 mask and 1898 tooling codes, the r3 codes, `fixed_n_plan_incomplete`
  and one unlisted code) five ways on worktrees at `492a30f42` and `a7e00c9f7`. The five probes were: refused target
  only, refused p42 only, both (all exit 1), exit 0 and exit 2. That makes 9710 probes.
- `901956944` gives the same classification as `492a30f42`.
- Exactly 6 probes changed: the target-only and target+p42 probes of the three codes, each going from
  `extraction_cell_tooling_refusal` to `extraction_cell_r3_refusal`.
- Nothing else changed class, including `idle_window_suspect_unknown`, `cooldown_cap_hit`, `paired_block_incomplete`
  and `fixed_n_plan_incomplete`.

**(2) No route to ok, the p42 exit or an outcome class** (`rand_diff.py`, `rand_diff_output.txt`).

- The `r3` lookup (`joulewise/b5_analysis/steps.py:107-110`) runs only after the exit-0 return (`:58-59`), the
  non-0/1 return (`:60-61`) and the p42 return (`:99-101`). Adding codes to `r3` can only turn the final
  tooling return into an R3 return.
- `extraction_cell_r3_refusal` is in `dry_run_refusal_classes.json` `tooling_refusal` and not in `outcome_class`.
  `dry_run.step_4` (`dry_run.py:796-800`) passes it through as `code`.
- A randomized differential over 200,000 four-cell reports, exit status drawn from {0, 1, 2}, compared
  classification plus `step_record` status:
  - 16,190 changes, all of them `(1, tooling → r3, tooling_refusal)`, each with an added code on a refused non-p42
    cell;
  - 0 unexpected changes;
  - 0 exit-1 reports reach `ok` or `outcome_class`.

**(3) The table is the blind generator output plus `HEADER` and `RULING`.**

- `make_table.py` sha256 is `051c13b2…a549d2` and is unchanged since `901956944`.
- Fresh generator output, wrapped with the test module's `HEADER` and `RULING` and dumped with `json.dumps(indent=1)`,
  equals the registered file byte for byte.
- `modules`, `mask_rule`, `mask`, `tooling`, `source` and `step4_rule` are identical to `492a30f42`.
- `mask` and `tooling` equal the blind `CLASS_TABLE.json` at `08ea5c958`.
- The `r3` delta is exactly the three codes. `RULING['r3']` is sorted and has 11 entries.

**(4) The static proof.** It is correct for the 11 modules. M8, which adds `reasons.append("paired_block_incomplete")`
to `inputs.py`, and M9, which uses `fixed_n_plan_incomplete` as a stop argument, are both killed. I broke it outside
its scan scope (M11), which is F1. The behavioural half (the precheck forwards only `REDUCER_REASON_CODES` and maps
anything else to `window_evidence_precheck_missing`, `inputs.py:4067-4068`) holds: neither claim-gate code is in
`REDUCER_REASON_CODES`.

I also checked the plan text. Plan 2.2 bullet 3 names all five codes literally, plus the cooldown-cap exclusion.
The three added codes are emitted by the precheck and, on a kept member, are not stopped by
`_stop_kept_member_exclusion` (`floor_extraction.py:2399-2404`, which only stops the anchor fallback and cap-hit), so
they land in cell reasons. That matches the ruling.

**(5) Mutants.** Twelve ran on the targeted tests (`test_step4_reason_table`, `test_step4_exit_classes`, r14), and
three more on the forwarding filter against `tests/test_floor_extraction.py`. Details are in `mutants_results.txt`
and `forwarding_mutants_test_floor_extraction.txt`.

| # | Mutant | Result |
|---|---|---|
| M1 | JSON drops `idle_window_suspect` (RULING kept) | killed (4) |
| M2 | JSON and RULING both drop it | killed (3: plan-named, r3-only, invariant) |
| M3 | JSON and RULING add `paired_block_incomplete` | killed (2) |
| M4 | JSON, RULING and pin add `cooldown_cap_hit` (widening) | killed (4) |
| M5 | JSON and RULING add `idle_window_suspect_unknown` | killed (3) |
| M6 | classifier checks r3 before the p42 exit | killed (6 failures across 4 tests, r14 included) |
| M7 | classifier checks only the first reason | killed (precedence test) |
| M8 | precheck appends `paired_block_incomplete` | killed (claim-gate test) |
| M9 | `fixed_n_plan_incomplete` as a stop argument | killed (R1 and claim-gate tests) |
| M10 | `campaign_cooldown_evidence_missing` emission made indirect | killed (pin test) |
| M11 | claim-gate literal in `calibration_bracketing.py` | **survives** (F1) |
| M12 | forwarding filter drops `window_evidence_precheck_missing` | **survives** (F2) |
| M12b | forwarding filter drops `idle_window_suspect` | **survives** `tests/test_floor_extraction.py` (F2) |
| M12c | forwarding filter drops `campaign_cooldown_evidence_missing` | killed by `tests/test_floor_extraction.py` (3) |

**(6) The whole `tests/b5_analysis` directory, at `a7e00c9f7`, on a clean tree.** TMPDIR was under /tmp, outside the
checkout.

```
TMPDIR=/tmp/l9rev_full JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b5_analysis -t .
```

Exact tail (`full_run_tail.txt`):

```
----------------------------------------------------------------------
Ran 1029 tests in 3085.343s

OK (skipped=13)

real	51m59.442s
EXIT 0
```

No `ERROR:` or `FAIL:` lines. This matches the lane's count (1029, 13 skipped).

## Report claims checked

- Every claim in the summary, counterfactual table, files-changed list and decisions 1-5 matches what I ran. There is
  one exception: the claim-gate sentence is true only within the 11 modules (F1).
- The AST-guard self-check the report describes is reproduced by M8 and M9.
- NEEDS_RULING 1-3 and the open issues carried forward from the prior reviews are fairly stated. F3 adds detail to
  NEEDS_RULING 3.
