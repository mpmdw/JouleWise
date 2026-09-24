VERDICT: PROCEED-AFTER-DICTATED-CLOSURES

# Cold Fable 5.1 ruling: MATH importer, branch feat/2026-09-23-math-importer at ed1c8205 (base 313efcca)

Session: detached worktree /Users/edr/code/wt-1d3796d5-fablemath, foreground only, no repository file edited (`git status --short` empty at the end). Every probe below was executed this session unless marked NOT EXECUTED. The full closure I dictate was prototyped in a /tmp copy of the tree and is saved verbatim beside this file as
`40-fable-ruling-math-closure-module.diff` (joulewise/benchmark_import_math.py, 111 lines) and
`40-fable-ruling-math-closure-tests.diff` (tests/test_benchmark_import_math.py, 81 lines).
Those two diffs ARE the dictated closure; the prose below explains them.

## Q1. Delta findings F1, F2, F3

### F1 CONFIRMED (blocker)
Executed: loaded the pinned files through `load_math_test` (all six receipts per file matched), took the 4,040 eligible rows, and scored `\boxed{<source answer>}` and `\boxed{<last box of the solution>}` against each row's production `expected_answer`.

| probe | result |
|---|---|
| source answer self-score | 4,025 / 4,040 correct, 15 incorrect |
| solution last-box self-score | 4,025 / 4,040 correct, the same 15 |
| eligible references containing `%` | 15 (exactly the 15 failures) |
| failures inside the registered sets | 3 in n64 and n128 (`test/prealgebra/1426`, `768`, `1440`); 0 in the pilot |

Mechanism: `score_response` line 306 compares `"%" in box` against `"%" in expected_answer`, but `expected_answer` is the canonical Fraction string (`44`, `36/5`), which never contains `%`. So the rule as coded is "any percent sign in the response is incorrect". Reference `44\%` with the model answering `44\%` scores incorrect.

Design fact the fix must respect: the population has 78 eligible problems whose text mentions percent; only 15 of their references carry `\%`, 63 do not, and 12 of those 63 ask "what percent" outright (e.g. `test/prealgebra/1599` reference `20`). A one-sided rule in EITHER direction therefore penalises a correct answer: `44` against `44\%` (F1 direction) and `20\%` against `20` (the 12 "what percent" items). The Hendrycks MATH grader strips `\%` symmetrically; packet A §3 step 4 already specified exactly that. Y5's percent sentence was a magistrate dictation that contradicted the design and was not checked against the data.

### F2 CONFIRMED (should-fix, same defect class as round one)
`validate_math_annotations` line 550 checks `canonical_math_rational(answer) != expected`, the mutable response parser. Eligibility (`eligible_records`) uses `canonical_reference_v1`. `score_response` line 295 also re-parses `expected_answer` with the response parser. Three call sites, two parsers with byte-identical bodies today: the delta re-audit's mutant (rejoin eligibility to the response parser) survived precisely because the bodies are identical, so the "separation" is a naming convention, not a mechanism.

### F3 CONFIRMED (should-fix), and wider than reported
Executed against the candidate, reference `5`:

| response | candidate outcome | should be |
|---|---|---|
| `5\text{Million}`, `5\text{ MILLION}` | incorrect | incorrect (case-insensitivity works, but no test pins it: removing `re.IGNORECASE` survives the named tests, delta V4) |
| `5\text{ million dollars}` | **correct** | incorrect |
| `5\text{ millions}`, `5 \text{thousands}` | **correct** | incorrect |
| `5\text{ dozen eggs}` | **correct** | incorrect |
| `5\text{ mi}` | correct | correct (unit "mi", not the imaginary unit) |
| `5\mathrm{i}`, `5\text{i}`, `5 i` | incorrect | incorrect |

The denial regex requires the magnitude word to be the ENTIRE `\text{}` group, so any compound or plural unit text bypasses it. Also executed: `canonical_math_rational("5i")` and `("5\,i")` are both `None`, so the `i\s*$` branch never changes an outcome (a raw box ending in `i` never canonicalises); only the `\mathrm{i}` / `\text{i}` form needs the denial. Harmless, kept as belt.

### Dictated closure (exact; prototyped and executed)

**C1. One parser.** Delete the duplicated body of `canonical_math_rational`. Replace it with the alias line
`canonical_math_rational = canonical_reference_v1  # packet A name; one parser, no second body`.
Test: `self.assertIs(math.canonical_math_rational, math.canonical_reference_v1)`.

**C2. Percent rule = packet A step 4, symmetric, no rescale.** Remove the `("%" in box) != ("%" in expected_answer)` clause entirely. `canonical_reference_v1` already strips one trailing `\%`/`%` on both sides. Golden pairs added, all `correct`: (`44\%`, `44`), (`44`, `44\%`), (`7.2\%`, `36/5`), (`5\text{ mi}`, `5`). Documented known accepted pair (dangerous direction, disclosed, same class as `5,120`): (`\frac12\%`, `\frac12`) is `correct`; it is caught by packet A's per-cell audit, not by the mechanical scorer. Remove the two percent pairs from the `incorrect` list.

**C3. Response-only hazards as a closed, named list.**
```python
_STRIPPED_GROUP = re.compile(r"\\(?:text|mbox|textrm|mathrm)\{([^{}0-9]*)\}")
_DENIED_UNIT_WORDS = frozenset({"hundred", "hundreds", "thousand", "thousands", "million", "millions", "billion", "billions", "trillion", "trillions", "dozen", "dozens", "i"})

def response_hazard_v1(box: str) -> str | None:
    """Closed list of response-only denials; never applied to references or eligibility."""
    for group in _STRIPPED_GROUP.findall(box):
        if any(word.lower() in _DENIED_UNIT_WORDS for word in re.findall(r"[A-Za-z]+", group)):
            return "denied_unit_word"
    if re.search(r"i\s*$", box):
        return "imaginary_unit"
    return None
```
Word-level, case-insensitive, plural forms named, applies to every stripped unit group (the same groups the canonicaliser removes). `score_response` sets `hazard = response_hazard_v1(box) if box is not None else None`, `unsafe_response = hazard is not None`, and returns the hazard under a new key `response_hazard` for the audit. Golden pairs added to `incorrect`: `5\text{ million dollars}`, `5\text{ millions}`, `5 \text{thousands}`, `5\text{ dozen eggs}`, `5\text{Million}`, `5\text{ MILLION}`, `5\mathrm{Dozen}`, `5\text{I}`, `5 i`, each against `5`.

**C4. Additions-only hook (M5).**
```python
def response_extension_v1(box: str) -> str | None:
    """Additions-only hook (M5): tried only when canonical_reference_v1 returns None. v1 accepts nothing."""
    return None
```
`score_response`: `parsed = canonical_reference_v1(box)`; if `None`, `parsed = response_extension_v1(box)`. The reference side: `reference = canonical_reference_v1(expected_answer)`, raise `"expected answer is not rational"` if `None`. Eligibility and annotation validation never call the hook or the hazard list.

**C5. Annotation validation decoupled.** Line 550 becomes
`canonical_reference_v1(answer) != expected or str(Fraction(expected)) != expected`
(the frozen canonicaliser, and the stored expected answer must itself be in canonical lowest-terms form).

**C6. Test shapes (all in the tests diff):**
- Synthetic decoupling test: patch `response_extension_v1` to `return_value="1"` (accept everything) AND `response_hazard_v1` to `return_value="deny_everything"`; assert `eligible_records` stats and id order unchanged, and `score_response(r"\boxed{\sqrt{2}}", "1")` is `incorrect`. With only the extension patched: that call is `correct`, and `score_response(r"\boxed{1}", r"\sqrt{2}")` still raises `not rational` (the reference side ignores the hook). Then every synthetic eligible row self-scores `correct`.
- Native suite test: under the extension patch, `validate_math_annotations` accepts the unchanged sidecar, and a sidecar whose `source_answer` is `\sqrt{2}` raises `answer mismatch` (not `source hash mismatch`).
- Real-file test (bench-only, currently NOT skipped on the bench; the two skips in the 62 are the transformers tests in test_benchmark_import): for every one of the 4,040 eligible rows, `\boxed{answer}`, `\boxed{last box of solution}`, and thinking-on `<think>x</think>\boxed{answer}` all score `correct`; then `assertEqual(sum(correct), 4040)`; then the extension+hazard patch leaves the count 4,040, `stats`, and the three set hashes unchanged.

### Executed evidence for the closure (prototype tree /tmp/fablemath/repo = worktree + the two diffs)
```
python3 -B -m unittest tests.test_benchmark_import_math tests.test_benchmark_import tests.test_suite
Ran 62 tests in 1.039s / OK (skipped=2)
self_score answer 4040 / 4040   last-box 4040 / 4040
set hashes: pilot 04c04ffec881aed3… n64 bf94123715a95328… n128 7ebb2d9defaf4d97…  (unchanged; fixture needs no regeneration)
```
Mutants run against the prototype's `tests.test_benchmark_import_math` (each a one-line edit in a /tmp copy):

| mutant | result |
|---|---|
| MA drop `.lower()` in the hazard word match | killed (4 failures) |
| MB re-add the one-sided percent clause | killed (20 failures, 1 error) |
| MC eligibility also excludes on `response_hazard_v1` | killed |
| MD eligibility falls back to `response_extension_v1` | killed |
| ME validation re-parses via `canonical_reference_v1(...) or response_extension_v1(...)` | killed |
| MF drop the plural `"millions"` from the word list | killed |
| MG restore a second parser body under the name `canonical_math_rational` | killed (`assertIs`) |
| MH scorer reference side falls back to `response_extension_v1` | killed |

## Q2. Structural design

Yes, and it is what C1 to C5 install. The scorer is now: outcome `correct` iff `response_hazard_v1(box) is None` and (`canonical_reference_v1(box)` or, only when that is `None`, `response_extension_v1(box)`) equals `canonical_reference_v1(expected_answer)`. Properties, each enforced by a test above:
1. There is one value parser. Nothing can drift between "reference" and "response" parsing because there is no second body (MG).
2. Every future M5 addition goes into `response_extension_v1` (a `v2` with a scorer-id bump) and is consulted only after the frozen parser returns `None`. It can turn an `incorrect` into `correct`, never the reverse, and it can never touch eligibility, selection, or the sidecar (MD, ME, MH, and the hash-unchanged assertion).
3. Every denial goes into `response_hazard_v1`, a closed list applied to the response box only (MC).
4. Mandatory self-consistency invariant: every eligible reference, in both its answer-field and solution-box forms, scores `correct` against itself, 4,040/4,040 on the bench and on the synthetic fixture in CI. No hazard or rule that hurts a reference form can land.
Keep `SCORER_ID = math_levels_v1/score_v1`: no response has ever been scored under the ed1c8205 variant, and the closure returns the percent semantics to packet A's published definition; the hazard list is a response-only refinement of packet A step 5.

## Q3. Are the Y5 denials sound for the rational-only population?

Executed over all 5,001 rows: 0 answers contain a magnitude word; 31 answers end in `i` (complex numbers such as `6 - 5i`) and none of them is eligible (the frozen parser rejects them). Over the 4,040 eligible references the stripped unit texts are ordinary units (`degrees` 4, `dollars` 4, `cm`, `mph`, `square units`, …) and never a denied word. So:
- **Magnitude words: KEEP, generalised (C3).** They cannot fire on any reference form (invariant test proves it) and they only ever convert a wrong-in-value response (`5\text{ million}` when the reference is `5`) from a false positive into `incorrect`. The candidate's whole-group regex was too narrow (F3 table); the word-level list closes the plural and compound forms.
- **Imaginary unit: KEEP.** `\mathrm{i}` / `\text{i}` is the only form that would otherwise be stripped as a unit and score correct; the trailing-`i` branch is redundant (never canonicalises) but harmless.
- **Percent: DROP the one-sided rule (C2).** It is wrong in both directions on this population (15 references carry `\%`, 12 "what percent" references do not), and it contradicts packet A step 4 and the reference grader.

## Q4. Anything else wrong in 313efcca..ed1c8205 for a claim-bearing importer

Checked by execution or read; nothing else blocking.
- Receipts: all six per file match the pinned constants from real bytes; the licence and both LFS pointers are required (Y1 closed).
- `ELIGIBILITY_NOTE` numbers (2 / 954 / 5 excluded; 381/437, 733/894, 924/1130, 967/1214, 1035/1324) match the recomputed stats exactly; the tracked hash-only fixture's population block matches too; the fixture holds no problem text.
- Brace-less box: `last_boxed(r"\boxed 12")` returns `1` (LaTeX-faithful: `\boxed 12` boxes only the `1`). Safe direction only; models emit `\boxed{...}`. Note for the audit, no change dictated.
- `score_response` returns `truncated` for capped runs before any box inspection, so a capped thinking-on response with no `</think>` is `truncated`, not `malformed`, as M2 requires.
- suite.py: `source_files` optional, serialised only when present, `lfs_pointer_blob_sha1` key required, first entry cross-checked against the legacy fields (Y9). GSM8K serialisation unaffected (Opus lens, not re-executed here: NOT EXECUTED).
- Still outside this lane and still open (Opus N5): `</think>` survival through the MLX decode path and rendering with the real tokenizer; the two skipped tests are the transformers-dependent ones. Must be closed in the runtime lane before the first scored night, not before this merge.

## Q5. PROCEED-AFTER-DICTATED-CLOSURES

The closure is not a description, it is two executed diffs. Mechanical check for the final pass, in order:
1. `git apply --check` both `40-fable-ruling-math-closure-*.diff` on ed1c8205 (paths: strip the absolute prefixes), then apply; no other source change.
2. `python3 -B -m unittest tests.test_benchmark_import_math tests.test_benchmark_import tests.test_suite` → `Ran 62 tests … OK (skipped=2)` on the bench, with `test_real_population_receipts_hashes_and_reference_self_check` executed (not skipped) and the 4,040 self-consistency assertions inside it passing.
3. `grep -c "canonical_math_rational = canonical_reference_v1" joulewise/benchmark_import_math.py` = 1 and no `def canonical_math_rational` remains.
4. Fixture unchanged (set hashes and population unchanged; no regeneration needed).
Optional but cheap (≈1 min): rerun mutants MA to MH from the table above; all eight must fail the named module.
If any step deviates from verbatim, that is ANOTHER-ROUND, not a local patch.
