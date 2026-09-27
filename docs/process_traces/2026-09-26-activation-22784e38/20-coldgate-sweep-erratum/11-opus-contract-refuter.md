# Cold gate BFGS-S1-SWEEPCLASS-01, erratum: paired Opus contract-lens refuter

Seat: Opus 5.5, contract lens, working independently of the cold Fable judge. Code: detached worktree `/Users/edr/code/JouleWise-wt-s1swcg-92472459` @ `cbfa9dc36a53d2a136f5efa5597e006233ccf033`. `git status --short` printed 0 lines before and after every probe. Scratch: `/tmp/oc_swerr/`. No repository file edited, no background task, no subagent.

**Contamination disclosure.** The harness placed the owner's global `CLAUDE.md`, the project `CLAUDE.md`, the private project notes and the memory index in my context before the charge arrived. I opened none of the files they point to and cite none of them. Everything below rests on the charge, the packet it names (`90-coldgate-sweep/00-charge.md`, `21-coldgate-fable-ruling.md`, `11-opus-contract-refuter.md`), amendment 51 as it stands (`80-coldgate-r2/30-erratum/21-coldgate-fable-erratum-ruling.md` §10), the code at `cbfa9dc3`, and probes I ran.

**Terms used below** (each defined once, used in this sense only):
- **The sweep**: the test `tests/test_bfgs_consumer_sweep.py`. It lists every **read site** (a place in `joulewise/` or `scripts/` that reads a bundle's `summary_metrics.json`, `metadata.json` or `power_trace.csv`, or calls one of the four **tolerant accessors** `raw_metadata`, `raw_config`, `raw_summary`, `raw_artifact_bytes`, which return a file's content with no battery check) that no **gate call** precedes. The **gate** is the battery check: `authenticate_window_members(...)` (window form) or `BundleReader.metadata()` (reader form); either refuses a bundle whose battery charged or discharged during the run.
- **Silent**: the detector reports nothing for a source, so no allowlist row is demanded and nothing fails.
- **The judge's prototype**: `/tmp/cg_sweep/sweep59.py`, the detector the first cold judge wrote with amendments 51 and 59 applied. **The repository detector**: `sweep_source` in the test file at `cbfa9dc3`.
- **Charging bundle**: the fixture `reader_probe_lib.build(..., charging=True)`, the repository's own charging-pair bundle with the sentinel value `4242.4242` written into its energy files. A probe that returns that sentinel returned energy the gate should have refused.
- **GREEN on the tree**: the proposed check passes at `cbfa9dc3` unchanged, so it costs nothing to land.

---

## Section A: independent verdicts on RSW-1 to RSW-9 (written before any erratum ruling existed; the ruling file was absent at 22:51)

### A.1 Executed evidence

| Id | Command (cwd = the worktree unless stated) | Output (exact, abridged only where marked) |
|---|---|---|
| E1 | `python3 /tmp/oc_sw92/alias.py` | `A1 bound-method alias -> silent []`; `A2 getattr by string -> silent []`; `A3 map over readers -> silent []`; `A4 direct call (control) -> REPORTED [('joulewise/zz_new.py', 'f', 'raw_summary', '-', 4)]` |
| E2 | `python3 /tmp/oc_sw92/rebind.py` | `R1 import then module-level rebind -> silent []`; `R2 import then local def of same name -> silent []`; `R3 ... -> REPORTED` |
| E3 | `python3 /tmp/oc_sw92/cache_probe.py` | `trace_rows after _cache.update on a CHARGING bundle: RETURNED 2 rows; sentinel True` |
| E4 | `python3 /tmp/oc_sw92/try_return.py` | `calibration_bracketing.py:2758 ['Return']`, `reduce.py:2651 ['Return']`, `window_duration_margins.py:944 ['Raise', 'Expr', 'Expr'] -> FALLS THROUGH` |
| E5 | `python3 /tmp/oc_sw92/journal58e.py`; `journal58e_eq.py` | containment: `count 5` (X14's four plus `joulewise/reduce.py _reduce`); equality: `count 4` |
| E6 | `/tmp/oc_swerr/rsw1_forms.py` (`ab724bbf1d44c916`): 13 non-call forms against the judge's prototype and against my implementation of RSW-1's `ref:<name>` rule, applied per function | judge's prototype silent on all but M11. Proposed rule REPORTS: `operator.methodcaller('raw_summary')`, `functools.partial(BundleReader.raw_summary, …)`, `BundleReader.__dict__['raw_summary']`, `vars(BundleReader)['raw_summary']`, `r.__getattribute__('raw_summary')`. Proposed rule silent on: M6 module-level `ACC = 'raw_summary'` then `getattr(r, ACC)()`; M7 module-level `GET = BundleReader.raw_summary`; M8 `'raw_' + k`; M9 `f'raw_{k}'`; M10 default argument `get=BundleReader.raw_summary` (the prototype walks `fn.body` only); M12 `lambda r: r.raw_summary()`; M13 class-body alias |
| E7 | AST scan of tracked `joulewise/`, `scripts/` for every non-callee reference to the four names | `('name','raw_config'): 60, ('kw','raw_config'): 6, ('attr','raw_config'): 17, ('name','raw_summary'): 8` (all 8 are a local variable in `scripts/run_campaign.py:2093-2190`). **Zero** attribute or string-constant references to `raw_summary`, `raw_metadata`, `raw_artifact_bytes`. |
| E8 | `/tmp/oc_swerr/scopes_cases.py` (`c090a6556e2aa3dd`): **direct calls** in scopes the sweep never visits, against both detectors | `U1 lambda`, `U2 def under if`, `U3 def under try at module level`, `U4 module-level __main__ block`: **silent in the judge's prototype and silent in the repository detector at cbfa9dc3**. `U5 comprehension (control)`: REPORTED in both. |
| E9 | `/tmp/oc_swerr/scopes.py` (`d5641a9bd9566105`) on the tree | `defs not reached by qualified(): 37 lambdas in tree: 273`. In those scopes: **zero** tolerant-accessor calls or attributes; the only watched constants are module-level tuples (`bundle.py:66-69`, `bundle_read.py:184-185`, `calibration_ledger.py:136,146`, `publication_privacy.py:268`, `salvage_dangler.py:45-59`, `package_d117_fixture.py:42`, `issue_dg071_dg075_statistics.py:90,94`) |
| E10 | `/tmp/oc_swerr/all_scopes_sweep.py` (`689ff74cfabe34eb`): the judge's prototype with every scope inventoried (every `def` wherever nested, every `lambda`, the module body and every class body) | `ordinary rows: 120`; `extra rows with every scope swept: 0`. The same prototype reports U1 to U4 of E8. |
| E11 | `/tmp/oc_swerr/rsw2_bypass.py` (`d5746dcef296d5ee`), charging bundle, fresh reader each | control `raised BatteryStatusRefusal`. **RETURNED, sentinel True** for: C1 `r._cache.setdefault('metadata', r.raw_metadata())`; C2 `r._cache.__setitem__(...)`; C3 `vars(r)['_cache']['metadata'] = …`; C4 `object.__setattr__(r, '_cache', {...})`; C5 `vars(r).update(_cache={...})`; C6 `r._cache = {...}`; S1 a subclass of `BundleReader` overriding `_battery_verdict`; S2 a subclass overriding `metadata` with `return {}`; M1 `BundleReader.metadata = lambda self: {}`; M2 `setattr(bundle_read, 'authenticate_window_members', …)` |
| E12 | inline: passing bundle A, `r.metadata()` passes, then `r._path = Path(B)` with B the charging bundle whose trace holds `9999.25`, then `r.trace_rows()` | `control charging: BatteryStatusRefusal`; `P1 ... trace_rows -> charging bundle rows [{'timestamp_s': '35.0', 'power_w': '9999.25', ...}]` |
| E13 | `/tmp/oc_swerr/static_bypass.py` (`e13096e1f51d07fb`), the judge's prototype on the sources of P1, S1, S2, M1, C3 | all **silent** (M2 is reported only because the prototype does not recognise `from joulewise import bundle_read` as importing the gate) |
| E14 | AST scan for `_cache`, `_battery_verdict`, `_path` outside `bundle_read.py`; subclasses of `BundleReader`; stores to attributes of `BundleReader`/`bundle_read`; `setattr`/`delattr` first arguments | `_cache`: 0 (attribute, keyword or string). `_battery_verdict`: 0. `_path`: 12 attributes, **all on `self`** (`bundle.py`), 2 strings in unrelated f-string keys (`evidence_night.py:363`, `generate_g2a_probe_inputs.py:1004`). Subclasses of `BundleReader`: 0. Stores to `BundleReader.*`/`bundle_read.*`: 0. `setattr` first args: `core`, `module` (the generic `replaced(module, **attributes)` helper, `scripts/sample_quiet_predicate_evidence.py:541`; its callers patch `quiet_admission`, `tempfile`, `run_night`), `namespace`, `self._tokenizer` |
| E15 | inline AST over `bundle_read.py`: every subscript write into `self._cache` | 17 writes; 4 have a non-constant key, each a name bound from an f-string with a prefix ending in `:` (`raw-bytes:`, `source_curve:`, `jsonl:`, `tolerant:`), so none can equal `"metadata"`. No method of `self._cache` is called (`grep '_cache\.\w'`: nothing). `__init__` binds it by an **annotated** assignment: `self._cache: dict[str, Any] = {}` (line 420) |
| E16 | `symtable` over every tracked file: every binding of `BundleReader` / `authenticate_window_members` | `import-only bindings: 29`; other bindings: only the `def` and the `class` in `joulewise/bundle_read.py`. No `as`-alias or relative import of either name. `grep`: 25 lines `from joulewise.bundle_read import`; the package does use relative imports elsewhere (`analysis_manifest_v2.py:16`) |
| E17 | `sed` of `joulewise/envelope_gate.py:71-245, 651-675`; `git grep -n -i envelope` over `docs/contracts` | every reader reaches `_manifest_record` (`reader.metadata()` at `:233`) or the call returns `_refused` before any `raw_summary` (`:100-107`); a battery refusal is a `BundleReadError`, returned as `REASON_SUITE_MANIFEST_MISSING` (`:101-102`). **`docs/contracts/analysis_plans.md:270`**: AP-5 "envelope-validation smoke gate must pass before any scored campaign"; **`:277`**: "Failed envelope validation … gives `not estimable`/L1" |
| E18 | `sed` of `scripts/make_figures.py:168-313, 679-760`; `git grep` for callers | `main` takes `--input-manifest` (default `analysis/rpt001-v2/input_manifest.json`, **tracked**) and `--bootstrap-input-manifest`; `gate_inputs` takes experiment ids from the manifest and does not check them against `EXPERIMENTS`. `gate_inputs` reads only `summary.get("status")`. `realized_output_tokens` reads `workload_observed.output_token_count` and the decode events' `emitted_tokens`, returns `(count, "outputs/tokens.jsonl")`; its only caller is `extract_rows` (`:332`); `extract_rows` has no caller in `joulewise/` or `scripts/` |
| E19 | `/tmp/oc_swerr/rsw5.py` (`535a32a4377bc3a2`): RSW-5's regex over every function; then the same functions checked for a **module constant** whose value matches | `functions (excl adapters): 28`. Module constants matching: 11 (`RAW_POWERMETRICS_NAME` in `reduce.py`, `SOURCE_ARTIFACT` in `idle_dependence.py`, `RAW_SAMPLES_NAME`/`RAW_IDLE_NAME` in `adapters/powermetrics.py`, `GOVERNED_ARTIFACTS` in `calibration_ledger.py`, …). **18 further functions** use one by name and hold no matching literal, among them `joulewise/reduce.py::_derive_anchor_context`, `joulewise/cli.py::_verify_powermetrics_raw_to_trace`, `joulewise/idle_dependence.py::_base_payload`, `joulewise/receipt_oracle.py::derive_bracket_session_receipt_oracle` |
| E20 | `/tmp/oc_swerr/rsw5_wide.py` (`0ca9cfd3d4a4e14b`): regex widened to `powermetrics[A-Za-z0-9_]*\.plist`; `git grep` of every `raw/…` literal | still `28` (the post-run idle capture `powermetrics_idle_post.plist` appears only in functions already counted); raw names in code include `raw/powermetrics_idle_post.plist`, `raw/powermetrics_idle_attempt_{attempt}.plist`, `raw/battery_float.{pre,post}.ioreg`, which RSW-5's regex does not match |
| E21 | module-level constants equal to or ending in `events.jsonl` | 10, e.g. `calibration_ledger.py:133 GOVERNED_ARTIFACTS`, `bundle_read.py:184 _REQUIRED_ARTIFACTS` |

NOT EXECUTED in Section A: the repository's own unit tests; any mutation of the repository's sweep (all rows below were run against the judge's prototype or as behaviour); a reader search for the envelope-gate verdict beyond `git grep` of the tracked tree; whether AP-5 is live or retired (I read its contract rows only).

### A.2 Verdicts

**RSW-1 (57 (d), `ref:<name>`). Finding RIGHT. Replacement text RIGHT in what it covers, INCOMPLETE, and it misses a larger hole of the same kind.**
- No false positives: the rule is GREEN on the tree (E7: zero attribute or string references to the three names; the 8 `raw_summary` hits are a local variable, which the rule does not match).
- It covers `operator.methodcaller`, `functools.partial`, `__dict__`/`vars()` lookups and `__getattribute__` (E6), because each carries the name as an attribute or a string constant.
- It misses names bound **outside a function** (module level, class body) and in defaults (E6: M6, M7, M10, M13), and names built at run time (M8, M9). The run-time forms cannot be closed by syntax; they belong in 51 (h).
- **Larger hole (new, N1): scopes the sweep never visits.** A plain direct call `r.raw_summary()` inside a `lambda`, inside a `def` nested under an `if`/`try`/`with`/`for`, or in module-level code such as `if __name__ == "__main__":` is silent in both detectors (E8). The tree holds 37 such defs and 273 lambdas, and none of them reads today (E9, E10: sweeping every scope adds 0 rows). So the closure is GREEN on the tree.
- The RSW-1 text also does not say whether a gate can gate a `ref:` site. I propose it never can: a string or an unbound attribute has no receiver for [E] to bind to.

**RSW-2 (57 (b) 4, the cache slot). Finding RIGHT. Replacement text INCOMPLETE, and one clause would be RED on the tree as literally written.**
- It covers `setdefault`, `__setitem__`, `update` and rebinding (C1, C2, C6), because it forbids the identifier `_cache` outside `bundle_read.py` and forbids method calls on it.
- It misses `vars(r)['_cache']`, `object.__setattr__(r, '_cache', …)` and `vars(r).update(_cache=…)` (E11: C3, C4, C5, all executed bypasses). These name `_cache` as a string or a keyword, not as an attribute.
- It misses variable-key writes inside `bundle_read.py`. It permits "assignments to a subscript of `self._cache`" without constraining the key. Today every variable key is prefixed (E15), but a new `self._cache[k] = raw` with `k == "metadata"` would pass.
- It misses a sibling slot, `_path`. A gate that passes on bundle A, followed by `r._path = B`, makes `trace_rows()` return a charging bundle's rows (E12, executed), and the detector is silent (E13).
- "Written only by the assignment `self._cache = {}`" would be RED if implemented as an `ast.Assign` match: the tree uses an annotated assignment (E15).

**RSW-3 (57 (b) 1, the binding rule). Finding RIGHT. Rule ENFORCEABLE by AST with no false positives today (E16). Replacement text INCOMPLETE.**
- **The form restriction needs a decision.** "Only by `from joulewise.bundle_read import <name>` without `as`" forbids a relative import. That is fail-closed and consistent with 51 (c), which also recognises only the absolute module. Say so, so that a seat does not read it as an oversight.
- **Gaps (new, N2): the gate can be replaced without rebinding the name.**
  - A subclass of `BundleReader` that overrides `metadata` or `_battery_verdict` (E11: S1, S2, executed bypasses). `R(b).trace_rows()` is not a read site, so nothing is reported (E13).
  - A store to `BundleReader.metadata` or `bundle_read.authenticate_window_members`, directly or through `setattr` (M1, M2).

  Each is GREEN on the tree to forbid (E14: no subclass, no such store, no `setattr` on either).
- A generic patch helper that receives the module as a value (`replaced(module, **kw)`, which exists in `scripts/sample_quiet_predicate_evidence.py:541`) cannot be seen by syntax unless its call names the module. That goes into 51 (h).

**RSW-4 (`historical` rows). Finding RIGHT for both groups: the `historical` condition is false. Replacement WRONG for the two `envelope_gate.py` rows, and weaker than necessary for `realized_output_tokens`.**
- **Envelope rows.** `analyze_envelope_gate(bundle_dirs, …)` takes any bundles (E17), so "cannot be pointed at a later bundle" is false. But `non_claim` (ii) is also false. 51 (f) defines a claim artifact as "a file a paper number is taken from **or licensed by**". AP-5 makes an envelope pass the precondition of every scored campaign, and a failed envelope the disqualifier (E17). So the envelope verdict is itself a claim artifact, and `_level_window_energy_records` writes energy into it (`calibration_evidence_only.level_window_gross_energies_j`).
  - The refuter's search looked for code readers only. The licensing reader is a contract row.
  - Under 58 (d), no class is left for these rows. `behind_gate` has no callee form. `historical` is false. `non_claim` (ii) is false.
  - The honest closure is to **gate at the site**: a production edit to `joulewise/envelope_gate.py`, adding `reader.metadata()` on the same name immediately before each `raw_summary()` (`:133` inside the comprehension; `:654` in the loop). This is **behaviour-identical** on every input. Every reader that reaches `:133` already passed `metadata()` inside `_manifest_record` (`:100-107` return `_refused` otherwise), and `metadata()` memoises on success. So the added call returns the cached dict.
  - Then the detector sees a dominating reader-form gate bound to the same name, and the rows leave the allowlist.
  - This is outside S1's WRITE_SCOPE as far as the packet shows, so it is its own lane, together with the mislabelled reason code (`suite_manifest_missing` for a battery refusal).
  - Until that lane lands, S1 must carry these two rows under something. I recommend that the judge rule them **returned** (51 (g) 6), and that S1 land with the two rows keyed under `historical` **only if** the judge explicitly accepts a false condition for a bounded time. I do not recommend that. The better order is: land the one-line gating edit as the first commit of the lane before S1's sweep closes.
- **make_figures rows.** `historical` is false (E18: `--input-manifest`/`--bootstrap-input-manifest` re-point it; `gate_inputs` does not check experiment ids against `EXPERIMENTS`).
  - `gate_inputs`: `non_claim` (i), field `status`. RIGHT.
  - `realized_output_tokens`: it reads a token count and returns an int and a constant string. So `non_claim` (i) (fields `workload_observed.output_token_count`, and `emitted_tokens` from the journal) is right and does not depend on callers. RSW-4's (ii) is weaker than necessary.
  - `extract_rows` (3 rows): `non_claim` (ii) with no production caller. RIGHT today, but (ii) rests on callers that the sweep does not re-check. See N3 in A.3.
- **The (h) item "a gate in a callee" is RIGHT** as a stated limitation.

**RSW-5 (raw capture). Finding RIGHT. The count is 28 at `cbfa9dc3` (E19, reproduced). The regex and the screen are INCOMPLETE.**
- The screen matches literals only. 18 further functions reach the raw capture through a module constant (E19), including the frozen reducer's `_derive_anchor_context` and the strict validator's `_verify_powermetrics_raw_to_trace`. Amendment 51 (a) already built module-constant resolution for watched names, and RSW-5 must reuse it.
- The regex misses `powermetrics_idle_post.plist` and `powermetrics_idle_attempt_{n}.plist` (E20). The count stays 28 today, but a new function naming only the post-run capture would be invisible.
- `battery_float.{pre,post}.ioreg` holds current and voltage, which are energy-class by the ruling's own definition. They are read by the gate itself. I would add them to the screen for inventory, not for classing. This is optional: NIT.
- **Why the set is computed-equals-constant.** The sweep computes the set of functions from the tree and asserts it equals a constant written in the test, so any new member fails until someone adds it. Each new member must then carry the refuter's statement. That is the right shape, and it is minimal.

**RSW-6 (NIT). RIGHT** (E5). The same module-constant gap applies to the journal screen (E21), which already calls itself "a screen". Add the module-constant clause here too, for the same reason as RSW-5.

**RSW-7 (NIT). RIGHT.** The kind `journal` for `events` is consistent with 58 (b)'s last sentence.

**RSW-8 (NIT). Accepted without re-execution.** `request_rows` reads `outputs/requests.jsonl` and `request_token_rows` reads `outputs/request_tokens.jsonl` (`bundle_read.py:700,703`). The refuter's B11 key list is the controller's writer. I did not re-run B11 (NOT EXECUTED).

**RSW-9 (NIT). RIGHT, no change.** E4 reproduces it. Widening 59 (a) to "always-raising helpers" would need inter-procedural analysis, and today no row arises.

### A.3 Additional findings (Section A, independent)

- **N1 (SHOULD-FIX, the most important latent hole): unswept scopes.** Replacement text, a new 51 (b) 0: "The sweep inventories **every scope** of a tracked file: each `def` and `async def` wherever it is nested (qualified name: the enclosing qualified name, then `.`, then its name; a nested def under a compound statement is qualified exactly as one in the body), the module body (qualified name `<module>`), each class body (qualified name `<Class>.<body>`), and each `lambda`. A `lambda`'s body is swept **as part of its enclosing scope**, and a read site inside a `lambda` is **never gated**, because the lambda runs at a time the enclosing gate does not govern. Parameter defaults and decorators belong to the enclosing scope." Test rows: R51-23 to R51-26 = E8's U1 to U4 → each reported. Counterfactual: the repository detector at `cbfa9dc3`, which is silent on all four (E8, executed). Row R51-27: the tracked tree → the reported keys still equal the allowlist, with 0 added rows (E10, executed on the prototype).
- **N2 (SHOULD-FIX): the gate replaced without rebinding its name.** Text in A.4.
- **N3 (SHOULD-FIX): a `non_claim` (ii) row rests on callers that the sweep does not re-check.** A new production caller of `extract_rows` that writes a figure would not change the row's key, so nothing fails. Replacement text, appended to 51 (f)'s (ii) cell: "A (ii) row also carries a third field `returns_to`, a tuple of `path::qualified function`. The sweep asserts, exactly as in the callers form of `behind_gate`, that every call of the function's name in a tracked file under `joulewise/` or `scripts/` lies in a listed function. An empty tuple asserts that no production caller exists." Test row: `extract_rows` with `returns_to=()` passes on the tree. It fails when a call of `extract_rows` is added to `main`. Counterfactual: (ii) as ruled.

### A.4 Replacement texts I propose (Section A)

- **RSW-1 (57 (d) 5):** "Amendment 51 (b) 1 is extended. A read site is also any **reference** to the name `raw_summary`, `raw_metadata` or `raw_artifact_bytes` that is not the callee of a call: an attribute of that name on any expression, or a string constant equal to it, in any scope of 51 (b) 0. It is reported as operation `ref:<name>`, watched name `-`, and is **never gated**. `raw_config` is excluded: 17 tracked attribute references are dataclass fields of that name, and `config.json` holds no energy-class value. 51 (h) gains: an accessor name built at run time (`'raw_' + k`, an f-string)."
- **RSW-2 (57 (b) 4):** "**The reader's private state.** (i) Outside `joulewise/bundle_read.py`, the identifiers `_cache` and `_battery_verdict` occur in no tracked file under `joulewise/` or `scripts/` as an attribute name, a keyword-argument name or a string constant. (ii) Outside `joulewise/bundle_read.py`, no attribute named `_path` is read or written on a receiver other than `self`. (iii) Inside `joulewise/bundle_read.py`, `self._cache` is bound only in `BundleReader.__init__`, by an assignment or annotated assignment of `{}`. No method of `self._cache` is called. Every subscript write into `self._cache` has as its key either a string constant or a name bound in the same function from an f-string whose leading literal ends in `:`. (iv) A write whose key is the constant `"metadata"` occurs in `BundleReader.metadata` and in no other function. (v) `self._path` is bound only in `BundleReader.__init__`." Test rows: R57-6b = C1, C3, C4, C5 of E11 and P1 of E12, each as source in `joulewise/zz_new.py` → fails naming the site. Counterfactual: 57 (b) 4 as ruled, under which C1, C3, C4, C5 and P1 are silent (C1 by B3 of the first refuter; the others E13, executed on the prototype). Behaviour companions: E11 and E12, executed.
- **RSW-3 + N2 (57 (b) 1, appended):** "… and in every tracked file under `joulewise/` and `scripts/`: (a) the names `authenticate_window_members` and `BundleReader` are bound only by `from joulewise.bundle_read import <name>` without `as`, or by their one definition in `joulewise/bundle_read.py`. No assignment, `def`, `class`, parameter, `for`/`with`/`except`/comprehension/`match` target, `global`/`nonlocal` rebinding, or other import binds either name. A relative import is refused, as 51 (c) refuses it. (b) No class has among its bases an expression whose last name is `BundleReader`. (c) No assignment, augmented assignment or `del` targets an attribute of an expression whose last name is `BundleReader`, `bundle_read` or `battery_float`, or of a name bound by importing `joulewise.bundle_read` or `joulewise.battery_float`. (d) No call of `setattr`, `delattr` or `object.__setattr__` has such an expression as its first argument. 51 (h) gains: a patch helper that receives the module or class as a value bound elsewhere." Test rows: R57-11 = R1 and R2 of the first refuter, plus S1, S2, M1 and M2 of E11 as sources → each fails naming the binding, base or store. Counterfactual: 57 (b) 1 as ruled (E2 and E13, executed silent).
- **RSW-4:**
  - The envelope rows are **returned**, and gated at the site in the lane described in A.2 (production change to `joulewise/envelope_gate.py`, behaviour-identical, with the reason for the change stated). They are **not** re-classed `non_claim` (ii).
  - `make_figures.py::gate_inputs`: `non_claim` (i), field `status`.
  - `::realized_output_tokens`: `non_claim` (i), fields `workload_observed.output_token_count` and the decode events' `emitted_tokens`.
  - `::extract_rows` ×3: `non_claim` (ii), `returns_to=()` (N3).
  - 51 (h) gains "a gate in a callee".
  - `historical` is kept only on `issue_dg071_dg075_statistics.py`, whose pin is a SHA-256 in committed code; I did not re-check that row (NOT EXECUTED).
- **RSW-5 (58 (f)):** as proposed, with two changes. (i) The regex becomes `^(raw/)?(powermetrics[A-Za-z0-9_]*\.plist|nvidia_smi[^ /]*\.csv)$`. (ii) A function is a member if it holds a matching string constant **or names a module constant, in the sense of 51 (a) and collected over all tracked files, whose value holds one**. The sweep computes the set and asserts it equals the constant `RAW_CAPTURE_READERS`. At `cbfa9dc3` the literal set is 28 (E19). The module-constant clause adds 18 candidates by my name-match approximation (E19). The exact number under the 51 (a) resolver is NOT EXECUTED, and the seat reports it with the rows listed.
- **RSW-6:** as proposed, plus the same module-constant clause.
- **RSW-7:** as proposed.
- **RSW-8, RSW-9:** no change.

### A.5 Section A verdict counts

- **BLOCKER: 0.** On every path I traced, no energy value reaches a claim artifact without a battery gate.
- **SHOULD-FIX, from the first refuter:** RSW-1, RSW-2, RSW-3, RSW-4 and RSW-5 are upheld. RSW-1, RSW-2, RSW-3 and RSW-5 need wider texts. RSW-4's envelope replacement is **wrong**.
- **SHOULD-FIX, new:** N1, N2, N3.
- **NIT:** RSW-6 and RSW-7 are upheld with a small addition. RSW-8 and RSW-9 stand with no change. The `ioreg` inclusion is optional.

---

## Section B: refutation of the erratum ruling

The ruling file appeared at 23:00. I read it in full (80349 bytes, lines 1 to 556) after Section A was written; Section A is unchanged. The judge re-saved it at 23:00:55 (80620 bytes, 557 lines). I did not re-read it in full. A keyword check of the re-saved file (`lambda`, `_path`, `licensed`, `AP-5`, `type(`) shows no text that addresses B-1 to B-5; the visible change is a corrected line reference in R60-3 (`:228-233`). **The ruling** below means `21-coldgate-fable-erratum-ruling.md`. **The ruled rules** means its amendments 57 to 60 as they stand in its §6. **The judge's prototype of the ruled rules** is `/tmp/cg_sw_erratum/rules60.py` (`binding_violations`, `cache_violations`, `ref_rows`), which I ran unchanged.

### B.0 Where the ruling and Section A agree

These points were reached independently:
- All nine findings are upheld.
- **RSW-2.** The refuter's text is too weak. The ruling's 57 (b) 4 (i) forbids `_cache` as an attribute, a string constant and a keyword name, which covers my C3, C4 and C5. Its (iii) constrains computed keys to the f-string-with-colon-prefix form, which is my E15.
- **RSW-3.** The ruling adds the subclass case and the attribute-store case, and narrows 51 (c)'s window form.
- **RSW-5.** The screen must follow module constants. The ruling's 20 missed functions is my E19's 18 plus the ones reached through class-body names and `LOGICAL_FILE_COUNT`.
- **RSW-4.** `historical` is false for seven rows. `gate_inputs` is `non_claim` (i). `extract_rows` is pinned by a caller check (my N3 and the ruling's 60 (c) 2 are the same idea).

The ruling also found two things I did not:
- The refuter's RSW-7 assertion is false, because `problems` also names `events.jsonl` (its Y16).
- It executed the envelope counterfactual (its Y11).

### B.1 Executed evidence (new in Section B; `/tmp/oc_swerr/`, SHA-256 prefix)

| Id | Command | Output (exact) |
|---|---|---|
| F1 | `secB_rules.py` (`49a3ceefd3446c59`): the judge's detector `sweep59.py` and the judge's prototype of the ruled rules, on the tree and on nine added sources | `tree: 0 0 0` (refs, binding, cache). Each of V1 to V9 below: **`detector:silent binding:0 cache:0 ref:0`** |
| F2 | `secB_behaviour.py` (`b7ecf186ad066deb`), the charging bundle | control `raised BatteryStatusRefusal`; **`V1 battery_float.authenticate_bundle patched  RETURNED sentinel=True`** (`trace_rows()` of the charging bundle); `V1w same patch, window gate  raised WindowBatteryRefusal`; **`V5 type('Q',(BundleReader,),...) subclass  RETURNED sentinel=True`**; control after: `raised BatteryStatusRefusal` |
| F3 | inline AST over `bundle_read.py` and the tree | `class BundleReader _cache refs 47 _path writes [419]`; no `_path` on a non-`self` receiver in `bundle_read.py`; **no** non-callee reference to `derive_idle_mean_uncertainty`, `extract_rows`, `_read_summary`, `evaluate_member`, `realized_output_tokens`, `_level_window_energy_records`; **no** store or `setattr` on an attribute of `battery_float`, `bundle_read` or `BundleReader`; the envelope strings `envelope_validated`, `envelope_failed`, `calibration_evidence_only`, `envelope_gate.v1` occur nowhere outside `envelope_gate.py`, and `bundle_refused` occurs at `determinism_gate.py:28` |
| F4 | `git grep` for `RAW_IDLE_POST_NAME`, `powermetrics_idle_post`, `powermetrics_idle_attempt`; membership in the judge's `rawcap_union.json` (48 entries) | `cli.py:1369` reads `raw/RAW_IDLE_POST_NAME` inside `_strict_uncertainty_evidence_problems`, which **is** in the 48 (through `RAW_IDLE_NAME` on the line before). Other hits: adapters, `publication_privacy.py:277`, `uncertainty_evidence.py:1579`, `run_campaign.py:2041`, `salvage_dangler.py:549`, `environment_admission.py:319`, all in functions already among the 48, or f-strings the regex could never match |
| E8–E12, E14, E17 | Section A, reused | as stated there |

The sources V1 to V9 (all as `joulewise/zz_new.py`):
- V1: `battery_float.authenticate_bundle = lambda p: …not_applicable_verdict…` at module level, then `BundleReader(b).trace_rows()`.
- V2: `setattr(battery_float, 'authenticate_bundle', v)`.
- V3: `import joulewise.bundle_read` then `joulewise.bundle_read.authenticate_window_members = fake`.
- V4: `setattr(joulewise.bundle_read, 'authenticate_window_members', fake)`.
- V5: `Q = type('Q', (BundleReader,), {'metadata': lambda self: {}})`, then `Q(b).trace_rows()`.
- V6: gate on reader `r` over bundle `a`, then `r._path = b`, then `r.trace_rows()`.
- V7: `g = lambda r: r.raw_summary()`.
- V8: a `def` nested under `if` that calls `raw_summary()`.
- V9: `if __name__ == '__main__': print(BundleReader(sys.argv[1]).raw_summary()['gross_energy_j'])`.

`git status --short` in the worktree: 0 lines after every probe.

NOT EXECUTED in Section B:
- The repository's unit tests.
- Any mutation of the repository's sweep; every row below was run on the judge's prototypes or as behaviour.
- The ruling's 48-member count under the widened regex of B-6.
- Whether AP-5 is in current use, beyond its contract rows (`analysis_plans.md:262-277`) and the ruling's own disclosure that a campaign using the envelope gate is queued (its §0 item 2).

### B.2 Findings

**BLOCKER: none.** On every path the ruling, the first refuter and I traced, no energy value reaches a claim artifact without a battery gate at `cbfa9dc3`. The ruling's §4 sets its own standard: a GREEN sweep must mean that no ungated energy read *can* be added silently. The findings below are places where the ruling misses that standard, each by the judge's own prototype (F1). Each closure is GREEN on the tree, so landing it costs only the rule and its rows.

#### B-1 (SHOULD-FIX, highest priority). Scopes the sweep never visits. The ruling's [D0] "seen by the sweep as ruled" is false for them.

- **The problem.** A plain **call** `r.raw_summary()` is silent in all of these places:
  - inside a `lambda` (V7);
  - inside a `def` nested under an `if`, `try`, `with` or `for` (V8);
  - in module-level code such as a script's `__main__` block (V9).

  It is silent in the judge's detector, in the repository detector at `cbfa9dc3` (E8), and in all three ruled rules (F1). The detector walks only the direct `body` of each def and class, and it skips lambdas.
- **This is the simplest door of all.** It needs no alias, no patch and no private name. It is a new door beside [D1] to [D4] of the ruling's diagram.
- **Two restated texts assume the missing coverage:**
  - 57 (d) 5 reports a *reference* at module level as `<module>`, while a *call* at module level is never swept;
  - 58 (f) 3 says "Nested functions are separate functions and inherit nothing", but a def nested under a compound statement is never reached.
- **Cost.** GREEN on the tree: sweeping every scope adds 0 rows (E10). There are 37 unreached defs and 273 lambdas, and none of them holds a read (E9).
- **Replacement text** (new 51 (b) 0): "The sweep inventories **every scope** of a tracked file: each `def` and `async def` wherever it is nested (qualified name: the enclosing qualified name, `.`, its name; a def nested under a compound statement is qualified as one in the body), the module body (`<module>`), each class body (`<Class>.<body>`), and each `lambda`. A `lambda`'s body is swept as part of its enclosing scope, and a read site inside a `lambda` is **never gated**, because the lambda runs at a time the enclosing gate does not govern. Parameter defaults and decorators belong to the enclosing scope." 58 (f) 3 and 57 (d) 5 then read "function or scope".
- **Test rows.** R51-23 to R51-25: V7, V8, V9 → each reported (`raw_summary`, watched `-`). Counterfactual: the repository detector at `cbfa9dc3` and `sweep59.py`, executed silent (E8, F1). R51-26: the tree → reported keys still equal the allowlist, with 0 added rows. Counterfactual: a scope walk that invents rows for module constants. Executed GREEN on the prototype (E10).

#### B-2 (SHOULD-FIX). The gate's **behaviour** can be replaced without rebinding a gate name, and the ruled 57 (b) 1 is silent.

- **What is silent.** All of these are silent under the ruled rules (F1):
  - V1 and V2 replace the **verdict source** `battery_float.authenticate_bundle`. `_battery_verdict` calls it through the module attribute, so every reader in the process then admits a charging bundle. Executed: `trace_rows()` returned the sentinel (F2).
  - V3 and V4 replace `authenticate_window_members` on the module written in full (`joulewise.bundle_read.…`).
  - V5 builds a subclass with `type(...)`, which is not a `class` statement, so 57 (b) 1 (ii) does not see it. Executed: it returned the sentinel (F2).
- **What 57 (b) 1 (iii) covers today.** It covers "an attribute of a gate name". The gate names are `authenticate_window_members` and `BundleReader`, so the verdict module and the module name written in full are outside it.
- **Cost.** GREEN on the tree: F3 finds no store or `setattr` on those receivers.
- **Replacement text** for 57 (b) 1 (ii) and (iii):
  - "(ii) no class, and no call of `type` with three arguments, names among its bases an expression whose last name or attribute is `BundleReader`;
  - (iii) no statement assigns to, or deletes, an attribute of an expression that is, or whose last name or attribute is, a gate name, `bundle_read` or `battery_float`, or of any name the file binds to the module `joulewise.bundle_read` or `joulewise.battery_float` (the full dotted name included). No call of `setattr`, `delattr` or `object.__setattr__` has such an expression as its first argument.
  - 51 (h) gains: a patch through a helper that receives the module or class as a value bound elsewhere (`replaced(module, **kw)`, `scripts/sample_quiet_predicate_evidence.py:541`), and a name built at run time."
- **Test rows.**
  - R57-11b: V1 to V5 → each fails, naming the store, the call or the base. Counterfactual: 57 (b) 1 as ruled, executed silent on the judge's `rules60.py` (F1).
  - R57-12b (behaviour, placed beside R57-12): the charging bundle, `battery_float.authenticate_bundle` patched inside the test → `BundleReader(b).trace_rows()` returns rows. This asserts that the hole is real, so R57-11b is known to guard something. Executed (F2).

#### B-3 (SHOULD-FIX). The reader can be re-pointed after its gate passes. 57 (b) 4 guards `_cache` and not `_path`.

- **The problem.** The gate passes on a bundle A. Then `r._path = B`, and `r.trace_rows()` returns the rows of B, a charging bundle. Executed (E12). This is silent under all three ruled rules (F1, V6).
- **Cost.** GREEN on the tree:
  - `_path` is written only at `bundle_read.py:419` (`__init__`), per F3;
  - outside that file the only `_path` attributes are 12 on `self` inside `RunBundleWriter` in `bundle.py`;
  - the two string constants `"_path"` are parts of f-string keys, not arguments to `setattr` (E14).
- **Replacement text**, a new 57 (b) 4 (v): "`self._path` is assigned only in `BundleReader.__init__`. Outside `joulewise/bundle_read.py`, no attribute named `_path` is assigned or deleted on a receiver other than `self`, and no call of `setattr`, `delattr` or `object.__setattr__` has the string constant `"_path"` as its second argument. (A class that derives from `BundleReader` is already forbidden by (b) 1 (ii), so a `self._path` there cannot arise.)"
- **Test row.** R57-6c: V6 → fails, naming `r._path`. Counterfactual: 57 (b) 4 as ruled (executed silent, F1). Behaviour companion: E12.

#### B-4 (SHOULD-FIX). The two `envelope_gate.py` rows are classed `non_claim` (ii), whose condition is false. This contradicts amendment 60's own title.

- **Why (ii) is false.** 51 (f) defines a claim artifact as a file a paper number is taken from **or licensed by**. AP-5 says:
  - "envelope-validation smoke gate must pass before any scored campaign" (`docs/contracts/analysis_plans.md:270`);
  - "Failed envelope validation … gives `not estimable`/L1" (`:277`).

  So the envelope verdict licenses AP-5 numbers, and it is a claim artifact. `_level_window_energy_records` writes energy into it (`calibration_evidence_only.level_window_gross_energies_j`). Clause (ii) ("nothing the function returns or writes is consumed by a claim artifact") is therefore false.
- **Why 60 (c) 1 does not catch this.** It pins "no tracked **code** reads the verdict". That is true (F3), but it is not the class condition: the licensing reader is a contract row, not code. The ruling's own disclosure (§0 item 2) says a campaign using the envelope gate is queued.
- **No energy leak.** The energy in the verdict is gated in fact, through the callee (the ruling's Y11, pinned by R60-3). This is a false classification in the exemption list, not a leak.
- **Replacement (recommended).** Rule a **production change**, with this reason: it is the only way these two reads can carry a class whose condition is true.
  - In `joulewise/envelope_gate.py`, add `reader.metadata()` on the same name immediately before each `reader.raw_summary()` (`:133`, inside the comprehension; `:654`, the first statement of the loop body).
  - This is **behaviour-identical** on every input. Every reader that reaches `:133` already passed `metadata()` in `_manifest_record` (`:100-107` return `_refused` otherwise). `metadata()` memoises on success, so the new calls return the cached dictionary. A refusal or custody failure cannot newly arise at these lines.
  - The detector then sees a dominating reader-form gate bound to the same name, and both rows leave the allowlist.
  - Put it in lane BFGS-ENVELOPE-REASON-01, beside the reason-code fix, and order that lane **before** S1's allowlist closes.
  - Keep R60-3 and R60-4. They stay GREEN across the change.
- **Fallback, if the lane cannot precede S1.** Keep the rows under (ii) only with a reason that states the truth: "the verdict licenses AP-5 (`analysis_plans.md:270, 277`) and is a claim artifact; the energy it carries is gated in the callee `_manifest_record` (R60-3); held under (ii) until lane BFGS-ENVELOPE-REASON-01 lands, by the cold gate's explicit exception". An exception to a class condition needs the cold gate's words. It must not be read out of amendment 60.
- **Test row.** R60-6: after the lane, the tree → no allowlist row for `envelope_gate.py`. Counterfactual: the lane's edit reverted (the rows return). NOT EXECUTED (the edit does not exist).

#### B-5 (SHOULD-FIX). The caller checks count calls only, the RSW-1 defect in another place.

- **The problem.** Two checks count calls and nothing else: 60 (c) 2 (`callers = ()`: "no call of the function's name") and the callers form of `behind_gate` (51 (f) as amended by 59 (b): "every call of the helper's name"). A new production caller that takes the function as a value (`rows = list(map(extract_rows, …))`, or `f = derive_idle_mean_uncertainty` then `f(r)`) passes both checks. That is exactly the defect the ruling upheld in RSW-1.
- **Cost.** GREEN on the tree: F3 finds no non-callee reference to any helper named in a callers row or a `callers = ()` row.
- **Replacement text** in both places: "every call of the function's name, and every **reference** to it (a name or attribute of that name used where it is not the callee of a call, other than its own definition), by bare name or as an attribute".
- **Test row.** R60-2b: `scripts/make_figures.py` with `rows = list(map(extract_rows, [runs_root]))` added to `main` → fails, naming `main`. Counterfactual: 60 (c) 2 as ruled. NOT EXECUTED as a mutation; the tree scan is executed (F3).

#### B-6 (NIT). 58 (f)'s capture regex misses the post-run idle capture.

- **The problem.** `^(raw/)?(powermetrics(_idle)?\.plist|…)$` does not match `powermetrics_idle_post.plist`, so `RAW_IDLE_POST_NAME` (`adapters/powermetrics.py:53`) is not a capture name. Today every reader of that file also names `RAW_IDLE_NAME` and is among the 48 (F4). A future function that reads only the post-run capture would be silent.
- **Replacement:** `^(raw/)?(powermetrics[A-Za-z0-9_]*\.plist|nvidia_smi[^ /]*\.csv)$`. The seat reports whether the count moves from 48 (NOT EXECUTED under the ruling's resolver).

#### B-7 (NIT). Wording in 57 (b) 4.

- (ii) says "the assignment of an empty dictionary to `self._cache` in `__init__`". The tree uses an **annotated** assignment (`bundle_read.py:420`). The judge's prototype accepts both forms, but the text should say "an assignment or annotated assignment".
- 51 (h) should also gain "`_cache` or `_path` named by a string built at run time".

#### B-8 (NIT). R57-12 pins the subclass hole as expected behaviour.

A later production hardening would turn R57-12 RED: for example, the four gated energy accessors calling `BundleReader.metadata(self)` instead of `self.metadata()`, which would close the subclass and `type()` doors in the code itself. Append to R57-12: "If a production change makes this row RED by closing the hole, the row is replaced by its negation under a cold gate; the change is not reverted."

#### B-9 (NIT). The envelope `output_marker` is one string.

A reader could key on the verdict's content without the schema string. If B-4's fallback is used, the marker becomes the set {`envelope_gate.v1`, `envelope_validated`, `envelope_failed`, `calibration_evidence_only`, `level_window_gross_energies_j`}. It is GREEN on the tree (F3). `bundle_refused` is excluded because `determinism_gate.py:28` uses it for its own verdict.

### B.3 Answers to the four questions

- **Is the ruling wrong or incomplete?**
  - **Incomplete:** B-1, B-2, B-3 and B-5.
  - **Wrong in one classification:** B-4, where `non_claim` (ii) is held against its own condition under 51 (f)'s definition and AP-5.
  - Its rulings on RSW-2, RSW-5 and RSW-7 against the first refuter are **right**, and stronger than Section A's proposals for RSW-7.
- **Can a new function still claim a gate or a class by name alone?**
  - The classes: no. `gate_body` is closed by 57 (b) 1, 2 and 6. `tolerant_definition` is closed by 57 (d), now with references.
  - The gate: its **name** can no longer be rebound in any form the ruling lists. But its **behaviour** can still be replaced while every name stays correct: through the verdict source (V1, executed), the module written in full (V3, V4), and a `type()` subclass (V5, executed). That is B-2.
- **Does any ungated energy read survive?**
  - Not one that reaches a claim artifact at `cbfa9dc3`.
  - Silent latent paths remain, each executed or shown silent on the judge's own prototypes: reads in unswept scopes (B-1), the reader re-pointed by `_path` (B-3), the patched verdict source (B-2), and the envelope rows' energy, gated only in a callee and held under a false class (B-4).
- **Do the restated amendments contradict each other, or the invariants the charge keeps?**
  - 57 (d) 5's `<module>` references and 58 (f) 3's "nested functions" assume a scope coverage that the detector of 51 does not have (B-1).
  - Amendment 60's title ("a class is held only where its condition is true") is contradicted by its own 60 (b) for the envelope rows (B-4).
  - No contradiction with the kept invariants. Custody stays an exception (R57-9, R60-4). No amendment reorders authentication before exclusion. The frozen files are parsed and not edited. No consumer gains a `battery_float` import (B-2's V1 is a test-side patch in a non-consumer source).
  - B-4's recommended closure is a production change, flagged as such, with its reason and its behaviour-identity argument.

### B.4 Verdict counts (Section B)

- BLOCKER: 0.
- SHOULD-FIX: 5 (B-1, B-2, B-3, B-4, B-5).
- NIT: 4 (B-6, B-7, B-8, B-9).
