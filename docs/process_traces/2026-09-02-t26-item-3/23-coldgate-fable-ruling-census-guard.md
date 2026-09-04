# Cold Fable seat ruling — census-guard packet (file 22), 2026-09-02

Seat: fresh Fable 5 instance (Agent tool, read-only, packet + primary evidence only). Custodied verbatim from the task transcript; scratchpad paths redacted.

## Charter digest

Contamination disclosure (registry convening procedure item 2): this seat was launched in a harness that auto-injected `CLAUDE.local.md` (rule 11 doctrine), the session-memory index, and the global `~/.claude/CLAUDE.md` into the system context before the packet was read. I did not open any other narrative document, brief, transcript, scratchpad, or process_traces directory beyond files 19, 20, 21, 22 of the packet's own directory, the census test, the module, `COLD-GATE-RULING.md` item 3 (grep-verified for the provenance paraphrase only), and `docs/decision_log.md` D-161 (index row line 207 and long-form entry lines 10358-10370). Every conclusion below cites evidence I executed or read in the checkout; nothing rests on the injected doctrine.

- Expected value (registry, `docs/process/coldgate_charter_registry.md` line 16, operative row): `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`, status RATIFIED, version v2.
- Observed value (`shasum -a 256 docs/process/coldgate_charter.md` at `a5040ed0`): `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`.
- Packet-stated value (file 22 line 5): identical. Method: shasum on the checkout file; registry read at HEAD `a5040ed0ed08e42845730b897b8df97a42e62a95`. MATCH; merits proceed.
- Checkout pins verified: HEAD `a5040ed0`; `git diff --stat e17ea794 a5040ed0` touches only files 21 and 22 (263 insertions, no code); `git status --short` empty before and after the probes (0 lines). Interpreter Python 3.14.7.

## Q1 classification

Verdict: AFFIRM — terra 257 F1 and Sol 256 F1 are the SAME defect class; the round-1 bench cure (`e17ea794`) was a first fix round; a cure of terra's F1 is a second fix round on the same defect; charter §3.1 ("any second fix round on the same defect") is met, and §9 bullet 2 (two consecutive rounds failing with the same signature) is engaged.

Rule applied: a defect is identified by the INVARIANT the guard fails to enforce and the FAILURE SIGNATURE it produces, not by the syntactic mechanism of the particular mutant that exposed it. The invariant is stated in the test's own words at `tests/test_arm_readiness_evidence_t0.py:887-892`: "direct calls are the ONLY way the module reaches `_fresh_probe` … so every such reference fails here." The signature in both rounds is identical: the module's runtime call graph to a governed probe diverges from the AST site count while every assertion stays green and the constant stays 600 s. Sol 256 F1 (file 19 lines 131-153) exposed it with a load-time alias and named equivalents; the round-1 cure ENUMERATED three node types (`Name`, `Attribute`, `Constant`, test lines 893-904); terra 257 F1 (file 21, F1) exposed the same invariant gap through a fourth form (`ast.alias`) that the enumeration omits. Round 2 is therefore "the enumeration is incomplete" a second time — the same formulation failing the same way.

Consequence under §9: terra's own proposed cure ("add an indirect-reference rejection for `ast.alias` nodes", file 21 F1) is a same-shape round three (a fourth enumerated node type) and must NOT be licensed without explicit justification; my table below shows it would leave at least six further binder forms open (M18, M19, M20, M22, M23, M36). The packet's whitelist is a change of shape (complement instead of enumeration) and is the permitted kind of next spend, subject to Q2.

Counter-argument considered and rejected: one could call Sol's finding "reference to the existing function" and terra's "rebinding of the name" and class them as distinct mechanisms. The test comment lines 887-892 already folds both under one guarantee, and the guard defect (an enumeration that cannot be complete) is identical; classifying by mutant mechanism would let every enumeration gap be relabelled a new defect, which is precisely what the trigger exists to catch.

## Q2 closure shape

Verdict on the packet's candidate as worded: REJECT the claim that the raw-text token-count whitelist "closes the whole literal-name class in one inequality". It closes every form terra and the packet listed, but (i) it admits two named literal-name survivors, one of which is a strict REGRESSION versus the current guard because the packet proposes to REPLACE the enumerated block; and (ii) it fails on harmless documentation, which the packet did not disclose. A different shape closes the class with neither defect.

Method: three guards re-implemented as functions over source text (`current_guard` = verbatim test body; `whitelist_guard` = packet candidate: `len(re.findall(r"\b_fresh_probe\b", src)) == 1 + direct Call.func Name sites`, plus the retained FunctionDef==1 / R1==1 / post_r1==11 pins; `ast-field` = my proposed shape, below). Thirty-eight mutants applied to in-memory copies of `joulewise/arm_readiness_evidence_t0.py`; base source passes all three; checkout untouched.

Executed table (KILLED = test would fail; SURVIVES = test stays green). Mutants inserted at the top of `_derive_power` (line ~1836) or before `def _boot_probe` (line ~498) unless stated:

| Mutant | current | whitelist | ast-field |
| --- | --- | --- | --- |
| M01 alias assignment + call (Sol 256) | KILLED (Name 1836) | KILLED (14 != 13) | KILLED |
| M02 `globals()["_fresh_probe"]` | KILLED (Constant) | KILLED | KILLED |
| M03 stored callback list | KILLED (Name) | KILLED | KILLED |
| M04 twelfth direct call | KILLED (post_r1=12) | KILLED | KILLED |
| M05 `functools.partial(_fresh_probe, …)` | KILLED (Name) | KILLED | KILLED |
| M06 nested `def _fresh_probe` | KILLED (FunctionDef 2) | KILLED | KILLED |
| M07 `from joulewise.unrelated import _fresh_probe` after def (terra F1) | SURVIVES | KILLED (14 != 13) | KILLED (alias.name 498) |
| M08 `globals()["_fresh_" + "probe"]` | SURVIVES | SURVIVES | SURVIVES |
| M09 `getattr(importlib.import_module(__name__), "_fresh_"+"probe")` | SURVIVES | SURVIVES | SURVIVES |
| M10 `import x as _fresh_probe` (module level) | SURVIVES | KILLED | KILLED (alias.asname) |
| M11 `from x import y as _fresh_probe` | SURVIVES | KILLED | KILLED (alias.asname) |
| M12b `import x as _fresh_probe` inside `_derive_power` (local shadow, no added call; its 3 existing calls now target the import) | SURVIVES | KILLED | KILLED (alias.asname 1836) |
| M13 `@_fresh_probe` used as a decorator | KILLED (Name 498) | KILLED | KILLED |
| M14 decorator applied ON `def _fresh_probe` (retry wrapper, no new token) | SURVIVES | SURVIVES | SURVIVES |
| M15 `__all__` string entry | KILLED (Constant 2435) | KILLED | KILLED |
| M16 docstring mention (harmless) | SURVIVES (correct) | KILLED (false positive) | SURVIVES (correct) |
| M17 comment mention (harmless) | SURVIVES (correct) | KILLED (false positive) | SURVIVES (correct) |
| M18 `class _fresh_probe:` redefinition | SURVIVES | KILLED | KILLED (ClassDef.name) |
| M19 `async def _fresh_probe` redefinition | SURVIVES | KILLED | KILLED (AsyncFunctionDef.name) |
| M20 parameter named `_fresh_probe` in `_derive_power` signature | SURVIVES | KILLED | KILLED (arg.arg 1833) |
| M21 `global _fresh_probe; _fresh_probe = _execute_probe` | KILLED (Name 1837) | KILLED | KILLED (Global.names + Name) |
| M22 `except Exception as _fresh_probe:` | SURVIVES | KILLED | KILLED (ExceptHandler.name) |
| M23 keyword argument `f(_fresh_probe=1)` | SURVIVES | KILLED | KILLED (keyword.arg) |
| M24 `_fresh_probe = staticmethod(_fresh_probe)` | KILLED (Name x2) | KILLED | KILLED |
| M25 `sys.modules[__name__]._fresh_probe = …` | KILLED (Attribute) | KILLED | KILLED |
| M26 walrus `(p := _fresh_probe)(…)` | KILLED (Name) | KILLED | KILLED |
| M27 escaped string `globals()["\x5ffresh_probe"]` | KILLED (Constant) | SURVIVES (regression) | KILLED (Constant.value) |
| M28 NFKC homoglyph ImportFrom shadow (fullwidth p, U+FF50) | SURVIVES | SURVIVES | KILLED (alias.name, parser-normalised) |
| M29 NFKC homoglyph alias + call | KILLED (Name, normalised) | SURVIVES (regression) | KILLED |
| M30 `from joulewise.unrelated import *` after def | SURVIVES | SURVIVES | SURVIVES |
| M31 direct call inside an `async def` deriver | KILLED (Name 499) | KILLED | KILLED |
| M32 module-level direct call | KILLED (Name 498) | KILLED | KILLED |
| M33 lambda wrapper inside deriver | KILLED (post_r1=12) | KILLED | KILLED |
| M34 second `_execute_probe` call inside `_fresh_probe` body (retry, no new token) | SURVIVES | SURVIVES | SURVIVES |
| M35 delete 2 direct sites in `_derive_power`, add 1 inside a nested closure | SURVIVES | SURVIVES | SURVIVES |
| M36 `match kind: case _fresh_probe:` capture | SURVIVES | KILLED | KILLED (MatchAs.name) |

Reading of the table:

1. Current guard: 15 survivors. Ten are literal-name binder forms invisible to the three enumerated node types (M07, M10, M11, M12b, M18, M19, M20, M22, M23, M36). Python binds identifiers through at least eleven distinct string-valued AST fields (`Name.id`, `alias.name`, `alias.asname`, `FunctionDef.name`, `AsyncFunctionDef.name`, `ClassDef.name`, `arg.arg`, `keyword.arg`, `ExceptHandler.name`, `Global/Nonlocal.names`, `MatchAs/MatchStar.name`), which is why enumeration keeps failing with the same signature.

2. Packet whitelist: kills all ten of those, but admits two literal-name survivors (M27 escaped string constant; M28/M29 NFKC-normalised homoglyph spelling — the parser maps `_fresh_ｐrobe` to `_fresh_probe`, verified: `ast.alias.name == '_fresh_probe'` while the raw-text token count stays 13). M27 and M29 are killed by the CURRENT guard and would REGRESS to survivors because the packet replaces the enumerated block. Both are deliberate-only constructions (D-161 operator-only, see Q3), so the regression is not a soundness hole, but the packet's "closes the whole class" claim is false as stated. Separately, M16/M17 show the whitelist forbids ever mentioning the helper in a comment or docstring of its own module (raw regex counts comments); the test would fail on documentation, which is a maintainability cost the packet omitted.

3. Shape I would install instead ("ast-field"): keep the FunctionDef==1, R1==1 and post_r1==11 pins; replace the enumerated `indirect` block by a GENERIC IDENTIFIER-FIELD CENSUS over the parsed tree: for every node and every str-valued field (lists included, via `ast.iter_fields`), a value equal to `"_fresh_probe"` is a mention; the only permitted mentions are the single `FunctionDef.name` and the `Name.id` of each direct `Call.func` already counted. It kills every literal-name form in the table including M27/M28/M29 (parser-normalised, escape-resolved), is comment- and docstring-blind (M16/M17 pass, correctly), needs no node-type list, and automatically covers binder fields added by future grammar. It is roughly the same line count as the current block. Its residual is exactly the computed-name set (M08, M09) plus the two non-name classes below.

4. Two survivors of ALL three guards are outside the literal-name class and need naming honestly:
   - M14/M34 (semantic wall-time changes: a decorator on `def _fresh_probe`, or a retry inside its body). The census counts SITES, not seconds; file 20 already records that the runtime question belongs to the empirical row. A retry on a flaky probe is a plausible maintainer mistake, and a two-line pin (`_fresh_probe.decorator_list == []`; exactly one `_execute_probe` call inside `_fresh_probe`) would close the two cheapest forms. NIT; optional.
   - M35 is a NEW defect in the census arithmetic, not a reference-form gap: the site loop walks every `FunctionDef` and re-walks nested functions, so a call inside a closure is counted once for the closure and once for its enclosing function. Executed: one closure site in `_derive_power` reports `{'_derive_power': 4, '_inner': 1}`, post_r1 sum 13 for 12 real sites; M35 (two sites deleted, one closure site added) reports post_r1 = 11 for 10 real sites and passes all three guards. Direction: the ruled derivation overstates the governed work (bound loosens silently), so physics is not endangered, but the equality the test claims to enforce is no longer true of the code. Cure (one line): derive post_r1 from the DISTINCT direct-call set (`len(direct_call_names) - r1_count`), or attribute each call to its innermost enclosing function only. Severity MATERIAL; it should ride the same commit as the shape change; it is not part of the rule-11 chain (different invariant, different signature).

## Q3 residual

Verdict: AFFIRM — the computed-name forms (M08, M09) are operator-only under D-161. Authority: `docs/decision_log.md:10358-10365` (D-161 long-form: "the operative test is MISTAKE vs DELIBERATE (fail-closed for physics/evidence, pre-registration and operator mistakes; deliberate-only guards retire)") and the index row at line 207. Writing `"_fresh_" + "probe"` or an `importlib` lookup of a private helper in the helper's own module cannot happen by mistake, auto-import, or refactor tooling; it is a conscious construction of the name. Recording the residual in the test's docstring is the correct and sufficient disposition.

Same bucket, to be recorded alongside (not built): M30 star-import rebinding (requires the OTHER module to list a private name in its `__all__`, deliberate by construction) and, if the raw-text whitelist were installed, M27/M28/M29 (escape/homoglyph spellings). Under the ast-field shape the latter three are killed anyway, so the docstring residual reduces to: computed names, star import, and wall-time changes inside or around `_fresh_probe` (which the empirical row instruments).

Not operator-only, and therefore NOT dischargeable by docstring: the M35 double count (a refactor into a closure is ordinary maintenance) — it must be fixed in code.

## Q4 merge gating

Verdict: (a) — install the ruled shape in-PR, one bench commit plus one delta §5 fresh pass, with the M35 arithmetic fix in the same commit.

What a maintainer of the module loses under (b) during the interval, in the module's own terms:

1. The test lies about its guarantee. Lines 887-892 tell the maintainer "every such reference fails here". Under (b) main carries a guard where ten literal binder forms pass green, and the single most plausible accidental form — an IDE auto-import `from … import _fresh_probe` or an `import … as _fresh_probe` landing after the definition (M07/M10/M11/M12b) — is among them. A maintainer who reads the comment and trusts it has less protection than a maintainer who reads no comment at all.
2. The derivation `600 s = post_r1 × 45 + 105` is enforced only against a census whose arithmetic double-counts closures (M35). Any consolidation refactor that moves probes into a helper closure makes the census report a number that is not the number of sites.
3. The 600 s constant's ruled provenance rests on this test being the enforcement of "eleven governed post-R1 sites" (ruling item 3, `COLD-GATE-RULING.md:308`). While the test's enforcement is narrower than its claim, the provenance is asserted, not enforced — exactly the condition the test was written to end (test docstring lines 858-862: "enforced, not asserted").

Justification for licensing one more round under charter §9 bullet 2: the next round is a REDESIGN (complement over identifier fields, not a fifth enumerated node type), so a third same-signature finding is closed by construction rather than by luck; if the delta pass nonetheless finds another literal-name form, that is a consult, not round three. The packet's raw-text whitelist would NOT earn this licence as worded, because it re-opens M27 and adds a documentation false positive — a fix round that introduces defects is the pattern the delta re-audit exists to catch.

Severity of the PR-blocking findings: the guard gap (Q1/Q2) is MATERIAL, not BLOCKER — no physics, evidence, or pre-registration outcome depends on it today (the module has exactly 13 tokens, 1 def + 12 calls, verified), and the bound direction under every survivor is either a louder failure or a looser envelope. I did not raise it to force a round; I rule (a) because the cure is one shape change plus one arithmetic line, the question asks what the maintainer loses, and the loss is the truth of the test's stated guarantee on main.

## Findings against the packet

1. MATERIAL (affects Q2): the packet asserts the whitelist "closes the whole 'literal name appears somewhere the census does not count' class in one inequality" with no executed evidence; executed evidence shows two literal-name survivors (M27, M28/M29), one a regression from the current guard because the packet REPLACES rather than augments the enumerated block. The packet's stated residual ("computed names") is incomplete.
2. MATERIAL (affects Q2, asymmetric treatment): the candidate's cost — raw-text token counting fails the test on any comment or docstring naming the helper (M16/M17) — is not mentioned, while the residual of the alternative is. The packet presents one candidate only; terra's own proposed cure (file 21 F1: reject `ast.alias`) is not carried into the packet's history table or evaluated, although it is the natural "round three" the seats should be asked to compare against.
3. NIT (accuracy): the grep line list at packet line 78 elides lines 1723-1726 (`_derive_process_census`, four sites) behind "…"; the count 13 and the composition 1 def + 12 calls are correct (verified: 1101, 1216, 1318, 1365, 1723, 1724, 1725, 1726, 1801, 1836, 1837, 1838 + `def` at 476).
4. NIT (framing): Q1 is phrased with the conclusion embedded ("such that … rule 11 mandatory trigger, met"). It did not affect my answer, which I reached from the test's own invariant statement before reading Q1's clause.
5. Verified as accurate: the reproduced test body (packet lines 31-60) matches `tests/test_arm_readiness_evidence_t0.py:871-920`; the claim of no comments, docstrings, `__all__` entries, annotations or imports carrying the token (packet lines 81-84) is true; the provenance paraphrase of item 3 matches `COLD-GATE-RULING.md:208-211, 308`; the history table's round-1 mutant set matches file 20; the checkout and code pins are correct.
6. New, not in the packet: the nested-closure double count (M35), MATERIAL, cure named in Q2 item 4.

## Executed evidence

```
$ cd /Users/edr/code/JouleWise-wt-t26-b && git rev-parse HEAD
a5040ed0ed08e42845730b897b8df97a42e62a95
$ shasum -a 256 docs/process/coldgate_charter.md
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md
$ sed -n '16p' docs/process/coldgate_charter_registry.md
| sha256 | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` |
$ git diff --stat e17ea794 a5040ed0
 .../21-terra-257-delta-fresh-pass.md               | 131 ++++++++++++++++++++
 .../22-coldgate-packet-census-guard.md             | 132 +++++++++++++++++++++
 2 files changed, 263 insertions(+)
$ grep -n "_fresh_probe" joulewise/arm_readiness_evidence_t0.py
476:def _fresh_probe(
1101:        probe = _fresh_probe(context, kind, f"R1 {server}", argv)
1216:    probe = _fresh_probe(
1318:    probe = _fresh_probe(
1365:    probe = _fresh_probe(context, kind, "thermal", ("/usr/bin/pmset", "-g", "therm"))
1723:        _fresh_probe(context, kind, "keep-awake", ...
1724:        _fresh_probe(context, kind, "agent", ...
1725:        _fresh_probe(context, kind, "browser", ...
1726:        _fresh_probe(context, kind, "monitor", ...
1801:    probe = _fresh_probe(
1836:    batt = _fresh_probe(context, kind, "AC state", ("/usr/bin/pmset", "-g", "batt"))
1837:    custom = _fresh_probe(context, kind, "low-power mode", ("/usr/bin/pmset", "-g", "custom"))
1838:    profiler = _fresh_probe(
$ grep -n "_PROBE_TIMEOUT_SECONDS\s*=" joulewise/arm_readiness_evidence_t0.py
54:_PROBE_TIMEOUT_SECONDS = 45
$ grep -n "_T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS\s*=" joulewise/arm_readiness.py
6349:_T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS = 600_000_000_000
$ TMPDIR=<scratch> python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census
Ran 1 test in 0.032s
OK
$ TMPDIR=<scratch> python3 <scratch>/probe.py        # three guards re-implemented; 36 in-memory mutants
BASE: {'current': ('SURVIVES', ...), 'whitelist': ('SURVIVES', ...), 'ast-field': ('SURVIVES', ...)}
BASE census: {'_fresh_clock_reference_batch': 1, '_derive_clock_probe': 1, '_maintenance_probe': 1, '_thermal_probe': 1, '_derive_process_census': 4, '_derive_powermetrics': 1, '_derive_power': 3} direct sites: 12
M07 ImportFrom shadow after def (terra F1)   | SURVIVES | KILLED (tokens 14 != 1+12) | KILLED (stray mention [('alias', 'name', 498)])
M27 escaped string constant                   | KILLED (indirect [('Constant', 1836)]) | SURVIVES | KILLED (stray mention [('Constant', 'value', 1836)])
M28 NFKC homoglyph ImportFrom shadow          | SURVIVES | SURVIVES | KILLED (stray mention [('alias', 'name', 498)])
M29 NFKC homoglyph alias + call               | KILLED (indirect [('Name', 1836)]) | SURVIVES | KILLED
M16 docstring mention (harmless)              | SURVIVES | KILLED (tokens 14 != 1+12) | SURVIVES
M35 delete 2 sites, add 1 in nested closure   | SURVIVES | SURVIVES | SURVIVES
(full 36-row output reproduced in the Q2 table above)
$ TMPDIR=<scratch> python3 <scratch>/probe2.py
M12b local import-as shadow, no added call: ('SURVIVES', 'all assertions pass') ('KILLED', 'tokens 14 != 1+12') ('KILLED', "stray mention [('alias', 'asname', 1836)]")
M35 sites_by_function: {..., '_derive_power': 2, '_inner': 1} distinct direct Name nodes: 11 sum post_r1: 11
M35b one closure site: sites_by_function: {'_derive_power': 4, '_inner': 1} post_r1 sum: 13 (real post-R1 sites = 12)
NFKC alias.name: ['_fresh_probe']
tokens in M28 raw text: 13
$ git status --short | wc -l
       0
```
