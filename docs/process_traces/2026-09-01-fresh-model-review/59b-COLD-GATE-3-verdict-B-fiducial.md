# 59b — Cold gate #3, Packet B verdict (cold Fable seat): fiducial receipt inventory

Cold Fable seat (fresh session, read-only) on `59-COLD-GATE-3-packet.md` §Packet B. Paired refuter: `59c-opus-refuter-B-fiducial.md`. Raw verdict follows.

---

# Cold gate #3 — Packet B verdict

Cold seat, 2026-09-01, read-only. Worktree `/Users/edr/code/JouleWise-wt-fiducial` @ `a7a2917c` was clean before and after every command (`git status --short` empty; all runs used `PYTHONDONTWRITEBYTECODE=1`, fixtures written to a `tempfile` dir).

## Bench reproduction

Script: `/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/trace_fiducial.py` (tracer = `sys.settrace`, a `joulewise/` file counts when any frame in it receives a `call` event; run from the worktree root as `PYTHONDONTWRITEBYTECODE=1 python3 trace_fiducial.py <mode>`, Python 3.14.7; mode `c` cross-checked on 3.11). Each mode imports `tests.test_transfer_fiducial` exactly as the test module does, builds `make_synthetic_capture_fixture(Path(tmp))`, and traces `transfer_fiducial.fit_run(runs/"synthetic-transfer-r01")`.

| Mode | Pre-import | Result |
|---|---|---|
| (a) as the test runs it, cold process | none | **22 modules** (the 24-list minus `clock.py`, `schemas.py`) |
| (a') same, using the test's own `_trace_joulewise_execution` (sys.monitoring LINE) | none | **22**, identical set |
| (b) `bundle_read`, `adapters`, `schemas`, `adapters.powermetrics` pre-imported | 4 modules | **7** |
| (c) whole tree via `pkgutil.walk_packages` (83 modules, `__main__` skipped) | 83 modules | **7** |
| (a) twice in one process: cold, then after (c) | — | a#1 = 22, a#2 = **7**; a#1 − a#2 = the 15 import-closure modules; a#2 − a#1 = ∅ |
| (c) on Python 3.11 | 83 | **7**, same set |

The 7: `adapters/powermetrics.py`, `authentication_io.py`, `bundle_read.py`, `powermetrics_fiducial.py`, `transfer_fiducial.py`, `uncertainty_evidence.py`, `validation.py`. Confirmed: (a) is order-dependent and the packet's "20–24" is the cold-process value; with the package tree pre-imported the set is identical across import order, tracer implementation, and Python 3.11/3.14.

Two further measurements the packet did not have (script `scratchpad/trace_fns.py`, per-function names):

1. **`schemas.py` executes in the fixture's `build_capture`**, not in `fit_run`: tracing `build_capture(plan, runs, calibration)` with `fit_run` patched exactly as the test does (line 587) shows `schemas.py` (`BenchmarkConfig.from_mapping` and 13 helpers, the `:1312` branch) plus `transfer_fiducial.py`/`validation.py`. The test already makes that call; it just closes the trace context before it.
2. **`clock.py` does execute on the path but is invisible to any tracer.** `fit_run` → `stamp_from_mapping` (`transfer_fiducial.py:275`) constructs `ClockStamp(...)`, a frozen dataclass; dataclass-generated `__init__` has `co_filename == "<string>"` on 3.11 and 3.14 (checked), so no `call`/LINE event is ever attributed to `clock.py`. The packet's "never executes on this path" is wrong in a way that matters for the definition: it is a trace blind spot, not non-execution.

`ESTIMATOR_CODE_PATHS` (`calibration_bracketing.py:180-185`): four hand-picked modules whose code determines the estimator (`powermetrics_fiducial`, `uncertainty_evidence`, `adapters/powermetrics`, `reduce`), digested per path, mutation-tested per path — deliberately NOT the import closure (`reduce.py` imports far more). Luna's mechanism (curated tuple, per-path sha256, canonical inventory digest, per-path named refusal, `pre_data_receipt_schema_unsupported` by name) matches that spirit exactly; only the membership does not, because the brief told the fixer to add whatever the trace showed and the trace measured the wrong thing.

## 1. Definition of "closed by execution" (contract-ready)

> A `joulewise/` module is **executed by the fit** when, with every module under `joulewise/` except `joulewise/__main__.py` already imported before tracing starts (so that no module body runs during the trace and the result cannot depend on what the process imported earlier), at least one function, method, lambda or comprehension whose code object names that module's file receives a call while the drift test (i) runs `fit_run` on the synthetic fixture bundle `synthetic-transfer-r01` and (ii) runs `build_capture` over the fixture plan with that fit and nine fixture fits. Code the interpreter cannot attribute to a file — dataclass-generated methods, whose code objects report `<string>` — is invisible to this measurement; a module whose only contribution is such code is listed by name in `RECEIPT_TRACE_BLIND_MODULES` with the reason (`joulewise/clock.py`: `ClockStamp`, constructed by `stamp_from_mapping`). The receipt inventory is closed by execution when `executed ∪ RECEIPT_TRACE_BLIND_MODULES == set(RECEIPT_SOURCE_MODULES)`: nothing the fit runs escapes the receipt, and nothing the fit does not run is frozen by it.

Reproducibility evidence: (b), (c), a#2, and 3.11 all give the same 7-set; only the un-pre-imported run varies.

## 2. Inventory ruling

**Keep (9):** the 7 measured runtime modules, plus `schemas.py` and `clock.py`.
- `schemas.py` — KEEP, but not as a "ruled but non-executing" exemption: it executes in `build_capture` (`BenchmarkConfig.from_mapping`, the planned-config binding that feeds `_run_binding_reasons` and hence the `supported` verdict). Widen the trace to cover the `build_capture` call the test already makes, and `schemas.py` is captured by execution. Verdict-relevant: a schema edit changes what config the fit binds to.
- `clock.py` — KEEP as the single named trace-blind member. `ClockStamp`'s field set is the shape every clock stamp is parsed into (`ClockStamp(**fields)` via `stamp_from_mapping`); an edit changes the fit's inputs and no tracer will ever see it. Exemption must be explicit and reasoned in code, not silent.
- `authentication_io.py` — KEEP (already present; it was luna's correct addition): `read_authentication_input`/`read_authentication_text` read the evidence bytes the fit consumes. The ruled eight missed it; the trace found it. That is the drift test doing its job.

**Strike (15):** `adapters/__init__.py`, `adapters/local_transport.py`, `adapters/mock_runtime.py`, `adapters/mock_spec_runtime.py`, `adapters/mock_telemetry.py`, `adapters/suite_control.py`, `arm_readiness.py`, `axi_decode_config.py`, `bundle.py`, `clock_reference.py`, `cooldown_anchor.py`, `identity_pins.py`, `interfaces.py`, `provenance.py`, `suite.py`. Every one entered via module-body execution of an import chain (`adapters/__init__.py:23-25` imports the three mocks; `bundle_read.py:43-88` pulls `axi_decode_config`, `provenance`, `suite` → `bundle`, …); none has a function called by the fit. Freezing them recreates the deadlock in miniature (a mock-adapter edit invalidating a non-reissuable receipt). Yes, mocks and `bundle.py` are struck.

## 3. Drift assertion direction

**Equality, not `⊆`.** `⊆` has two silent failure modes I can demonstrate: (i) it passed with 22 and passes with 7 — a shrinking set never fails, so an inventory can carry dead weight indefinitely (the over-freeze creep this packet is about); (ii) a broken or displaced tracer yields the empty set, which is a subset of anything, so a test that measures nothing passes. "`⊆` plus a minimum count" fixes (ii) but not (i) and names nothing. The equality form in §1 (`executed ∪ TRACE_BLIND == inventory`) fails in both directions with a named diff: a new module escaping the receipt, or an inventory entry the fit stopped executing (e.g. a fixture change that stops taking the `:1312` branch), each forcing a human decision rather than silent drift. Keep the existing no-duplicates and every-path-exists assertions.

## 4. Bench edit or round 3

**Bench edit by the magistrate.** The whole delta is mechanical and fully specified above: (1) an ~8-line pre-import helper (`pkgutil.walk_packages` over `joulewise.__path__`, **skip `__main__`** — see §5), called once before tracing; (2) move the `with _trace_joulewise_execution()` block to enclose both the real `fit_run` and the patched `build_capture` call (lines 578-594); (3) replace the 24-tuple with the 9 and add `RECEIPT_TRACE_BLIND_MODULES = ("joulewise/clock.py",)` with the dataclass reason in a comment; (4) change the assertion at 604-612 to the equality with a two-way diff message; (5) rewrite contract lines 230-258 to carry the §1 paragraph and the 9 paths. The 24 mutation subTests (`:763`) and the key-set assertion (`:755`) iterate `RECEIPT_SOURCE_MODULES` and shrink automatically; `TRANSFER_FIDUCIAL_ESTIMATOR_SHA256` is untouched (`powermetrics_fiducial.py` is not edited). Roughly 40 lines, smaller than the brief it would take to delegate — the doctrine's threshold is met. Because it is a fix to a fix, keep the delta re-audit but size it to the change: one seat (Opus 5 or terra, not luna — she wrote the code; not Sol — round-1 author) re-runs `trace_fiducial.py` modes `a-then-c-then-a` and `c`, reads the diff, and confirms the equality test fails when one of the 9 is removed and when `__main__`-skipping is removed. The magistrate runs the suite itself on 3.11 and 3.14 (rule 1). Not a round 3 and not a reshape: the mechanism luna built is right; the measurement fed to it was under-defined.

## 5. Missed

- **The brief caused the over-freeze, and the ruling supplied the defect.** Brief §A2: "if the execution-trace test shows a further `joulewise/` module executing during the fixture fit, ADD it … the trace is the authority, the list above is the starting point", with DROP licensed only for non-existent paths. Ruling 42b cold-gate section and 48c both define the set as "every `joulewise/` file with executed lines" — module-body lines run by a lazy `import` are executed lines. Luna measured exactly what was specified (my (a') run with her tracer reproduces her 22 + the ruled two = 24) and had no license to question it. This is not a fixer defect; do not charge it as one. The general lesson: an "authoritative" measurement in a brief needs its procedure defined to the point that two runs agree, or the fixer inherits an undefined instrument.
- **The brief specified `⊆`** ("assert that set ⊆ `RECEIPT_SOURCE_MODULES`"); the packet now criticises `⊆` as if it were the fixer's choice.
- **Magistrate's proposed cure has a live hazard:** `pkgutil.walk_packages` + `import_module` reaches `joulewise/__main__.py`, which is `raise SystemExit(main())` — it parsed my argv and exited (`joulewise: error: argument command: invalid choice`). Under unittest it would parse unittest's argv. The pre-import must skip `__main__` (and should assert every other import succeeded, so a future import-time failure fails loudly instead of silently shrinking coverage).
- **Packet bench fact "`clock.py` never executes"** is a tracer blind spot, not a fact about the program (§Bench 2). The proposed cure's rationale for keeping `clock.py`/`schemas.py` ("ruled but do not execute") is therefore wrong on both: `schemas.py` executes in scope once the scope is right, `clock.py` executes invisibly. Both stay, for the reasons in §2, and the reasons must be written into the code and contract, not "because ruled".
- **Trace scope was `fit_run` only** while the receipt's stated purpose is to freeze "the program that fit the data"; `build_capture` is where fits become a verdict (`_run_binding_reasons`, `summarize_target_edge_radii`, `supported iff …`). The test already runs it; the trace should cover it.
- **Contract paragraph (`transfer_fiducial.md:247-252`)** currently states an unreproducible definition ("at least one source line executes") as if it were closed; it must carry §1 verbatim so a reader can rerun the closure and get the same 9.
- Minor: the packet's "20–24" is a range because the cold-process count is 22 and the two ruled non-traced modules make 24; stating it as a range obscured that the un-pre-imported number is itself deterministic for a cold process. Not load-bearing.

VERDICT-B: BENCH-EDIT
