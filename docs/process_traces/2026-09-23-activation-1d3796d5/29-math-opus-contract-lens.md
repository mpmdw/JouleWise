**Verdict: MERGEABLE.** I found no blockers. There are four should-fix items; the first must be cured before any scorer change that the pilot is allowed to trigger (M5).

**Reviewed:** `47ea644d` against `313efcca` in `/Users/edr/code/wt-1d3796d5-math`. Everything I ran was read-only; scratch files are in `/tmp/mathlens/`.

## (1) Clauses C1–C8 (all in `joulewise/benchmark_import_math.py` unless noted)
- **C1, met with a caveat (see S3):** the loader checks six receipts per file at :55-80, a mismatch refuses and names the failing receipt at :64-66, and the pointer and licence checks are at :67-70.
- **C2, met:** duplicate exclusion, the rational test, the plain-comma test, and a refusal when the answer field and the last box disagree (:161-187).
- **C3, met:** domain-separated keys (:30-31, :190), an 80-item pilot (:202-209), and subject-interleaved test lists (:212-230).
- **C4, met:** the scorer is at :233-252, and capped attempts become truncated with the parsed value kept (:244, :240).
- **C5, met:** one prompt template with its sha256, used by both thinking arms (:34-36, :287-324).
- **C6, met:** the quarantine constants carry PENDING (:37-39), except for the wording flagged in S2.
- **C7, met:** `scripts/gen_math_scored.py:42-43` refuses an output directory inside the repo, and the only tracked output is the hash-only fixture.
- **C8, met:** the tests are at `tests/test_benchmark_import_math.py:44-202`. I re-ran the three named modules: 61 tests, OK, 2 skipped. The real-file test ran here.

## (2) Independent recount (`/tmp/mathlens/recompute.py`, my own parser written from packet A's text)
- **Six receipts:** all match for both files. The rebuilt LFS pointers are byte-identical to `ptr_*.txt`, and the licence blob is `4ccc7f8d…`.
- **Rows:** 5,001 rows, 5,000 distinct ids and 4,999 singletons. The duplicated id is `test/precalculus/24307.json`.
- **Exclusions:** 2 duplicate rows, 954 non-rational references and 5 plain-comma references (the same 5 strings packet A lists).
- **Eligible:** 4,040, with self-check mismatches = []. Per level: 381/437, 733/894, 924/1,130, 967/1,214, 1,035/1,324. All 35 (level, subject) cells match the seat's table exactly.
- **Set hashes:** my own implementation reproduces the pilot `d6a16718…`, n=64 `face9ab2…` and n=128 `1caaf115…`.
- **Packet A's hashes explained:** with a 16-item pilot, my code reproduces packet A's three hashes exactly (`62588aa3…`, `a4ac44ad…`, `115ac17b…`). The seat's explanation (the 80-item pilot from M4 is the only difference) is therefore proven.
- **Comma references:** all 45 eligible references with commas are true thousands groupings, not lists. No `\pi` survives into the eligible set.

## (3) Scorer, 66 adversarial pairs plus 8 extraction cases (`/tmp/mathlens/adv.py`)
**Wrong answers scored correct (the dangerous direction).** All five follow packet A's own rules:
- `5,120` against 5120 (a list read as a number; packet A already acknowledges this one).
- `5\text{ million}` against 5: step 5 strips any trailing `\text{}` without digits, including words that change magnitude.
- `5\mathrm{i}` against 5: an imaginary answer scored as the real number 5.
- `\frac12\%` against 1/2: a trailing percent sign is stripped with no rescaling.
- `\frac12\text{ and }` against 1/2 (harmless).

**Extraction nit:** in `\boxed{3} … \boxed 5` (last box written without braces), the earlier box `3` is scored.

**Correctly handled:**
- Negative and doubly signed fractions: `\dfrac{-3}{4}`, `-\tfrac`, `\frac{-3}{-4}`, `-\frac{-3}{4}`.
- `5.`, `-.5`, `x=5`, `\$5.00`, `90^\circ`, thousands in the forms `1{,}000` and `10,\!080`.
- `\pi`, `3\pi` and `\frac{\pi}{2}` all score incorrect.
- `</think>` handling, a missing `</think>` (scored malformed), and an unbalanced last box.

**Right answers scored wrong (20 cases; the scorer's accepted weakness):** `\left(\right)`, a trailing period after a fraction, mixed numbers, scientific notation, `10^3`, `\sqrt4`, repeating decimals, `5=x`, `5/-10`, `2^{-1}`, `\text{5}`.

## (4) Selection
- **Checks pass:** selection is deterministic regardless of input order, the pilot and test key domains are distinct, n=64 is a prefix of n=128 at every level, and pilot and test sets are disjoint. Each subject gets 9–10 items per level at n=64 and 18–19 at n=128.
- **Model influence:** yes, indirectly; this is **S1** below.

## (5) `suite.py` serialization
- I extracted base and head trees with `git archive` and loaded all 7 files in `configs/suite_manifests` under each.
- Aggregate hash `3c8e1d79…` is identical at base and head.
- The GSM8K manifest hash is `1ad902f8…` at both; its round-trip hash is `7d63f3ff…` at both, and the output has no `source_files` key.
- GSM8K serialization is byte-identical.

## (6) Problem text in the tracked tree
None. The fixture's only free-text strings are schema labels. A scan of every added diff line against all 12,500 source problem prefixes found 0 hits. The synthetic fixtures contain invented text only.

## (7) Quarantine text against AP-5 today
Mostly sound: AP-5M is marked PENDING throughout, and the forbidden upgrades match AP-5's "no intelligence-per-joule / difficulty causes energy". One overclaim, S2.

## Findings
- **S1, should-fix (cure before any pilot-driven scorer addition): a scorer change can change the test set.**
  - `eligible_records` uses the same `canonical_math_rational` as the response scorer. M5 lets the pilot audit add scorer rules, which would also change the eligible population and therefore the selection.
  - Executed evidence (`/tmp/mathlens/couple.py`): adding mixed-number parsing raises eligibility to 4,054 and swaps 4 items in the n=64 set. The pilot happened not to change this time.
  - Fix: freeze the reference-side canonicalizer as its own pinned function (for example `canonical_reference_v1`), or make the pinned id-list hashes authoritative.
  - The bench-only real-file test would catch the drift, but it is skipped on CI.
- **S2, should-fix:** `CORRECTNESS_QUARANTINE` (:39) says "malformed and capped count as incorrect (D-047.6)". D-047.6 (`decision_log.md` clause 6) covers malformed only; capped-as-incorrect comes from M2 and the pending AP-5M. Proposed text: "malformed counts as incorrect (D-047.6); capped counts as truncated-incorrect (M2; AP-5M PENDING)".
- **S3, should-fix:** in `load_math_test`, the pointer and licence paths default to None, so both byte checks are silently skipped.
  - The receipt's `license_blob_sha1` is the constant compared with itself (:63).
  - Executed: a call with no licence file returns a receipt claiming `4ccc7f8d…`.
  - Fix: make both paths required, or record them as not checked.
- **S4, should-fix:** pin the five false positives in (3) as golden pairs labelled "known false positive", as packet A does for `2\frac12`, or deny-list magnitude words and `i`/`\mathrm{i}` in step 5. They are rare, but they are in the dangerous direction and currently undisclosed.
- **N1, nit:** the pilot is not subject-balanced (Level 1: 7 Algebra, 5 Prealgebra, 0 Number Theory) while the test set is. The Level-5 95th percentile that sets the cap (M3) comes from a different subject mix than the test set it applies to. Consider interleaving the pilot by subject too.
- **N2, nit:** the extraction fallback to an earlier box when the last box has no braces, from (3).
- **N3, nit:** a `source_files` entry that omits the `lfs_pointer_blob_sha1` key is accepted as null and re-emitted with the key, so it does not round-trip byte-identically.
- **N4, nit:** `ELIGIBILITY_NOTE` does not carry the exclusion counts or per-level retention that packet A §5 asks for; the counts exist only in the full and hash-only manifests.
- **N5, gap to track:** packet A's test that `<think>`/`</think>` survive the `mlx_runtime` decode path is absent. If decoding strips them, every thinking-on response scores malformed. Native rendering with the real tokenizer is also unverified (seat flag F1). `score_math_outcome_table` has no production caller yet (packet B).

