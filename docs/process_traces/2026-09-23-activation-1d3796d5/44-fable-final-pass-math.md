VERDICT: MERGE

# Cold Fable 5.1 final pass: MATH importer, feat/2026-09-23-math-importer at a53a6b97 (base 313efcca; current origin/main 64d4c034)

Session: detached worktree /Users/edr/code/wt-1d3796d5-fablemath at a53a6b97, `git status --short` empty, no repository file edited, nothing under /Users/edr/night-custody touched, no launchctl/sudo/model load. Every line below was executed this session unless marked NOT EXECUTED. Scratch trees under /tmp/fp44 only.

## Q1. Mechanical check (ruling 40 steps 1-4)

1. **Dictated diffs == a53a6b97.** `git archive ed1c8205` to /tmp/fp44/base, `git archive a53a6b97` to /tmp/fp44/head. The two dictated diffs carry absolute prefixes (`a/Users/edr/code/wt-1d3796d5-fablemath/…`, `b/tmp/fablemath/repo/…`); after rewriting only those prefixes to `a/` and `b/`, `git apply --check -p1` passed and `git apply` applied both. `diff -r base head` printed nothing: **ed1c8205 + the two dictated diffs is byte-identical to a53a6b97.** `git diff --stat ed1c8205..a53a6b97` touches exactly the two files (module 75 lines, tests 46 lines).
2. **Named tests.** `python3 -B -m unittest -v tests.test_benchmark_import_math tests.test_benchmark_import tests.test_suite` → `Ran 62 tests in 1.867s / OK (skipped=2)`. The two skips are `test_local_qwen3_mirrors_match_every_committed_prompt_token_id` and `test_render_prompts_asserts_two_mirror_equality_and_empty_think_tail` (transformers absent). `test_real_population_receipts_hashes_and_reference_self_check … ok` — executed, not skipped; it loads the pinned files, asserts (5001, 5000, 4999, 4040), the per-level 381/733/924/967/1035, receipts == SOURCE_RECEIPTS, the three set hashes, and the 4,040 × 3 self-consistency scores.
3. **One alias, no second body.** `grep -c "canonical_math_rational = canonical_reference_v1"` = 1; `def canonical_math_rational` absent (defs present: canonical_reference_v1, response_extension_v1, response_hazard_v1, eligible_records, score_response, validate_math_annotations).
4. **Fixture unchanged.** `git diff --stat ed1c8205..a53a6b97 -- tests/fixtures` is empty. Recomputed from the pinned bytes at head: fixture `source_files` == SOURCE_RECEIPTS == recomputed receipts; fixture `population` == recomputed stats; each set's stored `population` == stats and its item-id list hashes to the stored `set_hashes` entry (pilot 04c04ffe…, n64 bf941237…, n128 7ebb2d9d…). Pilot disjoint from n128; n64 is a per-level prefix of n128 (not a flat-list prefix; consistent with the per-level selection design, wording note only).

## Q2. Mutants MA-MH (all eight re-run, each a one-site edit in its own /tmp copy of a53a6b97, `python3 -B -m unittest tests.test_benchmark_import_math`)

| mutant | edit | result |
|---|---|---|
| MA | drop `.lower()` in hazard word match | KILLED (failures=4) |
| MB | re-add one-sided `("%" in box) != ("%" in expected_answer)` | KILLED (failures=20) |
| MC | eligibility also excludes on `response_hazard_v1` | KILLED (failures=2) |
| MD | eligibility falls back to `response_extension_v1` | KILLED (errors=2) |
| ME | validation re-parses via `canonical_reference_v1(...) or response_extension_v1(...)` | KILLED (failures=1) |
| MF | drop `"millions"` from the word list | KILLED (failures=1) |
| MG | second parser body `def canonical_math_rational(raw): return canonical_reference_v1(raw)` | KILLED (assertIs, failures=1) |
| MH | scorer reference side falls back to `response_extension_v1` | KILLED (failures=1) |

Each substitution site matched exactly once (asserted before running). 8/8 killed.

## Q3. Whole-lane sanity, `git diff 313efcca..a53a6b97` (8 files: benchmark_import_math.py, suite.py, scripts/gen_math_scored.py, three fixtures, two test modules)

- **Problem text in the tracked tree: NONE.** For all 5,001 test-split rows, the first and last 30 characters of both `problem` and `solution` were searched in the concatenated content of all eight lane files at a53a6b97: 0 hits. The hash-only fixture holds only `{item_id, source_sha256}` per item plus receipts, population counts and hashes; the string `problem` does not occur in it; the synthetic fixtures are invented rows. `gen_math_scored.py` refuses an `--out-dir` inside the repository.
- **Receipts authenticated from bytes: YES.** `authenticate_file` reads the payload, computes sha256, byte length, git blob sha1, line count, the git blob sha1 of the local pointer file bytes and of the licence bytes, compares all six to the pinned constants, and additionally requires the pointer bytes to equal the pointer regenerated from the payload's own sha256/size. Pointer and licence paths are required (ValueError when absent). The one-byte-mutation test passed in the named run; the real-population test asserts receipts == SOURCE_RECEIPTS from the pinned bytes.
- **Eligibility/selection reachable from the response scorer: NO.** `eligible_records` calls only `canonical_reference_v1`, `plain_comma_ambiguous`, `last_boxed`; `select_pilot`/`select_items` key on `source_sha256` under domain-separated SHA-256; `validate_math_annotations` uses `canonical_reference_v1` plus `str(Fraction(expected)) == expected`. `response_hazard_v1` and `response_extension_v1` are referenced only inside `score_response`. Mutants MC/MD/ME/MH and the patched-hook assertions in the real-population test enforce this.
- **GSM8K serialization unchanged: YES.** `configs/suite_manifests/gsm8k_scored_v6_qwen3.json` hashes to 1ad902f8ec64c737ee80f76b9b2dc6989b9e2d49ca267d5cb685b6f4c645c7f5 with round-trip equality under both the main (313efcca) and head trees; `to_dict` pops `source_files` when None, so legacy manifests serialize byte-identically. New field has a trailing default, so positional construction is unaffected.
- **Scorer behaviour at head (executed golden probes):** `44\%`↔`44`, `7.2\%`↔`36/5`, `5\text{ mi}`↔`5`, `20\%`↔`20`, `1{,}000`↔`1000` all correct; `5\text{ million dollars}`, `5\text{ millions}`, `5\text{ dozen eggs}`, `5\text{Million}`, `5\mathrm{i}` → incorrect with `denied_unit_word`; `5 i` → incorrect `imaginary_unit`. Known disclosed accepted pairs (dangerous direction, caught by the per-cell audit, not the mechanical scorer): `\frac12\%`↔`\frac12` and `5,120`↔`5120` score correct.
- **Merge cleanliness:** main has gained only PR #396 (tests/test_run_night.py, 46+/3−). `git merge-tree --write-tree origin/main a53a6b97` → clean tree 146830ca…, rc=0.

## Not executed / outside this lane

- A wider run of the 19 other test modules that reference the suite schema exceeded the 500 s command timeout and was stopped at 8 min 42 s; NOT EXECUTED to completion. Partial evidence: 146 tests had run with no failure or error marker before the stop. The three named modules are the gate and pass; post-merge CI covers the rest per the CI post-merge ruling.
- The two transformers-dependent tests remain skipped on this bench; real-tokenizer rendering and `</think>` survival through the decode path (Opus N5) stay in the runtime lane, before the first scored night, not before this merge.
- Hygiene, non-blocking: the pinned source directory also holds two scratch scripts (`canon.py`, `proto.py`, 15:01 today) that the importer never reads; consider moving them out so the directory holds only the five receipted files.

## Q4. MERGE

The closure landed verbatim, the named gate is green with the real population executed, all eight mutants die, no problem text is tracked, receipts are byte-derived, eligibility and selection are unreachable from the scorer, and GSM8K serialization is stable. No blocker found.
