# Cold-gate ruling: dependence-sensitivity (worktree 907f5877)

Cold Fable instance, read-only. Inputs read: packet, reports 14/19/26, the three files under adjudication, `generate_configs.py` 1855–1861/2574–2580, `analysis_engine/__init__.py` 660–712 (block arm means), `multiplicity.py` 148–160. Targeted module: 12 tests, OK.

## Rulings

### Q1 (N1, blocker) — ruling: cure (A), with a specific ten-delta list found and verified at the bench

**Evidence.** The doc prints six-decimal deltas (md:72) but every result descends from 12-digit constants (py:44); Sol's seven-field diff is real. Cure (B) already half-exists — md:95 carries the 12-digit list — so the doc would hold two different lists for one example, and a 12-digit list is not a hand-replicable input; it meets the letter of replication, not the standard.

**(A) is feasible with ONE-decimal deltas and exact rationals everywhere.** Parity fact worth recording so nobody burns a round on it: at one decimal, `s = 1.5` is impossible (sum of centred tenths = 0 forces an even count of odd tenths; Σc² = 2025 ≡ 1 mod 4 forces an odd count). `s = 1.4` and `1.6` are both feasible; I chose `s = 1.4` (first hit, floor/direction outcomes unchanged from the current example: floor passes, direction fails in all three models, gates agree).

**Proposed deltas (J, collection order):** `[5.0, 7.6, 5.5, 4.2, 4.7, 6.8, 5.5, 3.6, 3.9, 3.2]`; keep F = 3.5, se_metrology = 0.2, deterministic_bound_total = 4.0.

Exact rationals (Fractions): sum 50, mean 5, ΣSD² = 441/25 = 17.64, s = 1.4, ρ numerator 108/25 = 4.32, denominator 72/5 = 14.4, ρ̂ = 3/10 exactly, V = 8673473003/5000000000 = 1.7346946006, term sum 0.3673473003. Script output (6 dp), no value within 1e-9 of a rounding tie:

| Model | V | n_eff | ν | repeat SE | repeat-only | total SE | crit | half-width | metrology-aware | decision | t | raw p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Registered n_eff=n | 1.000000 | 10.000000 | 9 | 0.442719 | [3.998570, 6.001430] | 0.485798 | 2.262 | 1.098876 | [3.901124, 6.098876] | [-0.098876, 10.098876] | 10.292337 | 0.000002814 |
| AR(1) ρ̂=0.300000 | 1.734695 | 5.764703 | 4 | 0.583095 | [3.381327, 6.618673] | 0.616442 | 2.776 | 1.711242 | [3.288758, 6.711242] | [-0.711242, 10.711242] | 8.111070 | 0.001256214 |
| Halving | 2.000000 | 5.000000 | 4 | 0.626099 | [3.261949, 6.738051] | 0.657267 | 2.776 | 1.824573 | [3.175427, 6.824573] | [-0.824573, 10.824573] | 7.607258 | 0.001602484 |

Nine AR terms: 0.270000, 0.072000, 0.018900, 0.004860, 0.001215, 0.000292, 0.000066, 0.000013, 0.000002. Independent Simpson-integration check of the t model: p(9, 10.292337) = 0.000002814; p(4, 7.607258) = 0.001602484; crit 2.262/2.776 — agree. Canonical JSON `[5.0,7.6,5.5,4.2,4.7,6.8,5.5,3.6,3.9,3.2]`, SHA-256 `d491f101…3c7a`.

**Minimal change.** py:44 constant := that list; md:69–95 recomputed from the table above (md:95 CLI line uses the same list); golden test parses the doc (Q2). A third cure is not needed.

### Q2 (F9, structural) — ruling: yes, structural; one design change kills the class

**Evidence.** Two patterns: (i) the golden test (test:61) pins the script's own output to hard-coded numbers — it can never see a doc/script divergence, which is how N1 was certified; (ii) every refusal row (test:390) asserts only `exit 2 + empty stdout`, so a deleted guard whose input is also refused downstream is masked (426 masked by `_finite_number(None)`; 373 by 81). Probes at the bench confirm each survivor's reachability and current reason string.

**The single change:** a reason-keyed refusal table plus a completeness meta-test. Rows are `(name, argv-or-call, expected_reason_regex)`; the CLI helper asserts exit 2, empty stdout AND stderr matches the reason. The meta-test AST-walks `scripts/dependence_sensitivity.py`, collects every `raise ValueError("…")` / `parser.error("…")` string literal, and asserts each is matched by some row's regex. A guard without a row then fails the suite; a masked deletion fails on the reason. Golden test: parse the deltas from md:72, assert equal to `EXAMPLE_BLOCK_DELTAS_J`, run `analyze_deltas` on the PARSED list, render each worked paragraph and table row through the doc's own format (`%.6f`, p `%.9f`), and assert the rendered strings are substrings of the doc.

Per survivor (line numbers at 907f5877):
- py:61 bool/str → CLI-reachable (`["1",2,…]`, `[true,…]`; deletion would silently accept them) → row, reason `must be a finite number`.
- py:81 list-type → shadowed by py:373 from the CLI. Delete 373–374 (duplicate); 81 then owns both paths → CLI row `'{"a":1}'` + unit row `analyze_deltas("0123456789")`, reason `must be a JSON list`.
- py:140 V>0 → unreachable: V·n = 1ᵀR1 with R the AR(1) correlation matrix, positive definite for |ρ|<1 (grid min 0.000998 at ρ=−0.999) → delete guard, leave a one-line comment.
- py:148 n_eff finite/positive → CLI-unreachable; private, already unit-tested → keep, unit row `_degrees_of_freedom(10, math.inf)`, reason `not positive and finite` (0.0 is masked by 151; inf is not).
- py:162 interval finite → CLI-reachable (`--se-metrology 1e308`) → row, reason `interval is not finite`.
- py:202 decision finite → CLI-reachable (`--se-metrology 5e307 --deterministic-bound-total 1.7e308`) → row, reason `decision interval is not finite`.
- py:211 evidence finite → unreachable, and the py:205–207 `se_total == 0` branch it protects is reachable only with a subnormal s (constant sequences are already refused by ρ) and is undocumented → replace 205–212 with `if se_total <= 0.0: raise ValueError("total standard error must be positive")`, then `statistic = mean_j / se_total`; unit row via `_model_result(sample_stddev_j=0.0, se_metrology_j=0.0)`; test:342 floor-boundary case changes `se_metrology_j` to 0.1.
- py:405 example exclusivity → CLI-reachable → row `--example --floor 3.5`, reason `cannot be combined`.
- py:422 missing source → CLI-reachable (deletion → AssertionError, exit 1) → row (metrology args, no source), reason `is required unless --example`.
- py:426 missing metrology → CLI-reachable; existing row is masked → add reason `are required unless --example`.
- py:373 parsed-list → delete (see 81).

### Q3 (N2) — ruling: convert, at bench size; not soundness-bearing

Ten `1e308` deltas and a 400-digit integer both exit 1 with an empty stdout — already fail-closed (no artifact). No operator path produces such joules, so this is uniformity, not soundness. The conversion is two tokens: `except (ValueError, OverflowError)` at py:445 and py:457, plus one table row (`[1e308]*10`, reason `overflow`). Cheaper to do than to carry as an open finding.

### Q4 — other failures of the replication standard / registration

1. md:9 — `s` is defined as "the square root of the summed squared distances from d̄, divided by n−1": as written that is √SS/(n−1) = 0.467, not 1.4. Must read "the square root of (the summed squared distances divided by n−1)". Replication defect.
2. md:11 — cites generator lines 1857/2576; the fields are at 1859 (`"family_alpha": 0.05`) and 2578 (`"multiplicity": {"method": "holm", "alpha": 0.05, … "m": 2}`). Cite the field names, not line numbers.
3. md:47 — `⌊·⌋` unglossed at first use; add "(⌊x⌋ is x rounded down to a whole number)".
4. md:69 vs md:95 — two different delta lists for one example; cure A collapses both to one list.
5. py:205–207 — undocumented `se_total == 0` branch (Q2).
6. test:398 — row named `five_blocks_effective_n` is refused for count, not n_eff; rename `five_blocks`.
7. Registration checked and consistent: α = 0.05 fixed (py:34, 195; `--alpha` exits 2), n = 10 (py:35, 89), Holm m = 2 inclusive (md:51; engine `adjusted <= threshold` at multiplicity.py:160; script emits no Holm key). Block delta d_i = (B̄−Ā) with arm means at `__init__.py:676–683` matches md:5.

## Fix-round-2 brief

1. `scripts/dependence_sensitivity.py:44` — replace the constant with `[5.0, 7.6, 5.5, 4.2, 4.7, 6.8, 5.5, 3.6, 3.9, 3.2]`; update the comment at :42 to "mean 5 J, s 1.4 J, ρ̂ = 3/10 exactly".
2. `docs/paper/round7/dependence-sensitivity.md:69–95` — rewrite the worked example from the Q1 table verbatim (all 6 dp, p at 9 dp); md:72 and md:95 carry the same one-decimal list; add one sentence after :75: "Every intermediate is an exact decimal: 17.64, 4.32, 14.4, and ρ̂ = 3/10."
3. md:9 — fix the `s` definition (Q4.1). md:47 — gloss ⌊·⌋ (Q4.3). md:11 — cite field names `family_alpha`/`multiplicity.alpha, m` (Q4.2).
4. py:373–374 — delete the list-type check (keep JSON parse); py:140–141 — delete the V guard, add a comment "V = 1ᵀR1/n > 0 for |ρ| < 1"; py:205–212 — replace with the `se_total <= 0` refusal and unconditional statistic/p (Q2).
5. py:445 and py:457 — `except (ValueError, OverflowError)`.
6. `tests/test_dependence_sensitivity.py:61–159` — golden test now parses md:72 (regex on the `\[[ … ]\]` block), asserts equality with the script constant, runs `analyze_deltas` on the parsed list, renders each worked paragraph + table row with the doc's format strings, asserts substring presence.
7. tests — one `REFUSALS` table with rows (name, argv or callable, reason regex) covering: 61 str/bool, 81 dict (CLI) and str (unit), 148 inf (unit), 162, 202, 205 zero-SE (unit), 405, 422, 426 (add reason), overflow, plus every existing row with its reason added; helper asserts exit 2 + empty stdout + stderr regex. Rename `five_blocks_effective_n` → `five_blocks`; test:342 `se_metrology_j=0.1`.
8. tests — meta-test: `ast.walk` the script, collect every string literal inside `raise ValueError(...)` and `parser.error(...)` calls, assert each matches at least one table reason.
9. Verify: `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_dependence_sensitivity` green; then re-run the 24-mutation table from report 26 — target 0 survivors among guards that still exist.

## Bench commands run

All with `cwd=/Users/edr/code/JouleWise-wt-dependence`, interpreter `/Users/edr/code/JouleWise/.venv/bin/python`, stdin heredocs (no files written except this one).

- `git rev-parse --short HEAD; sed -n '1855,1861p;2574,2580p' configs/…/generate_configs.py` → `907f5877`; `"family_alpha": 0.05` (1859), `"multiplicity": {"method": "holm", "alpha": 0.05, … "m": 2` (2578–2580).
- `python -m unittest tests.test_dependence_sensitivity` → `Ran 12 tests in 1.585s / OK`.
- Random search at one decimal, s = 1.5 (integer tenths, Σc=0, Σc²=2025, 10N=3D): `tries 4000000 found 0` — then the mod-4 parity proof above.
- Solved-last-two-coordinates search, s ∈ {1.4, 1.6}: `s=1.4 FOUND [5.0, 7.6, 5.5, 4.2, 4.7, 6.8, 5.5, 3.6, 3.9, 3.2] … tries 2446877 found 12 elapsed 5.9`.
- Fractions + `analyze_deltas` on the chosen list → `EXACT: mean 5 SS 441/25 … rho 3/10`, `V … = 1.7346946006 neff 5.764703479529583 nu 4`, model rows as tabulated, `agree True`, `values within 1e-9 of a 6-dp rounding tie: []`, SHA `d491f101…3c7a`.
- Simpson integration of the t density: `df 9 t=10.292337 p=0.000002814`, `df 4 t=7.607258 p=0.001602484`, `crit9 2.262 crit4 2.776`.
- CLI probes: `1e308x10 exit 1 … OverflowError: intermediate overflow in fsum`; `bigint exit 1 … int too large`; 61/373/162/202/405/422/426 each `(2, True, <reason>)` as quoted in Q2; `140 min V over rho grid: 0.000998`; `211 subnormal s -> se_total 0.0 stat None p 0.0`.
- `grep -n "<= threshold" joulewise/analysis_engine/multiplicity.py` → `:160 and adjusted[contrast_id] <= threshold`.
