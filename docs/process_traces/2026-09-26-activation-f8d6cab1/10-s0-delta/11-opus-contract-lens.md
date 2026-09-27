# BFG-S S0 delta re-audit: CONTRACT lens (Opus 5.5), candidate `783a09be`

Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), fresh session, READ-ONLY on the repository (WRITE_SCOPE `[]`).
- **Worktree:** `JouleWise-wt-s0delta-opus-f8d6cab1`, detached at `783a09be`, clean at start and at end.
- **Scratch work:** in `/tmp/opusdelta/` only. Mutation runs used a `git archive 783a09be` copy at `/tmp/opusdelta/tree`, and each was restored afterwards (`git status --short` empty).
- **Contamination:** the harness loaded the global and project `CLAUDE.md`, the private `CLAUDE.local.md` and the memory index. I opened no memory file, `RUN_STATE.md`, `TASK_QUEUE.md` or decision log. I read only the authorities the charge names, the lens reports 31, 32 and 33, and seat reports 43 and 46.

## Verdict

**PASS WITH FINDINGS: 0 BLOCKER, 2 SHOULD-FIX, 9 NIT.**

- **Closures.** Every C1–C13 closure, and every addendum-2 amendment in S0 scope (20–25, 27, and 28's scope clause), is **CLOSED** by executed evidence. None is OPEN or REGRESSED.
- **Freeze fence.** Verified independently from the base file: all 39 closure definitions are byte-identical to main `5d5a0b75`, decorators included, and all 39 pins equal the base hashes I recomputed.
- **Same signature: no.** No input turns a custody failure or a non-pass status into `pass`.
- **Scope.** Nothing outside S0's WRITE_SCOPE moved.
- **Both SHOULD-FIX findings are gaps in guard mechanisms, not in the candidate's behaviour:**
  - the C7 pin mechanism cannot see decorator edits or nested rebinding;
  - the C8 guard misses `copy.replace`, the stdlib twin of `dataclasses.replace`.

## Executed evidence (this session)

| # | Probe | Result |
|---|---|---|
| E1 | `python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep` at `783a09be` | `Ran 120 tests in 210.773s` / `OK` |
| E2 | `python3 -m unittest tests.test_evidence_night tests.test_night_kinds` at `783a09be` | `Ran 181 tests in 696.096s` / `OK` |
| E3 | `git diff --stat 5d5a0b75 783a09be` | 8 files, all in the S0 WRITE_SCOPE (text E): `battery_float.py`, `evidence_night.py`, `night_kinds.py` and the five S0 test files. The bench commit touches `battery_float.py` and `tests/test_battery_float.py` only. Round 3b touched `tests/test_battery_float_consumers.py` only. |
| E4 | `git show --remerge-diff ac424c0d` | Empty: a clean merge with no conflict resolution content. |
| E5 | `/tmp/opusdelta/pins.py` (recomputes the pins from `git show 5d5a0b75:joulewise/battery_float.py`) | The closure has 39 members at base, 39 at the candidate and 39 in the table, and the three sets are equal. Every table pin equals the base hash. Every candidate segment equals the base segment. A decorator-inclusive comparison of every member is identical. `CustodyFailure` = `af27587c…` and `load_committed_verdict` = `43900752…` at both base and table. |
| E6 | Same script: the global names each frozen closure function resolves at runtime, base module against candidate module | No difference, apart from the module `__name__` artefact of loading the two copies under different names. The new `os` and `stat` imports, and every new top-level name, are referenced by no frozen code. |
| E7 | `/tmp/opusdelta/cmp.py`: every pre-existing top-level definition, decorator-inclusive | `64e39bb9→aa90f349`: only `CustodyFailure` changed. `64e39bb9→980138c7`: only `CustodyFailure` changed. `5d5a0b75→783a09be`: none changed and none removed. `git diff 5d5a0b75 783a09be -- joulewise/battery_float.py` has 0 deleted lines. |
| E8 | Consumer grep for `.failures` and `custody failure:` | Production consumers of `CustodyFailure` are `authenticate_committed_verdict` (`battery_float.py:731`, uses `.detail`) and `issue_calibration_acceptance_generation.py:1634` (uses `.detail` and adds its own prefix). `.failures[0]` is read only in tests, on list-form raises from `validate_window` or `authenticate_pair`. No production code calls the S0 wrappers, so `CustodyUnreadable` reaches no existing consumer. No string-form `CustodyFailure(` raise remains anywhere in `joulewise/` or `scripts/`. |
| E9 | `/tmp/opusdelta/sig_probe.py` and `closure_probe.py` | The same-signature and closure matrix below. |
| E10 | C10 mutation runs in `/tmp/opusdelta/tree` | M1 adds `"battery_brackets"` to the exemption tuple: guard `FAILED (failures=1)`. M2 writes a `skipped` row: `FAILED (errors=1)`. M3 makes the unreadable-kind branch `skipped`: `FAILED (failures=1)`. M4 reverts C5 to `row.battery_brackets`: `FAILED (errors=1)`. All four restored. |
| E11 | C8(ii) allowlist mutation runs in `/tmp/opusdelta/tree` | (a) A new `replace(v, status="pass")` in `night_gate.py`: both the inventory test and the tree guard go RED. (b) The allowlisted `replace(probes, run=first_census)` removed from `run_night.py`: the inventory test goes RED. (c) A textually identical second call in the same function: the inventory test goes RED through the `Counter` comparison. All restored. |
| E12 | `/tmp/opusdelta/guard_probe.py` | See findings S-2 and N-2. |
| E13 | Pin-mechanism mutations in `/tmp/opusdelta/tree` | See finding S-1. |

## Closure table

| Item | State | Evidence |
|---|---|---|
| **C1** unreadable round journal | CLOSED | A digest-mismatch journal raises `CustodyFailure`. The same file becomes `{`, `[]`, whitespace, a directory, non-UTF-8 or a dangling symlink, and each raises `CustodyUnreadable: round journal unreadable`. A row `{"raw": null}` raises `CustodyFailure` (Astra R1's `AttributeError` is gone). A missing or empty journal gives zero rows, as dictated, and the raw custody check still fires: a deleted journal plus a tampered raw raises. Tests: `test_round_journal_mismatch_and_malformed_both_raise` and `test_unreadable_round_journal_refuses`. |
| **C2** spans | CLOSED | Under ADD2, `(80,20)`, `42`, `(True,80)` and `(20.0,80)` each give `quiet span unavailable`. Amendment 22's wording `<kind> span unavailable` correctly supersedes C2's "span malformed", because the addendum takes precedence. `span=None` for quiet or bundle raises `ValueError("<kind> pairs owe a span")` per amendment 22, which supersedes C2's status form. A bundle with `span=42` and a deleted post raw raises `CustodyFailure`, not `TypeError`. The span rung sits after custody, probe, parse and predicate (one subtest per rung). |
| **C3** symlinks | CLOSED | An outside symlink with matching bytes raises. A `raw/` directory symlinked to an in-container copy also raises `CustodyUnreadable: raw path traverses a symlink` (E9). Every component is checked with `lstat`, the resolved path must stay inside the container, and the file is opened with `O_NOFOLLOW`. |
| **C4** duplicate keys | CLOSED | Top-level duplicates raise in all five inputs (test). A duplicate *nested* `metadata.monotonic_ns` in `events.jsonl` raises `CustodyUnreadable` (E9). `CustodyUnreadable` is a `RuntimeError`, so the `(OSError, ValueError)` handlers never swallow it. |
| **C5** fence with a missing flag | CLOSED | `getattr(row, "battery_brackets", None) is not True`. The injected attribute-less kind journals a `fail` row. Mutation M4 turns the test RED. |
| **C6** stale `check.json` | CLOSED | `require_fresh_check` requires a `battery_brackets` row whose verdict is `pass`, and refuses otherwise with the dictated text. There is a test for it. |
| **C7** dependency-closure pins | CLOSED as dictated | The 39-member closure is pinned by `ast.get_source_segment`, and the `_signed` self-test is present. The mechanism has two blind spots (S-1). |
| **C8** guard evasions (i)–(iv), amended by R-F1 | CLOSED as dictated | All four E7 forgeries are flagged, and `isinstance`/`issubclass` stay clean. The allowlist is content-keyed on `(path, qualname, ast.unparse)` and is shrink-only: an exact `Counter` match plus `len == 9` (E11). The nine reasons are verbatim, and the seat quoted type evidence per site. `copy.replace` evades (S-2). |
| **C9** exit code | CLOSED | `False` and `0.0` give `probe failed`. `timed_out` is still tolerated when absent (N-4). |
| **C10** fence guards (R-F2) | CLOSED | Three baseline-green guards. My own mutation runs turn each RED (E10). The exemption guard is textual (N-1). |
| **C11** `PHASES` sweep aliases | CLOSED | All three dictated alias forms are visible. The relative-import form is not (N-3). |
| **C12** ADD2 Q2 (amendments 24, 25) | CLOSED | `bundle_sha256` is the last field, set by `dataclasses.replace` after `authenticate_pair` for every status. It equals `complete_bundle_sha256` computed independently. A bundle containing a symlink raises the digest function's own `ValueError("not a regular file")`. Quiet and capture carry `None` (both asserted). The two factories exist and the guard exempts only `bundle_read.py`, which is one row. The import is local (the comment is missing, N-7). |
| **C13** ADD2 Q3 (amendment 27) | CLOSED | The E6 shape gives `('pair identity disagreement', 'attempt identity mismatch')`. The attempt-mismatch, partial, ledger-mismatch and missing-`validation_id` cases each give their ruled reason, in the ruled order. The ordinary null-identity shape passes. `expected` is not validated for its key set (N-5). |
| **Amendment 20** (S0 clause) | CLOSED | `monotonic_ns_from_s` is `floor(s·1e9)` and refuses bool, NaN, ±inf and negatives. `QUIET_REFUSAL_ERROR_CLASS == "network_time_provenance"`, which equals the collector's `NETWORK_TIME_REFUSAL` (`scripts/sample_quiet_predicate_evidence.py:86`). The S2 clause is out of scope. |
| **Amendment 21** | CLOSED | A refusal-shape envelope passes. A capture shape without `end_stamp`, and a refusal shape with a row, each give exactly `('quiet span unavailable',)`. A refusal shape with `rounds.jsonl` missing gives `quiet span unavailable` (E9). An overflowing `1e300` stamp gives unavailable. |
| **Amendment 22** | CLOSED | See C2. The span check never raises and is applied to every kind: capture with `span=42` gives `capture span unavailable`. |
| **Amendment 23** | CLOSED | Each gives `pair stamps malformed`: a negative stamp, a boolean stamp, a float stamp, a post stamped before pre, and an inverted probe duration. Every fixture pair still passes. |
| **Amendment 25** | CLOSED | See C12. The `parse` allowlist has exactly seven rows. |
| **Amendment 28** (S0 scope) | CLOSED | No path added (E3). The `observe` golden is byte-identical at `26ab7234` and `783a09be` (sha256 `e6efa8ae…`). Of the ten root pins, only `load_committed_verdict` differs from `26ab7234`, and that is main's A309 change (`git diff 64e39bb9 5d5a0b75`). The fix contract assigned that recompute to the lead bench. |
| Amendments 26 and S1/S2 clauses | Out of scope | S0 touches none of them. |

## Same-signature statement (mandatory)

**Same signature: no.** No input that S0 reads converts a custody failure into `pass`, or a non-pass into `pass`. Matrix (E9):

| Input path | Malformation × custody defect | Outcome |
|---|---|---|
| `rounds.jsonl` | malformed, non-object, whitespace, directory, non-UTF-8, dangling symlink; digest mismatch; `raw` null or list | raise (`CustodyUnreadable` / `CustodyFailure`) |
| `rounds.jsonl` | deleted (capture shape) plus a tampered raw | raise `CustodyFailure` |
| `session.json` | duplicate key | raise |
| `session.json` | trailing garbage plus a tampered raw | `evidence_missing` (phase not recorded) |
| `end_stamp` / `start_stamp` | malformed, overflowing, reversed, boolean, plus a tampered raw | the raise preempts; without a tamper, `quiet span unavailable` |
| `events.jsonl` | malformed line plus a tampered raw | raise `CustodyFailure` |
| `events.jsonl` | malformed line alone | `bundle span unavailable` |
| `metadata.json` | garbage plus a tampered raw | `evidence_missing` |
| `instrument_evidence.json` | duplicate key | raise |
| raw ioreg | missing, directory, symlink (file or directory), appended byte | raise |
| monotonic fields | bool, float, negative, inverted | `pair stamps malformed` / `span unavailable` |

The weaker form, custody downgraded to a *non-pass status*, occurs in exactly two places, and both are ruled.

1. **An unparseable record container.** `session.json`, `metadata.json` or `instrument_evidence.json` cannot be parsed, so no reference digest exists. Text 2(a) makes this `evidence_missing`. Every consumer then refuses or blanks:
   - text 6: an unreadable envelope yields no number;
   - text 8: `BundleReadError`;
   - text 10: the ledger's `instrument_evidence.json` digest check runs first and raises `CustodyFailure` on altered bytes;
   - text 11: the attachment is refused.
2. **A rung-(a) fault in the same phase as a tampered raw.** An example is `wall_time_s = "x"` or a wrong `phase` lexeme, which gives `evidence_missing`. This is the ruled T2 order (structure → custody), pinned since round 1 by `test_structure_is_checked_before_raw_custody`, and it mirrors frozen `validate_window`. For capture, the rung-(a) edit alters `instrument_evidence.json`, which text 10's ledger digest already refuses as custody; the quiet and bundle consumers blank or refuse.

Neither reaches a number. I record (2) for the magistrate as a property of the ruled text, not as an S0 defect.

## Freeze-fence verification (charge item 3)

- **Frozen-root closure.** Every definition in the `FROZEN_ROOTS` transitive closure (39 members) is byte-identical between `git show 5d5a0b75:joulewise/battery_float.py` and `783a09be`. I checked the pin segments and also the decorator-inclusive segments (E5).
- **Pins.** Every pin equals the hash I recomputed from the base file (E5), including `CustodyFailure` `af27587c…` and `load_committed_verdict` `43900752…`.
- **No shadowing.** No frozen function resolves a global differently at the candidate (E6).
- **The round-3 breach, confirmed and cured.**
  - Rounds 3 and 3b edited exactly one pre-existing definition, `CustodyFailure.__init__` (widened to accept `str`), and no other definition, frozen or not (E7).
  - The bench commit restores it to 0 deleted lines against main.
  - `CustodyUnreadable(CustodyFailure)` carries the five string-detail raises: one duplicate-key raise, three symlink raises and one journal raise.
- **Consumer dependence.** No production consumer depends on `.failures` being non-empty or on the `custody failure:` prefix; both use `.detail` (E8). `CustodyUnreadable` is still not a `ValueError` or `OSError`, so no `evidence_missing` handler swallows it (bench test plus E9).

## Guards (charge item 4)

- **`REPLACE_CALL_ALLOWLIST`.**
  - It is content-keyed on `(repo-relative path, enclosing qualname, ast.unparse(call))`, with no line numbers.
  - It is exact: the `Counter` of production sites must equal the keys, and `len == 9`.
  - It is therefore shrink-only, and adding, removing or duplicating a call turns it RED (E11).
  - I spot-checked the type evidence: `night_gate._finish` returns `Receipt` (`night_gate.py:764`), `run_night.make_probes() -> Probes` (`:401`), and `night_gate._run(...) -> ProbeResult` (`:660`).
- **C10 guards.** Each of the three R-F2 guards has a mutation proof that turns it RED, reproduced independently (E10: M1, M2, M3). C5 also turns RED when reverted (M4).

## Findings

### S-1 SHOULD-FIX: the C7 pin mechanism cannot see decorator edits or nested rebinding of closure members

**Where.** `tests/test_battery_float.py::S0FreezeTests.test_frozen_function_sources_match_base`.
- Non-root members are hashed with `ast.get_source_segment(source, node)`. For a `ClassDef` or `FunctionDef`, that segment starts at the `class`/`def` line and excludes the decorators.
- `definitions` is built from `tree.body` only, from direct `Assign`/`AnnAssign`/`def`/`class` children. It never checks that the runtime binding is that node.

**Executed (E13, in `/tmp/opusdelta/tree`, restored afterwards).**
- Changing `@dataclasses.dataclass(frozen=True, slots=True)` above `class AuthenticatedVerdict` to `frozen=False` leaves the pin test `OK`, and `AuthenticatedVerdict.__dataclass_params__.frozen` is now `False`.
- Appending `if True:\n    def _is_sha256(value): return True` leaves `S0FreezeTests` at `Ran 4 tests … OK`, and `battery_float._is_sha256("zz")` is now `True`.

**Why it matters.** Text 3 says these definitions "do not change before S4". C7 was ruled to make that true of the dependency closure (prior Opus S-1). `AuthenticatedSlot` and `AuthenticatedVerdict` are the frozen consumer-facing verdict types, and a one-keyword decorator edit makes them mutable with the fence green. The candidate itself is clean (E5 checks decorator-inclusive bytes), so this does not block S0's correctness. It is the backstop for every later PR, and S4 is the next PR allowed to touch the file.

**Exact fix (lead bench, test-only).**
1. Hash every `FunctionDef`/`ClassDef` member from its first decorator line: `lines[min([n.lineno] + [d.lineno for d in n.decorator_list]) - 1 : n.end_lineno]`, or `inspect.getsource(getattr(battery_float, name))`, which includes decorators.
2. For every closure name, require that the module binds it exactly once anywhere in the tree. Walk the whole module for `Store` targets, `def`/`class`, `import … as`, `global`, `AugAssign` and walrus.
3. For function and class members, also require that the runtime object's `inspect.getsource` digest equals the pin.
4. Regenerate from base `5d5a0b75` only. Only the digests of the decorated classes move (`AuthenticatedSlot`, `AuthenticatedVerdict`).
5. Add the two mutations above as self-tests.

### S-2 SHOULD-FIX: C8(ii) misses `copy.replace` and `__replace__`, the stdlib twins of `dataclasses.replace`

**Where.** `tests/test_battery_float_consumers.py::_Checker.visit_Call` matches only `dataclasses.replace`, however imported.

**Executed (E12, on Python 3.14.7, the interpreter in use).** In `joulewise/x.py`, each of the following returns `violations == []`:
- `import copy; copy.replace(v, status='pass', reasons=())`;
- `from copy import replace; replace(v, …)`;
- `v.__replace__(status='pass', reasons=())`.

The control `dataclasses.replace(v, status='pass')` is flagged. At runtime, `copy.replace(confounded_verdict, status="pass", reasons=())` returns `PairVerdict(kind='quiet', status='pass', reasons=(), …)`.

**Why it matters.** Prior Opus S-2 named `copy.replace` in its fix. Contract C8(ii) narrowed the rule to `dataclasses.replace`, so this is a contract gap, not a seat defect. On Python ≥ 3.13, `copy.replace` is as idiomatic as the call C8 was written to catch, and it is the same one-line status forge.

**Exact fix.**
- In `visit_Call`, treat as a `dataclasses.replace` site any call to `replace` imported from `copy`, any `<copy alias>.replace(...)`, and any `<expr>.__replace__(...)`. Scope and allowlisting stay as they are.
- `grep -rn "copy\.replace\|from copy import\|__replace__" joulewise scripts` finds only `deepcopy` imports (`controller.py:60`, `reissue_calibration_acceptance.py:14`), so no allowlist row is needed.
- Add the three forms to `test_pair_verdict_forgeries_are_flagged`.

### N-1 NIT: the C10 exemption guard is textual

`test_battery_brackets_has_no_skipped_state_or_exemption` asserts `'name in ("machine_quiet", "corecaptured")'` is present and the three-name tuple is absent.

**Executed.** Rewriting the filter as `((name in ("machine_quiet", "corecaptured") or name == "battery_brackets") and c["verdict"] == "skipped")` keeps the guard `OK`. This is inert on its own. Combined with a `skipped` QPE row, it is caught by the other tests (`test_qpe_candidate_is_not_armable_before_s2` and the guard go RED).

**Fix.** Make it behavioural: patch `inspect` so that `battery_brackets` records `skipped`, and assert that the check is not armable and that `battery_brackets` is in the refusal text.

### N-2 NIT: guard forms beyond C8's four dictated forms

All of these give `[]` (E12):
- a walrus inside the `isinstance` second argument (`isinstance(v, (P := bf.PairVerdict)); P(...)`), because the whole subtree is exempt;
- a constructor embedded in an annotation;
- `from joulewise.battery_float import *`;
- module rebinding (`m = battery_float; m.PairVerdict(...)`);
- `object.__setattr__(copy.copy(v), "status", "pass")`, which works at runtime on the frozen, slotted class.

These are adversarial rather than accidental, so under D-161 they are a NIT.

**Fix (if wanted).**
- Exempt only `Name`, `Attribute` and `Tuple`-of-those nodes in the `isinstance` argument and in annotations.
- Flag star imports of the module.
- Add simple `x = <module alias>` to `module_aliases`.

### N-3 NIT: the `PHASES` sweep does not resolve relative imports

**Executed.** `_observe_phases("joulewise/x.py", "from . import battery_float as bf\nbf.observe(phase='unknown')\n")` returns `[]`. The consumer guard already resolves this form through `_absolute_module`. No production module uses it today.

**Fix.** Resolve `ImportFrom` through `_absolute_module(relative, node)` in `_observe_phases`.

### N-4 NIT: rung (c) accepts a record whose `timed_out` key is absent

**Executed.** With `post.timed_out` deleted, the verdict is `pass`. `observe` always writes a bool (`battery_float.py:354`), so no genuine record is affected.

**Fix.** Use `… or stored.get("timed_out") is not False`.

### N-5 NIT: `authenticate_capture(expected=…)` does not enforce "keys exactly"

**Executed.** An extra key is accepted and gives `pass`. A missing key raises a bare `KeyError: 'session_id'`, which is neither a status nor a `ValueError`. Amendment 27 says the keys are exactly `attempt_id`, `session_id` and `slot`.

**Fix.** Add `if expected is not None and set(expected) != {"attempt_id", "session_id", "slot"}: raise ValueError("expected identity keys")`.

### N-6 NIT: `CustodyUnreadable` drops the `custody failure:` prefix from `str(exc)` and carries `failures == []`

No current consumer is affected (E8). Text 12 has S1 consumers "naming the member", so their messages must be built from `.detail`.

**Fix.** Either `RuntimeError.__init__(self, f"custody failure: {detail}")`, with the bench test's `str(exc)` expectation updated, or one sentence in the S1 brief: "report `CustodyFailure` via `.detail`; `.failures` may be empty".

### N-7 NIT: the local import in `authenticate_bundle` does not carry the comment naming the cycle

Addendum 2 §3 Q2.1 asks for "a comment naming the cycle".

**Fix.** Put `# local: module-level import cycles detection_floor → calibration_bracketing/whole_window → battery_float after S1` above the import.

### N-8 NIT: the C8(ii) self-test clause (c) is near-tautological

The test asserts that `assertEqual(Counter([]), Counter([site]))` raises; it never exercises the production inventory comparison with a stale row. The real inventory test does go RED on a stale row (E11(b)).

**Fix.** Factor the comparison into a function `_replace_inventory_mismatch(sites, allowlist)` and self-test it with a nine-row allowlist plus one stale row.

### N-9 NIT (forward note for S1): `events.jsonl` leniency

`authenticate_bundle` treats a syntactically malformed `events.jsonl` as zero events, giving `bundle span unavailable`, which is safe here. It silently skips non-object lines. Texts 7 and 8 make the S1 reader decide `not_reached` (no obligation) from the same file. If S1 parses it with the same leniency, a malformed `events.jsonl` would read as "no `idle_baseline` start", which means no obligation. That is this round's blocker signature, moved one layer up.

**Fix.** The S1 brief states that a present but malformed `events.jsonl` (any non-object or unparseable line) is `BundleReadError`, never `not_reached`, and T8 gains that row.

## Line-by-line conformance with no finding

- **Text 2.**
  - Rungs (a)–(f) are in order, and custody raises before any status.
  - `identity_reasons` is a keyword-only addition to the ruled signature. It can only add reasons, so it cannot produce `pass` from a non-pass.
  - Confounded ranks above `evidence_missing`, which ranks above `pass`.
  - The stored `passed` value and the stored charge delta are never read.
- **Texts 15 and 17, T3 and T4.** Unchanged since `26ab7234` and still green. The calibration row is `True` and the QPE row `False`, the fence placement is unchanged, and the staleness pin still passes a future `UpdateTime` today.
- **Environment.** The seat's V3 live-probe failure is a sandbox limit, not a finding.
