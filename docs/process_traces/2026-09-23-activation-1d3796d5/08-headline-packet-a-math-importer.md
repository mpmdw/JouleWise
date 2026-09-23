# 08 — Headline packet A: the MATH importer (design seat, Opus 5.5, read-only)

Worktree read: `wt-1d3796d5-consult` at `313efcca`. Every count comes from the downloaded files unless it is marked
**planning figure**. The scratch prototype that produced the counts and hashes is `/tmp/mathsrc/{canon,proto}.py`. It
is not durable, and the implementation seat rebuilds it from this text.

## Answers first

1. **Source:** `openai/prm800k` @ `7ecc7947…`, both LFS (Git Large File Storage) files in `prm800k/math_splits/`.
   **Correction to the brief:** `test.jsonl` holds **500** items (MATH-500), not 5,000. The other 4,500 MATH test
   items are inside `train.jsonl`, tagged `unique_id: "test/…"`. MATH-500 has only 43 Level-1 items, so the importer
   reads both files.
2. **Population:** 5,000 test problems, minus 2 rows sharing one duplicated id, minus 954 whose reference answer is
   not a single rational number, minus 5 ambiguous plain-comma references. That leaves **4,040 eligible**, and the
   smallest level × subject cell holds 30.
3. **Selection:**
   - a disjoint 16-item pilot;
   - then per level, a list ordered by domain-separated sha256 and interleaved round-robin across the 7 subjects;
   - the test set is the first n items, so the 64-item set is a prefix of the 128-item set. No cell runs short at
     n = 128.
4. **Scorer:** stdlib only (D-009). It compares the last `\boxed{}` against the reference by exact `Fraction`
   equality after fixed normalization steps; it does no symbolic algebra. Scoring a wrong answer correct is ≈
   impossible. Scoring a correct answer wrong is possible and is measured by a blind audit.
5. **One user-message template for both arms** (Qwen3's documented math instruction). The arms differ only in
   `enable_thinking`.
6. A new sibling module, a producer, and one optional suite-schema field. It takes the **full gate**.
7. **Rulings (§7):** public commit of the problem text (Ed); the rational-only population; pilot-driven scorer
   additions; greedy decoding in thinking mode; who audits.

## 1. Source pin

| | `test.jsonl` | `train.jsonl` |
|---|---|---|
| Repo @ commit | `https://github.com/openai/prm800k` @ `7ecc794703b2877f63226f2477a49b34f9b25163` (head of `main`, 2023-06-01) | same |
| Path | `prm800k/math_splits/test.jsonl` | `prm800k/math_splits/train.jsonl` |
| sha256 (= LFS oid) | `35dc41080a3680858b27fa7e0533d2d547825316fc5dafe5d316f4ccc5a06132` | `90d96daeac3fe343ebb1e22ce93dd99690f75983e957f88de42f87cffe1e8076` |
| Bytes / lines | 446,564 / 500 | 10,896,985 / 12,000 |
| Content git-blob sha1 | `2376b9a194b46c0790e197c91b7249e5f88ac09b` | `3a9d774ba092769cce4b93133bf3c97f2b8ea20c` |
| LFS-pointer blob sha1 (in the commit tree) | `8837efbfa7fb7ad8a9a66b280a8cd86be3cd70bd` | `fabbf3962afc8d64618406adde7f012bf0ba3c20` |
| Fetch | `https://media.githubusercontent.com/media/openai/prm800k/<commit>/prm800k/math_splits/<file>` | same |
| License | MIT; `LICENSE` blob sha1 `4ccc7f8dba5cb9f5dc77f14778602ef4c0a585b2` (1,062 B; the GitHub license API reports SPDX `MIT` with the same sha) | same |

**Why the pointer matters.** Under LFS, the commit tree stores a 131/133-byte pointer, not the data. The loader
rebuilds the pointer from the content (`"version https://git-lfs.github.com/spec/v1\noid sha256:<sha>\nsize <bytes>\n"`)
and checks its blob sha1. I confirmed that the rebuilt pointers are byte-identical to the fetched pointers and match
the tree entries. This chains the data bytes to the commit.

The loader checks six receipts per file: sha256, bytes, content blob sha1, rebuilt-pointer blob sha1, line count, and
that every line parses.

**Fields** (all 12,500 rows): `problem, solution, answer, subject, level` (int 1–5), and `unique_id` (the original
MATH path, e.g. `test/precalculus/807.json`). `answer` equals the last `\boxed{}` content of `solution` for 4,999/4,999
non-duplicate test rows.

**Counts** (non-duplicate test rows; the last column is the MATH-500 count):

| Level | Alg | C&P | Geo | IntAlg | NT | PreAlg | PreCalc | Total | MATH-500 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 135 | 39 | 38 | 52 | 30 | 86 | 57 | 437 | 43 |
| 2 | 201 | 101 | 82 | 128 | 92 | 177 | 113 | 894 | 90 |
| 3 | 261 | 100 | 102 | 195 | 122 | 224 | 126 | 1,130 | 105 |
| 4 | 283 | 111 | 125 | 248 | 142 | 191 | 114 | 1,214 | 128 |
| 5 | 307 | 123 | 132 | 280 | 154 | 193 | 135 | 1,324 | 134 |

**Defect:** `test/precalculus/24307.json` occurs twice in `train.jsonl`, at 1-based lines 2337 and 11795. Both rows
say `Geometry`, level 5, answer 315, with different solutions: MATH holds this problem in both train/geometry and
test/precalculus, and PRM800K merged the ids. Rule: **exclude any `unique_id` that occurs more than once.**

**Why not the alternatives:**
- **Original Hendrycks tarball:** HTTP 403 from here, with and without a browser User-Agent, and no commit identity.
- **`hendrycks/competition_math` (Hugging Face):** `disabled: true`, following Art of Problem Solving's (AoPS) DMCA
  takedown of 2025-01-02 ([notice](https://huggingface.co/datasets/huggingface-legal/takedown-notices/blob/6be1fd145590de35cc6c3788a146dcf6a806382a/2025/2025-01-02-AoPS.md)).
- **EleutherAI / lighteval / nlile mirrors:** Parquet, which needs pyarrow and so breaks the stdlib loader (D-009).
- **HuggingFaceH4/MATH-500:** 500 items only.
- **PRM800K:** commit-pinned, MIT, stdlib-readable JSONL, integer levels, and reference answers that are
  pre-extracted and cross-checked. Same publisher as the GSM8K pin.

## 2. Selection

**Record:**
- `source_file` and `line_index`;
- `source_item_id = "math_" + unique_id[:-5].replace("/","_")`;
- `source_sha256 = sha256(canonical_json({problem, answer, level, subject, unique_id}))`. Level and subject are
  hashed, so relabelling an item changes its identity.

**Eligibility** depends on the reference answer only and is fixed before any output. It is applied in this order,
with counts reported per level:
1. duplicate id → excluded (2 rows);
2. `canonical_math_rational(answer)` is None (§3) → excluded (954);
3. plain comma → excluded (5: `58,500`, `61,328`, `\$115,000`, `15,600`, `70,110`; the last is a list of two
   angles). Test: remove whitespace and `\,` `\;` `\:`, delete `,\!` and `{,}`, and exclude the item if any comma
   remains.

**Retention falls with level:**

| Level | Eligible / non-duplicate | Retention |
|---|---|---|
| L1 | 381/437 | 0.872 |
| L2 | 733/894 | 0.820 |
| L3 | 924/1,130 | 0.818 |
| L4 | 967/1,214 | 0.797 |
| L5 | 1,035/1,324 | 0.782 |

The integer-answer share also falls, from 0.751 at L1 to 0.543 at L5. Both are disclosed beside every result.

| Eligible | Alg | C&P | Geo | IntAlg | NT | PreAlg | PreCalc |
|---|---|---|---|---|---|---|---|
| L1 | 128 | 38 | 35 | 32 | 30 | 83 | 35 |
| L2 | 178 | 100 | 65 | 81 | 83 | 171 | 55 |
| L3 | 229 | 99 | 75 | 137 | 109 | 211 | 64 |
| L4 | 250 | 109 | 82 | 174 | 130 | 172 | 50 |
| L5 | 248 | 121 | 88 | 199 | 149 | 162 | 68 |

**Keys** (GSM8K form; a duplicate key refuses):
- `pilot_key = sha256("joulewise.benchmark_import.math.pilot.v1\0" + source_sha256)`;
- `test_key = sha256("joulewise.benchmark_import.math.selection.v1\0" + source_sha256)`.

**Pilot, 16 items:** order each level by `pilot_key`, then take round-robin over L5, L4, L3, L2, L1 until 16 are
taken. That is L5 = 4 and the other levels 3 each. Level 5 gets the extra item because the longest traces set the
cap.

**Test list per level** (pilot removed first):
1. Put each subject in a queue sorted by `test_key`.
2. For round r = 0, 1, …, take the r-th item of every subject queue that still has one. Sort those items by
   `test_key` and append them.
3. The test set is the first n items.

At n = 64 each subject gets 9 or 10 items. **Short cell:** a subject that runs out drops from later rounds, and the
others fill its places. The per-(level, subject) counts go into the manifest. The importer refuses a level with fewer
than n eligible items. No subject runs short at n ≤ 128.

**Reference hashes** (`canonical_json_sha256` of the id list, levels ascending). The implementation must reproduce
these or explain the difference:
- pilot: `62588aa3c58e9c7b68c1900a811b5e3336d5acaf798280cdc75b05657240b99c`;
- n = 64: `a4ac44addbee60dac8a75aaad6d3b6a6aa0eceb8ab12de983d8ce20c79545c88`;
- n = 128: `115ac17bf73bf63fef69e5023d8c50933fb446376eafe2849749e3ed092cb98e`.

Checks: the 64-set is inside the 128-set, and the pilot is disjoint from both. MATH-500 members at n = 64 per level:
3/8/6/9/4. The importer records an `in_math500` flag per item; it is descriptive only.

**Why equal subject shares:** they remove subject mix as a difference between levels. For example, Algebra is 31% of
the Level-1 population. The paper states that its estimates describe a subject-balanced population.

**n:** the importer emits n ∈ {64, 128}. The registration fixes n from pilot runtime and token counts, never from
accuracy, before any test item runs (D-062(a)). The accuracy 95% half-width at p = 0.5 is ±0.123 at n = 64 and
±0.087 at n = 128.

## 3. Scorer `math_levels_v1/score_v1`

**Answer section.**
- Thinking-on: the text after the **last** `</think>`. If there is none, the outcome is `truncated` when the response
  was capped and `malformed` otherwise.
- Thinking-off: the whole response.

`<think>` (151667) and `</think>` (151668) are `special: false` in the local 8B `tokenizer.json`, so they survive
decoding. A test must pin this through the `mlx_runtime` decode path.

**Extraction:** the last `\boxed{` or `\fbox{`, read to its matching brace by counting depth. No box or unbalanced
braces → `malformed`.

**`canonical_math_rational(s)`**, applied identically to reference and response:
1. `\dfrac`/`\tfrac` → `\frac`.
2. Remove `\$`, then `$`.
3. Remove `\!` `\,` `\;` `\:` `\ ` `~` and all whitespace.
4. Strip one trailing `^\circ`, `^{\circ}`, `\%`, `%` or `\degree`.
5. Strip trailing `\text{}`, `\mbox{}`, `\textrm{}` or `\mathrm{}` groups whose content has no digit and no brace.
6. `{,}` → `,`.
7. Strip a leading single-letter `x=`.
8. Match, in order:
   - `[+-]?\d+`;
   - `[+-]?(\d+\.\d*|\.\d+)`;
   - `[+-]?\d{1,3}(,\d{3})+` (commas dropped);
   - `a/b`;
   - `[+-]?\frac` with two arguments, each `{[+-]?\d+}` or a single digit.

   Anything else returns None, and so does a zero denominator.
9. Return `str(Fraction)` in lowest terms.

**Outcomes** (the four GSM8K classes, plus a `parse_status` field):
- runtime `runtime_failed`/`malformed` → `malformed`.
- runtime `capped` → **`truncated` even if a box parses.** This agrees with packet C (its ruling 5) and departs from
  GSM8K. The parsed value is recorded for the audit.
- no box → `malformed`.
- box that does not canonicalize → `incorrect` (`parse_status: boxed_noncanonical`). Every reference is rational,
  so a non-rational box is wrong in value, not in format.
- equal → `correct`; unequal → `incorrect`.

Truncated and malformed count as incorrect in the denominator (D-047.6, AP-5).

**Why not sympy:** sympy-based graders (PRM800K's, Minerva-style) break D-009 and let a library version decide
correctness. With rational references, exact equality is complete on the reference side: canonical(`answer`) equals
canonical(last box of `solution`) for **4,040/4,040** eligible items.

**Error risk:**
- *False positives* (wrong scored correct) need an accidental match, e.g. a list `5,120` against a reference of 5120.
  Expected ≈ 0.
- *False negatives* (right scored wrong) come from equivalent forms the parser does not accept: mixed numbers,
  scientific notation, `\sqrt{4}`, repeating decimals, `\left(…\right)`.

The error that matters is **level-correlated**, because answer forms shift with level (above).

Measurement:
- **Pilot:** all 64 pilot responses (16 × 2 models × 2 arms) are audited.
- **Test:** in each (arm, model, level) cell, audit all `boxed_noncanonical` and `malformed` rows, plus 8 `incorrect`
  and 4 `correct` rows. The samples are the lowest `sha256("joulewise.math.audit.v1\0" + item_id)`. The auditor is
  told neither the model nor the level.
- Report false-negative and false-positive rates per level with Wilson 95% intervals, and an audit-corrected accuracy
  as a **sensitivity row**. The mechanical scorer stays primary.
- R_L is the ratio of J/correct for the 8B over the 1.7B at level L. A level where the correction moves R_L's
  interval across 1 is labelled *scorer-sensitive*.

**Golden pairs** (response → reference ⇒ outcome):
- `\dfrac{3}{4}`, `0.75`, `3/4`, `\frac{6}{8}`, `\boxed{\frac{3}{4}}` → `\frac34` ⇒ correct.
- `-\frac12` → `-\frac{1}{2}`; `x=5` → `5`; `10,080` → `10,\!080`; `90^\circ` → `90`; `5\text{ cm}` → `5`; `\$4` → `4`;
  `.5` → `\frac12` ⇒ correct.
- `\sqrt{2}` → `\frac32`; `\frac{1}{0}` → `0`; `1,2` → `12` ⇒ incorrect (noncanonical).
- `2\frac12` → `\frac52` ⇒ incorrect. This is a known false negative, pinned as such.
- `0.333` → `\frac13`; two boxes with the last one wrong ⇒ incorrect.
- A box only inside `<think>` ⇒ malformed.
- Capped, with or without a parseable box ⇒ truncated.

A test asserts the round-trip canonical(`answer`) = canonical(last box of `solution`) over the authenticated files.
It skips when the files are absent.

## 4. Prompt template (both arms)

```
PROMPT_TEMPLATE = "{problem}\n\nPlease reason step by step, and put your final answer within \\boxed{}."
PROMPT_TEMPLATE_SHA256 = "1a0796c08f1175730c3dde6a9e7d38312904f985853cb2ad46d594a90dd2319d"
PROMPT_TEMPLATE_ID = "math_levels_v1/qwen3_chat_boxed_v1"
```

The instruction is verbatim from the Qwen3-8B model card's math best practice. Fill it with
`.replace("{problem}", problem)`. `.format` would break on the literal `{}`. A test asserts exactly one placeholder.

Render `[{"role":"user","content":prompt}]` with `add_generation_prompt=True` under the pinned chat template
(`87a2728c…`) and tokenizer.json (`aeb13307…`):
- **Off:** `enable_thinking=False`. The tail must be `EMPTY_THINK_PREFIX`; reuse the GSM8K assertions.
- **On:** `enable_thinking=True`. The tail must be `"<|im_start|>assistant\n"`, and the text must contain no
  `<think>`.

Both arms use the same items and the same user text, so the flag is the only difference.

Rejected alternatives:
- GSM8K's "Reason briefly": it would confound tokens per attempt.
- A "reduced fraction or decimal" hint: it tells the model the answer is a single number.

## 5. Quarantine text

This aligns with packet C (`10-…-ap5-amendment.md` §6). The AP-5M and D-166-addendum ids are filled from whichever
ruling lands. AP-5M is packet C's proposed MATH sibling of AP-5.

- `difficulty = {"axis":"math_author_level","value":L,"scale":"ordinal","label":"Level L","source":"hendrycks_math_2021","quarantine_note":DIFFICULTY_QUARANTINE}`.
  The current `ItemDifficulty` schema accepts this.
- `DIFFICULTY_QUARANTINE = "D-166 add. 2026-09-23/AP-5M: MATH author-assigned level (Hendrycks et al. 2021), fixed before any model output and never computed from a tested model; it stratifies comparisons and licenses no 'difficulty causes energy' or intelligence-per-joule claim"`
- `CONTAMINATION_NOTE = "D-166/AP-5M: MATH (2021) and PRM800K (2023) predate Qwen3 and are widely redistributed; pre-training contamination is UNMITIGABLE; accuracy is a property of this pinned, subject-balanced, rational-answer subset, never a capability claim"`
- `CORRECTNESS_QUARANTINE`: the GSM8K text plus "; capped counts as truncated-incorrect (AP-5M)".
- A new `ELIGIBILITY_NOTE` in `source_manifest` carries the exclusion counts and the per-level retention.

## 6. Files, tests, gate

**New:**
- **`joulewise/benchmark_import_math.py`.** A sibling module, so GSM8K's pinned module and its hash tests stay
  untouched. It reuses `_canonical_json*`, `_tokenizer_manifest` and `_reviewed_qwen3_pins`, and provides:
  - `load_math_test(test, train)` returning `AuthenticatedMATHRecords` (two receipts);
  - `canonical_math_rational`, `extract_answer_section`, `last_boxed`;
  - `eligible_records`, `select_pilot`, `select_items(n)`;
  - `render_prompts(…, enable_thinking)` with a lazy transformers import;
  - `build_math_manifest` and `build_math_annotations` (the sidecar adds `unique_id`, `source_file`, `line_index`,
    `level`, `subject`, `in_math500`);
  - `validate_math_annotations`, which recovers `problem` between `<|im_start|>user\n` and the template suffix;
  - `score_math_outcome_table`, with an exact-set gate and outcome counts per level.
- **`scripts/gen_math_scored.py`** with `--test-jsonl --train-jsonl --tokenizer-dir… --arm {off,on} --set {pilot,test} --n {64,128}`.
- **`tests/test_benchmark_import_math.py`:**
  - the golden pairs;
  - per-file receipt refusals (sha, bytes, blob, pointer, lines);
  - duplicate-id exclusion;
  - eligibility on a synthetic fixture;
  - pilot/test disjointness and the prefix property;
  - selection independent of input order;
  - the short-cell fill rule and the refusal of a short level;
  - the template hash and single placeholder;
  - both render tails with two-mirror equality;
  - think tokens surviving `mlx_runtime` decoding;
  - capped means truncated;
  - exact-set, order and foreign-item refusals;
  - producer determinism through a mocked render;
  - with the real files (skip otherwise): 4,040, the per-level table and the three reference hashes.
- **`configs/suite_manifests/math_levels_v1_qwen3_{nothink,think}_{pilot,n<N>}.json`** plus annotations, generated on
  the Mac after the n ruling. Their form depends on R1.

**Changed:**
- `joulewise/suite.py` `BenchmarkImport`: an optional `source_files` list with entries
  `{path, sha256, bytes, line_count, git_blob_sha1, lfs_pointer_blob_sha1|null}`. The legacy single-file fields carry
  `test.jsonl`, so GSM8K manifests stay valid. Add a regression in `tests/test_suite.py`.
- `scripts/test_timings.json`: an entry for the new tests.
- The fixed claim-bearing gate list (synthesis item 5) gains the new module.

**Regressions (green, unchanged):** `tests/test_benchmark_import.py` (26 tests, including `PINNED_MANIFEST_SHA256`
and the mirror token-id test), `tests/test_suite.py`, `tests/test_analysis_inputs.py`, and the gsm8k cells of
`tests/test_floor_extraction.py`. Run these modules plus the new one, not the full suite.

**Gate:** the full shape (an Opus lens, Sol refuters with distinct contract and execution lenses, and a cold Fable
instance). The module produces the correctness denominator, which makes it claim-bearing. Executed evidence required:
- the six receipts per file on the real files;
- the three reference hashes reproduced;
- the golden pairs;
- one counterexample per refusal;
- the production call site: packet B's scored-campaign night kind consumes `score_math_outcome_table`.

## 7. Open rulings

- **R1 (Ed).** The GSM8K precedent commits `prompt_text` to this **public** repo (`gh repo view`: PUBLIC). The MATH
  problems are the subject of AoPS's 2025 takedown. Options:
  - (a) commit the full manifests under PRM800K's MIT license;
  - (b) commit only hash-bearing manifests (ids, `source_sha256`, subset hashes, and prompt-token *sha256s*,
    because token ids decode to the text). Full manifests would be generated at the desk into an untracked custody
    path, and tests would skip without the source.

  **Recommend (b).** It needs a small schema allowance, ruled together with R1.
- **R2 (magistrate).** The rational-only population (−954 items, with retention falling as level rises) versus a
  stdlib radical/π numeric evaluator. Recommend rational-only: the scorer stays checkable and its error measurable.
  The narrowed population is disclosed.
- **R3 (magistrate + cold gate).** May pilot-audit false negatives add normalization steps before any test item
  runs? Recommend **yes, additions only**, with the scorer id bumped and a golden pair added per step. This extends
  synthesis item 3's list of what the pilot may set.
- **R4 (magistrate, registration).** The Qwen3 card says "DO NOT use greedy decoding" in thinking mode (endless
  repetitions). Recommend keeping greedy, which gives deterministic tokens and energy-only repeats. The pilot measures
  the repetition and cap-hit rate before the cap is frozen, and that rate is registered as a reported factor.
- **R5 (magistrate).** The auditor. Recommend a blind model seat for all audited rows, plus Ed hand-labelling 20 rows
  as a check of the seat.
- **R6 (with packet C).** Capped means truncated (adopted here); the cap-bound threshold.
