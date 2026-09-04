# Cold-gate packet — the `_fresh_probe` census guard, second survivor (t26-b, 2026-09-02)

Mechanically assembled by the magistrate under the cold-gate charter
(`docs/process/coldgate_charter.md`, sha256
`099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`,
registry `docs/process/coldgate_charter_registry.md:16`). Trigger: rule 11
"any second fix round on the same defect" — the magistrate is NOT
classifying the defect itself this time (the paper-d gate, file 42 there,
ruled that the party proposing to continue should not classify); Q1 asks
the seats to classify. Seats read ONLY this packet and the primary evidence
it names. Read-only.

## The mechanism under review (built from the code, no prior context needed)

`joulewise/arm_readiness.py` holds a constant
`_T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS = 600_000_000_000` (600 s). The cold
gate T26 item 3 (`docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`,
item 3 and its two 2026-09-02 addenda) ruled the number's PROVENANCE as
"eleven governed post-R1 probe sites × 45 s probe timeout + 105 s
ungoverned work". A "probe site" is a call to the helper `_fresh_probe(...)`
in `joulewise/arm_readiness_evidence_t0.py`; "post-R1" means every site
except the one inside `_fresh_clock_reference_batch` (which IS the R1
batch). The test
`tests/test_arm_readiness_evidence_t0.py::test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census`
exists so that a future edit adding or removing a probe site fails a test
instead of silently changing the governed envelope while the constant stays
600 s.

The test's current body (at `e17ea794`, the head under review):

```python
tree = ast.parse(Path(t0.__file__).read_text(encoding="utf-8"))
sites_by_function: dict[str, int] = {}
direct_call_names: set[int] = set()
for node in ast.walk(tree):
    if not isinstance(node, ast.FunctionDef):
        continue
    calls = [call for call in ast.walk(node)
             if isinstance(call, ast.Call)
             and isinstance(call.func, ast.Name)
             and call.func.id == "_fresh_probe"]
    direct_call_names.update(id(call.func) for call in calls)
    if calls:
        sites_by_function[node.name] = len(calls)
# every other reference form fails:
indirect = [(type(node).__name__, getattr(node, "lineno", None))
            for node in ast.walk(tree)
            if (isinstance(node, ast.Name) and node.id == "_fresh_probe"
                and id(node) not in direct_call_names)
            or (isinstance(node, ast.Attribute) and node.attr == "_fresh_probe")
            or (isinstance(node, ast.Constant) and node.value == "_fresh_probe")]
self.assertEqual(indirect, [], "indirect _fresh_probe references")
self.assertEqual(<count of FunctionDef named _fresh_probe>, 1)
self.assertEqual(sites_by_function.pop("_fresh_clock_reference_batch"), 1)
post_r1_sites = sum(sites_by_function.values())
self.assertEqual(post_r1_sites, 11, sites_by_function)
self.assertEqual(t0._PROBE_TIMEOUT_SECONDS, 45)
self.assertEqual(readiness._T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS,
                 (post_r1_sites * t0._PROBE_TIMEOUT_SECONDS + 105) * 1_000_000_000)
```

## History of the defect (two rounds)

| Round | Finder | Finding | Cure applied |
| --- | --- | --- | --- |
| 0 (`7488a3c0`) | — | Test counted direct `Name`-call sites only | — |
| 1 | Sol 256 (file 19, F1, should-fix): an alias `probe_alias = _fresh_probe; probe_alias(...)` adds a governed probe the census cannot see; equivalents: stored callback, `globals()["_fresh_probe"]`, method/lambda | Bench (file 20, commit `e17ea794`): the `indirect` block above — forbids non-call `Name`, `Attribute`, string `Constant`; pins one `FunctionDef`. Four mutants killed (alias, globals-literal, stored callback, twelfth direct call). |
| 2 | terra 257 (file 21, F1, should-fix): `from joulewise.unrelated import _fresh_probe` placed AFTER the local definition rebinds the name; the `ImportFrom`'s `ast.alias` is neither `Name`, `Attribute` nor `Constant`, so the guard passes while runtime calls target the imported function. terra's own table: 6 mutants killed; survivors = this one, plus two computed-name forms (`"_fresh_" + "probe"` via `globals()` / `importlib`) which terra classes operator-only under D-161. | NONE — this packet. |

## Executed evidence (bench, `/Users/edr/code/JouleWise-wt-t26-b` at `e17ea794`)

```
$ grep -c "_fresh_probe" joulewise/arm_readiness_evidence_t0.py
13
$ python3 -c "import re;s=open('joulewise/arm_readiness_evidence_t0.py').read();print(len(re.findall(r'\b_fresh_probe\b',s)))"
13
$ grep -n "_fresh_probe" joulewise/arm_readiness_evidence_t0.py   # (the 12 call lines + the def)
1101 (R1 batch), 1216, 1318, 1365, 1801, 1836, 1837, 1838 ... + `def _fresh_probe`
```

So the module's source contains the literal token `_fresh_probe` exactly 13
times: 1 definition + 12 direct calls (1 R1 + 11 post-R1). There are no
comments, docstrings, `__all__` entries, annotations or imports carrying the
token.

## Candidate cure the magistrate would otherwise apply (NOT applied; the seats rule)

Replace the enumerated `indirect` block by a WHITELIST at the token level:
the number of `\b_fresh_probe\b` token occurrences in the module source must
equal 1 (the `FunctionDef`) + the number of direct `Call.func` `Name` sites
found by the AST census. Any other appearance of the literal token — an
import alias, an `asname`, an attribute, a string, a comment, a docstring, an
annotation — makes the token count exceed the AST count and fails the test.
The AST census and the `FunctionDef == 1` pin stay. This closes the whole
"literal name appears somewhere the census does not count" class in one
inequality instead of naming node types. Residual: computed names
(`"_fresh_" + "probe"`, `importlib`-constructed lookups) — invisible to any
static literal check.

## Questions for the seats

Q1 (classification — answer this FIRST and independently of Q2–Q4). Is terra
257 F1 the same defect class as Sol 256 F1 ("the guard's enumeration of
reference forms is incomplete"), such that the bench cure of round 1 was a
first fix round and a cure of terra's F1 would be a second fix round on the
same defect (rule 11 mandatory trigger, met)? Or is it a distinct defect?
State the rule you applied.

Q2 (closure shape). Does the token-count whitelist above close the
literal-name class completely, or does it too admit a named survivor? Build
your own mutant table against it: at minimum terra's `ImportFrom` shadow,
`import x as _fresh_probe`, a decorator application, a nested redefinition,
a `__all__` string, a docstring mention, and any form you devise. Name the
shape you would install if not this one.

Q3 (residual). Are the computed-name forms operator-only under D-161 (Ed,
2026-08-27: operator-only-adversary refusals are over-engineering; fail-closed
only for physics/evidence/pre-registration)? If yes, the test's docstring
records the residual and no further guard is built. If no, say what closes
it.

Q4 (merge gating for PR #274). The PR installs the ruled 600 s constant, its
census test, the PHYS-1 correction and the empirical kernel row. Given Q1–Q3:
(a) install the ruled shape in-PR (one more bench commit + one more §5 fresh
pass), or (b) merge with terra's F1 recorded and the shape as a kernel row on
main? Answer in terms of what a maintainer of the module loses under (b)
during the interval, not in terms of process cost.

## Charter §9 expected digest

The charter digest above is supplied here for the seat to verify against
`docs/process/coldgate_charter_registry.md` independently of this packet.
