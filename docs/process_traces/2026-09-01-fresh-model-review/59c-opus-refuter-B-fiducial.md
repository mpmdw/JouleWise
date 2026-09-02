# 59c — Opus 5 contract-lens refuter, cold gate #3 Packet B (fiducial receipt inventory)

Seat: Opus 5, read-only, paired with the cold Fable seat (verdict 59b). Packet: `59-COLD-GATE-3-packet.md` §Packet B. Raw report follows.

---

# Cold gate #3 — Packet B, Opus contract-lens refutation

Read-only. No file in `/Users/edr/code/JouleWise` or `/Users/edr/code/JouleWise-wt-fiducial` was edited; all scripts written to scratchpad. Branch head confirmed `a7a2917c`. Python 3.14.7.

---

## 1. Bench reproduction — the packet's central fact

Script: `/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/bench_trace.py`. Four modes: **A** = the test's own `_trace_joulewise_execution` (`tests/test_transfer_fiducial.py:408-474`, which prefers `sys.monitoring` LINE events); **B** = pure `sys.settrace` call-event collector; **P** = mode B with the packet's stated four pre-imports; **C** = mode B with `pkgutil.walk_packages` over the whole package.

```
$ for m in A B P C; do python3 .../bench_trace.py $m; done
MODE A verdict fitted count 22
MODE B verdict fitted count 22
MODE P verdict fitted count 7
   joulewise/adapters/powermetrics.py   joulewise/authentication_io.py
   joulewise/bundle_read.py             joulewise/powermetrics_fiducial.py
   joulewise/transfer_fiducial.py       joulewise/uncertainty_evidence.py
   joulewise/validation.py
MODE C usage: joulewise [-h] {validate-config,...}
      joulewise: error: argument command: invalid choice: 'C'
```

**"7 runtime modules": CONFIRMED, exactly.** Mode P reproduces the packet's seven-member list member-for-member. Mode C (whole-tree pre-import, after skipping `__main__` — see §3) also yields **7**, so the number is stable across two independent normalisation strategies. Determinism check: mode B run three times → 22, 22, 22.

**"Order-dependent": CONFIRMED, and stronger than the packet states.** `order_demo.py` runs the same `fit_run` on the same fixture, varying only what the process imported first:

```
--- nothing extra (what luna's test does)
pre-imported=0  traced=22  subset_assertion_passes=True
--- + joulewise.suite
pre-imported=1  traced=21  subset_assertion_passes=True
--- + joulewise.bundle_read
pre-imported=1  traced=20  subset_assertion_passes=True
--- + joulewise.adapters.powermetrics
pre-imported=1  traced= 7  subset_assertion_passes=True
--- packet's four
pre-imported=4  traced= 7  subset_assertion_passes=True
```

The decisive form — this is not hypothetical, it is what the repo's own suite does. `tests/test_adapters_powermetrics.py` sorts **before** `tests/test_transfer_fiducial.py`, and imports `joulewise.adapters.powermetrics`. `suite_order.py` runs the test module's own tracer both ways:

```
$ python3 .../suite_order.py alone;  python3 .../suite_order.py with-sibling
alone          observed= 22  subset_assertion_passes=True
with-sibling   observed=  7  subset_assertion_passes=True
```

So luna's 24-entry inventory is an artifact of the *two-module* verification command in the round-2 brief (`python3 -m unittest tests.test_transfer_fiducial tests.test_transfer_fiducial_v2_plan`). Under `unittest discover tests` the same test would have certified **7**. The inventory recorded into a non-reissuable receipt is currently a function of test-runner composition. The drift assertion passes in every one of those cases (`tests/test_transfer_fiducial.py:604-612`, `assertEqual(missing_from_inventory, [])`), and the test itself passes at HEAD:

```
$ python3 -m unittest tests.test_transfer_fiducial.TransferFiducialTests.test_transfer_capture_records_estimator_revision_and_both_magnitudes
Ran 1 test in 30.200s
OK
```

**Two packet errors found here** (detail in §5): the "20–24 modules" range conflates the traced set (22) with the inventory size (24 = 22 traced ∪ `clock.py`, `schemas.py`), and `transfer_fiducial.py:1312` is inside `build_capture` (`:1261`), **not** inside `fit_run` (`:354`) — so `schemas.py` is not "a branch of this path", it is unreachable from the traced entry point at all.

**The entry point is wrong.** The verdict is produced by `build_capture`, not `fit_run` (`capture["verdict"] == "supported"`, asserted at `tests/test_transfer_fiducial.py:616`). Tracing `build_capture` under full pre-import (`capture_trace.py`):

```
build_capture traced: 8 verdict: supported
    adapters/powermetrics.py  authentication_io.py  bundle_read.py
    powermetrics_fiducial.py  schemas.py            transfer_fiducial.py
    uncertainty_evidence.py   validation.py
executed but not in inventory: []
in inventory but never executed by build_capture: 16 paths (the 15 import-closure
  entries + joulewise/clock.py)
```

The verdict-producing set is **8**. `clock.py` executes **zero** lines on either entry point.

---

## 2. Contract check — `docs/contracts/transfer_fiducial.md` on the branch

**Does it state what the receipt's inventory fences?** Partly. `:220-221`: *"the exact-byte SHA-256 value of `scripts/fit_transfer_fiducial.py` and a source inventory for the fit program"*. `:230-244` then enumerates all 24 paths verbatim (I verified mechanically that the contract list and `RECEIPT_SOURCE_MODULES` at `joulewise/transfer_fiducial.py:58-83` have identical membership: `code 24 doc 24 / code-only [] / doc-only []`). The purpose sentence at `:252-256` is good and meets the standard: *"an edit to `uncertainty_evidence.py` on the day after the receipt is issued could change the metrology standard-error term `se_metrology` used for validation without changing the old receipt, so the receipt would no longer identify the program that fit the data."*

**Does it state how it is closed?** `:247-252`: *"The inventory is closed by execution: the regression runs the one fixture fit while recording every `joulewise/` file for which at least one source line executes, and asserts that this observed set is a subset of the tuple; it also asserts that every listed path exists and that no path is duplicated. This is an execution check, not a transitive import-graph walk."*

**Does it state when the fence closes?** Yes, correctly — `:256-258`: *"The inventory fence closes before the first receipt is issued, not before the first fit; receipt publication is create-new and a receipt is not reissued after data."* Corroborated in code: `scripts/fit_transfer_fiducial.py:30-31` refuses `pre_data_receipt_already_exists` on `FileExistsError`.

**Can a reader with only the text predict `adapters/mock_telemetry.py` is in the fence?**

Trivially yes, because it is *enumerated* at `:238`. But that is a list, not a mechanism, and enumeration is exactly what Ed's replication bar excludes: a reader must be able to **rebuild** the fence. Applying the contract's stated mechanism, they cannot:

- (a) The contract never names the fit being traced — no entry point, no fixture path, no command. `fit_run` gives 7 or 22; `build_capture` gives 8. All three are "the one fixture fit".
- (b) The mechanism is stated as `⊆`, so it never determines the tuple. Any superset satisfies it. A reader deriving the tuple from the text has no rule that produces 24 rather than 7 or 8 or 85.
- (c) Executing the stated mechanism the obvious way (whole-suite run, §1) yields **7** — the reader's reproduction disagrees with the enumeration by 15 entries.
- (d) The contract's own justification (`:252-256`, verdict-relevance) argues mock telemetry *out*. Nothing in the text tells a reader that "at least one source line executes" silently includes module-body execution triggered by a lazy import inside the traced region.

**Contract and code disagree, and the disagreement is a false sentence.** `:251-252` — *"This is an execution check, not a transitive import-graph walk"* — is false as implemented. Measured: 22 observed with nothing pre-imported vs 7 with the import closure already resolved, so **15 of the 22 entries are present solely by transitive-import module-body execution**. The check *is* an import-graph walk; lazy imports at `transfer_fiducial.py:364-365` moved the walk inside the traced window. The distinction 42b drew ("closed by execution, not by import graph", `42b:48-50`) is not implementable without an environment-normalisation step that neither 42b nor 48c specified.

**Which is wrong: the code.** Specifically the *measurement* that produced the tuple. The contract's purpose statement, forcing-problem example and fence-closing timing are correct and should survive verbatim. Wrong and to be struck: the 15 import-closure entries in `joulewise/transfer_fiducial.py:67-83` and their mirror at contract `:235-244`, plus the one false sentence at `:251-252`, plus the mechanism sentence at `:247-251` which is too weak to determine anything.

---

## 3. Attack on the magistrate's proposed cure

### 3a. The cure as written does not run

`pkgutil.walk_packages(joulewise.__path__, "joulewise.")` enumerates 84 modules including `joulewise.__main__`, and `joulewise/__main__.py` is four lines:

```
from joulewise.cli import main


raise SystemExit(main())
```

Importing it **runs the CLI against the test process's `sys.argv` and raises `SystemExit`** — a `BaseException` that an ordinary `except Exception` guard does not catch. That is mode C's output in §1: the test harness dies with `joulewise: error: argument command: invalid choice: 'C'`. Beyond the crash, running `cli.main()` inside a test is an arbitrary side-effecting operation depending on argv. The pre-import must be an explicit name list, never a tree walk.

### 3b. Honest edits that still invalidate a receipt under the cure

The cure's 9-module inventory retains whole-file hashing of the two hottest shared modules in the repo. Measured (`linecount2.py`, `sys.monitoring` LINE over `build_capture`, full pre-import), plus 60-day churn on `main`:

| module | executed lines | file lines | frozen-unexecuted | commits/60 d |
|---|---:|---:|---:|---:|
| `joulewise/adapters/powermetrics.py` | 80 | 2278 | 2198 | 27 |
| `joulewise/bundle_read.py` | 45 | 2832 | 2787 | 25 |
| `joulewise/schemas.py` | 221 | 2356 | 2135 | — |
| `joulewise/uncertainty_evidence.py` | 17 | 1447 | 1430 | 9 |
| `joulewise/authentication_io.py` | 9 | 736 | 727 | — |
| `joulewise/powermetrics_fiducial.py` | 261 | 1585 | 1324 | — |
| `joulewise/transfer_fiducial.py` | 507 | 1532 | 1025 | — |
| `joulewise/validation.py` | 9 | 28 | 19 | — |
| `joulewise/clock.py` | **0** | 118 | 118 | 2 |
| **total** | **1149** | **12912** | **11763** | |

**91% of the frozen bytes never execute.** `bundle_read.py` and `adapters/powermetrics.py` alone contribute 125 of 1149 executed lines (11%) while carrying 5110 frozen lines and **52 commits in the last 60 days**. Any one of those 52 — a new reduce-path field reader, a parser tolerance for a new powermetrics key, a docstring — lands between receipt issuance and fit and produces `pre_data_receipt_joulewise/bundle_read.py_source_sha256_mismatch` (`joulewise/transfer_fiducial.py:1118-1122`) against a receipt that `scripts/fit_transfer_fiducial.py:30-31` forbids reissuing. Cold gate #1's deadlock finding (`48c:12`) is **reduced in count from 24 to 9 and not eliminated in kind**; on churn, the cure removes the mocks (4 commits/60 d) and keeps the two files responsible for most of the risk.

### 3c. Honest changes the cure FAILS to catch

**(i) The ⊆ direction is dead in both failure modes.** §1 shows `subset_assertion_passes=True` at 22, 21, 20 and 7 observed modules against the same 24-entry tuple. Any refactor that removes a call — inlining a `bundle_read` helper, dropping the `authentication_io` round-trip — shrinks the observed set and the test stays green while the receipt keeps freezing a module the program no longer uses. Over-freeze is never detected, only ever accumulated.

**(ii) A verdict-relevant module is already invisible to the mechanism, today.** `schemas.py` decides refusals — `BenchmarkConfig.from_mapping` at `transfer_fiducial.py:1312-1318` is what raises `"planned config is invalid"` (the path `tests/test_transfer_fiducial.py:633-648` exercises). It lives inside `build_capture`, so a `fit_run`-entry-point trace can **never** observe it (measured: fit_run → 7, build_capture → 8). Under the cure, `schemas.py` enters the inventory by magistrate ruling, not by the mechanism. The mechanism's blind spot is not hypothetical; it is realized on this exact code, and the cure papers over the one instance we happen to know about rather than fixing the entry point.

**(iii) Execution tracing structurally UNDER-includes type and constant definitions.** `clock.py` executes zero lines yet is verdict-relevant: `ClockStamp` (`joulewise/clock.py:19-20`, a frozen dataclass) is imported by `uncertainty_evidence.py:12` and by `adapters/powermetrics.py:29`, and the fit path's stamp gate (`transfer_fiducial.py:275-278`, `_clock_stamp_malformed`) is decided by that class's field set. Add a field, change a default, and the fit's refusal behaviour changes with no traced line anywhere. **This is fatal to any `==`-on-traced-set assertion**, and it means the packet's framing — "define 'closed by execution' so it is reproducible" — asks for a primitive that cannot exist. Execution over-includes on one side (import closure) and under-includes on the other (definitions consumed but never run).

**(iv) One fixture covers one verdict.** The synthetic fixture yields `fitted`/`supported`. Every module reachable only on an `inconclusive` or `unsupported` branch is verdict-relevant — refusal *is* the verdict — and is invisible. The cure adds no fixture coverage requirement.

### 3d. The assertion shape I would accept

**Ruled list, normalised alarm, stated blast radius.**

1. **`RECEIPT_SOURCE_MODULES` is human-ruled, not measured** — the `ESTIMATOR_CODE_PATHS` shape 48c actually pointed at (`joulewise/calibration_bracketing.py:180-186`). "Verdict-relevant" is a semantic property; no tracer computes it (3c-iii). The contract carries **one sentence per module** naming what it contributes to the verdict. A module with no such sentence is not in the fence.

2. **The trace becomes a reproducible alarm, not a definition:**
   - runs in a **subprocess**, so the enclosing runner's import state cannot change the answer (§1's 22-vs-7);
   - pre-imports an **explicit name list** — never `walk_packages` (3a) — and asserts at trace start that the `joulewise.*` keys in `sys.modules` equal that declared list, failing loudly otherwise;
   - entry point **`build_capture`**, the verdict producer;
   - over an **enumerated fixture list** covering each verdict outcome (fitted/supported, unsupported, inconclusive, and each refusal family), the list named in the contract;
   - asserts `observed ⊆ RECEIPT_SOURCE_MODULES` **and** `observed ⊇ RECEIPT_SOURCE_MODULES \ DECLARED_NON_EXECUTING`, where `DECLARED_NON_EXECUTING` is a second small tuple — currently exactly `("joulewise/clock.py",)` — each entry carrying its one-line reason in the contract. Both directions live; the set becomes exactly determined; the type-definition case is admitted honestly instead of being smuggled in.

3. **The refusal vocabulary closes the fixture list**: assert that every distinct `_inconclusive_fit` reason string constructible in `transfer_fiducial.py` appears in at least one fixture's observed reasons. A new refusal branch without a fixture then fails the test, which is what stops (3c-iv) recurring.

4. **Blast radius must be ruled explicitly, not left silent.** For `bundle_read.py` and `adapters/powermetrics.py`, either (a) record per-function source digests for the qualnames observed rather than whole-file hashes, or (b) state in the contract that these two are frozen whole, that a receipt is *expected* to be invalidated by unrelated edits to them, and what the operator does then (re-issue before data; after data there is no cure). One of the two must be chosen. Leaving it unaddressed reproduces cold gate #1's finding at 9 modules instead of 24 — the same defect, a fourth time.

5. **No second schema bump needed.** `expected_keys` (`joulewise/transfer_fiducial.py:1064-1074`) does not change when the inventory *values* change, `...PRE_DATA_RECEIPT_SCHEMA` is already `.v2` on this branch, and no receipt has been issued (no data). Say so in the brief so round 3 does not gratuitously bump again.

**Verdict on the cure:** the *set* it lands on is nearly right (9 = my measured 8 ∪ `clock.py`), but every step of its derivation is wrong — unrunnable normalisation, wrong entry point, an assertion direction that cannot fail, and no answer to the over-freeze that caused cold gate #1. Adopting it as written reproduces the same signature a fourth time. **AMEND.**

---

## 4. Bench edit or fixer round — from the contract's standpoint

**Fixer round.** The magistrate's own sizing ("the pre-import block + the constant + contract sentence") understates it by an order of magnitude.

Contract text that must change (`docs/contracts/transfer_fiducial.md`):

| line | disposition |
|---|---|
| `:230-244` enumeration (24 paths) | **replace** — 8 paths, plus **8 new one-sentence justifications** (§3d-1) |
| `:244-247` `source_inventory` / `source_inventory_sha256` rendering | keep verbatim (correct) |
| `:247-251` "closed by execution … subset of the tuple" | **replace** — ~5 sentences: subprocess, explicit pre-import list, `build_capture` entry point, named fixture list, both-directional assertion + `DECLARED_NON_EXECUTING` |
| `:251-252` "not a transitive import-graph walk" | **strike — currently false** (measured: 15 of 22 entries are import-closure) and restate truthfully |
| `:252-256` forcing problem / `se_metrology` example | keep verbatim (good; meets the standard) |
| `:256-258` fence closes before first receipt issuance | keep verbatim (correct, verified against `scripts/fit_transfer_fiducial.py:30-31`) |
| `:259-261` per-path mismatch reason | keep |
| — | **add** 1-2 sentences: the blast-radius ruling for `bundle_read.py` / `adapters/powermetrics.py` (§3d-4) |

≈ **2 sentences struck, ≈ 14 added.** Code side: the tuple at `joulewise/transfer_fiducial.py:58-83` (24→8); a rewritten harness replacing `tests/test_transfer_fiducial.py:408-474` (subprocess + normalisation + two-directional assertion); the fixture list and the refusal-vocabulary closure; **15 mutation tests deleted** with their fixtures; every stored fixture receipt's `source_inventory_sha256` regenerated.

Not a bench edit. But it is the **third round on the same defect**, and the standing escalation trigger has already fired — this cold gate *is* the mandated consult. Round 3 is therefore admissible only if the brief carries the harness **verbatim** (the subprocess normalisation block, the pre-import name list, the entry point, the fixture list, the two assertions) and contains **no discretionary clause** of the form "the trace is the authority, the list above is the starting point". That clause in §B.1 is the proximate cause of the 24-module inventory and must not survive into round 3.

---

## 5. Missed list

**Packet (`59-COLD-GATE-3-packet.md`, §Packet B):**

1. *"trace as luna's test runs it: 20–24 modules"* — the traced set is deterministically **22** in this checkout (three runs, §1). 24 is the *inventory* size (22 traced ∪ `clock.py` ∪ `schemas.py`, corroborated by report 50's own "8 ruled + 16 added"). Conflating the two hides that two inventory members were never observed at all.
2. *"`schemas.py` executes only on a branch at `transfer_fiducial.py:1312`"* — `:1312` is inside `build_capture` (`:1261`), not `fit_run` (`:354`). It is not a branch of the traced path; it is unreachable from it. **Material**: it means the cure's "9" is 7 plus 2 hand-additions the mechanism can never self-check, and it identifies the real root cause (wrong entry point) that the cure does not fix.
3. **The cure is unrunnable as written**: `pkgutil.walk_packages` imports `joulewise/__main__.py` → `raise SystemExit(main())` → the CLI runs against the test's argv and the process dies. Reproduced (§1 mode C, §3a).
4. The packet describes only `sys.settrace` call events. The test's *primary* path is `sys.monitoring` LINE events (`tests/test_transfer_fiducial.py:421-450`), with settrace only as fallback. They agree here (22 both), but LINE monitoring counts module-body execution in modules whose functions are never called — that is precisely the pollution mechanism, and the packet should name it.
5. The packet asks the seat to *"define 'closed by execution' so it is reproducible"* while the cure retains `⊆`. `⊆` is satisfied by every subset and so cannot be made reproducible-in-consequence; and, per §3c-iii, no purely execution-derived definition can be correct in the other direction either. The question as posed has no good answer; the mechanism must be ruled-list-plus-alarm.
6. The packet does not state the over-freeze that survives the cure. 91% of the frozen lines never execute; the two hottest-churn files (52 commits/60 d) stay in.

**Ruling 42b / cold gate 48c:**

7. `48c:12` and `42b:46-47` specify the curated set as *"the modules whose code the fit path executes"* and include `clock.py`. **Bench-refuted**: `clock.py` executes zero lines on either entry point. The ruled starting eight was wrong by one member and asserted as executed by both seats. (It is nevertheless verdict-relevant via `ClockStamp` — which is the point of §3c-iii, and neither ruling noticed the contradiction.)
8. **Neither 42b nor 48c specified the trace's entry point.** §B.1 says only "the ONE end-to-end fixture fit (see C2)", which is ambiguous between `fit_run` and `build_capture`; luna chose `fit_run`, the non-verdict-producing one. This is a brief defect, not a fixer defect.
9. `42b:48-50` / `48c:12` — *"closed by execution, not by import graph"* — is not implementable as stated. With lazy imports inside the traced window (`transfer_fiducial.py:364-365`), execution **is** the import graph. Neither ruling mentioned environment normalisation, which is the only thing that separates them.
10. **Same signature, third instance.** Round 1 failed on "hash the fitter module" without a closed-set definition; round 2 failed on "closed by execution" without a closure definition. `48c:18` explicitly ruled *"That is not 'two rounds failing the same way', so STOP-AND-CONSULT is not triggered."* That call was wrong on the shared signature — both rounds failed because the closure rule was under-specified in the brief, and round 2's §B.1 A2 handed the fixer an unbounded discretionary clause ("the trace is the authority, the list above is the starting point") that guaranteed the outcome. The packet should lead with this: the defect is in brief specification, not in fixer execution, and luna followed the brief exactly.

**Round-2 brief (§B.1) and report 50:**

11. §B.1's verify command is two test modules only. Had it been the discovered suite, the same test would have certified 7 rather than 22 (§1, `with-sibling`). A drift test whose output depends on the verification command is not a fence; the brief's own verification instruction determined the answer.
12. Report 50's mutation-reason table is faithful to the code (`transfer_fiducial.py:1118-1122`) — reasons literally contain `/` and `.py`, e.g. `pre_data_receipt_joulewise/adapters/mock_telemetry.py_source_sha256_mismatch`. Contract `:259-261` describes this correctly. Low-tier note only: this is an unbounded path-templated reason family; the D-078 registry (`docs/contracts/d078_reason_registry_amendment.md`, `tests/test_d078_reason_registry.py`) does not reference `transfer_fiducial` or `pre_data_receipt`, and the arm is diagnostic-only and non-claim-bearing, so no registry violation. Flagged in case a future claim-path consumer parses these strings.
13. Not an error, recorded for the seat: the receipt correctly dropped `estimator_source` (`:1036-1046`, `expected_keys` `:1064-1074`) in favour of `source_inventory["joulewise/powermetrics_fiducial.py"]` plus the pinned-constant check at issuance (`:1030-1031`), and contract `:220-221` reflects that faithfully. `scripts/fit_transfer_fiducial.py` remains separately hashed as `fitter_source`, so the `joulewise/`-only trace filter leaves no gap there.

REFUTER-B: AMEND-CURE
