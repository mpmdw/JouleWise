# 73a — COLD GATE verdict on the realized-prefill vector rounds (r2/r3): NOT CLOSED

Fresh Fable instance, no loop context, over a mechanically assembled packet (luna 69 M2 survivor, terra 73 should-fix, diff `0d14893e..504af787`). Outcome: the magistrate's `.lower()`-equivalence claim was false — the registered operand reached the comparison unvalidated. Directed r4 (`18a939f3`): canonicalize the registered operand through `PromptTokenExpectation.from_mapping`. Luna max delta re-audit of r4 follows as trace 75.

**VERDICT: NOT CLOSED** — the magistrate's `.lower()`-equivalence claim is false: the *registered* operand reaches line 1056 unvalidated (raw `config.json` dict), so a case-folded comparator is observably different and survives the suite.

**1. Diff scope** — `git diff 0d14893e..504af787`: exactly one file, `tests/test_bundle_read.py`, +26/-0 (commits 3c8393fd, 504af787). No blocker.

**2. Mutation table** (scratch copy of HEAD 504af787, line 1056 edited, `python3 -m unittest tests.test_bundle_read`; baseline 80 tests OK):

| comparator at line 1056 | result |
|---|---|
| `[:8]` both sides | FAILED — `test_hash_comparison_binds_every_character_not_a_prefix` |
| `[:56]` both sides | FAILED — same test |
| `[-8:]` both sides | FAILED — same test |
| `sorted(...)` both sides | FAILED — same test |
| `.lower()` both sides | **OK (survives)** |
| `.lower()` realized side only | OK (survives; genuinely equivalent — see 3) |
| `.lower()` registered side only | **OK (survives; NOT equivalent — see 3)** |
| `str(reg).lower() != real.lower()` | **OK (survives)** |
| `if False:` (control) | FAILED — 5 tests |

**3. Is `.lower()` equivalent?** Only half of it.
- Realized operand: `_lowercase_sha256` at bundle_read.py:968 routes any non-lowercase value into `missing` → early return `prompt_realization_evidence_missing` before line 1056. Case-folding the realized side is equivalent. Confirmed by the test's 4th vector.
- Registered operand: `_prompt_realization_problems` is called at bundle_read.py:804 with `parsed.get("config.json")` — the RAW dict — unconditionally, even when `BenchmarkConfig.from_mapping` at :786 raised `SchemaError`. The function's own guard (:944) checks only `isinstance(expectation, dict)`; the lowercase-hex rule lives solely in `PromptTokenExpectation.from_mapping` (schemas.py:877-885, `_SHA256_HEX_RE = ^[0-9a-f]{64}$`) and the JSON schema (:1321), neither of which gates this call. The comment at :945 ("Config schema validation owns malformed registrations") is an assumption, not an enforced precondition.
- Reproduced: bundle built normally, then `config.json` rewritten on disk with registered `"A"*64`, realized `"a"*64`. Original code emits `prompt_realization_mismatch … token_ids_sha256`; the `.lower()` mutant emits nothing from this check. Observable difference → not equivalent. (Practical soundness impact is nil — the bundle is still refused by `config.json does not re-validate` and `metadata.config_sha256 mismatch` — so this is should-fix severity, but the closure argument as written is wrong.)
- Kill vector: a test that tampers `config.json` on disk to an upper-case registered hash and asserts the mismatch line is present (or, better, that the function refuses ill-formed registrations itself — see 4).

**4. Structural cause (recommendation, not ruling).** Two rounds were spent enumerating comparator-mutant classes (prefix, suffix, permutation, case) one at a time — an open-ended list that will keep leaking. The design gap is that line 1056 compares a validated string against an unvalidated one: the function consumes the raw dict rather than the already-validated `PromptTokenExpectation`. Fix by (a) passing the validated `BenchmarkConfig`/`PromptTokenExpectation` into `_prompt_realization_problems` (or gating `expectation["token_ids_sha256"]` with the same `_lowercase_sha256` at :944), so both operands are canonical by construction, and (b) collapsing the vector zoo into one test that flips a single nibble at each of positions {0, 31, 32, 63} — which kills every prefix/suffix/permutation/case comparator at once.

**5. Verdict:** NOT CLOSED — the registered hash reaches the comparison unvalidated, so `.lower()` is a live, non-equivalent survivor; close by canonicalising/gating the registered operand and adding the on-disk tamper vector (or the single-nibble-flip test) that kills it.