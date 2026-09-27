# Cold gate BFGS-S1-SWEEPCLASS-01: paired Opus contract-lens refuter

Seat: Opus 5.5, contract lens. Code: detached worktree `/Users/edr/code/JouleWise-wt-s1swcg-92472459` @ `cbfa9dc3` (`git status --short` empty before and after every probe). Scratch: `/tmp/oc_sw92/`. No repository file edited; no background task; no subagent.

**Contamination disclosure.** The harness put the owner's global `CLAUDE.md`, the project `CLAUDE.md`, the private project notes file and the memory index into my context before the charge. I opened none of the files they point to and cite none of them. Everything below rests on the packet texts named in the charge, the code at `cbfa9dc3`, and probes I ran.

---

## Section A: independent answers, written before any ruling existed

### A.0 What the two texts actually say (contract lens)

- **Text 8** (`2026-09-26-activation-6bec2aa6/.../30-addendum/21-coldgate-fable-addendum-ruling.md` §4 C, line 115) names the four energy accessors **by name**: "**The four energy accessors `summed_curve`, `source_curve`, `trace_rows`, `measured_window` call `self.metadata()` first**, so every byte-level re-derivation passes the gate. `raw_metadata`, `raw_config`, `raw_summary`, `raw_artifact_bytes` **stay tolerant and are governed by the sweep (text 12)**." So `raw_summary` is not one of the four, and text 8 forbids gating it inside the reader. Its governance is per call site, through text 12's sweep.
- **Text 12** (same file, line 123) watches exactly `raw_metadata`, `raw_config`, `raw_summary`, `raw_artifact_bytes` and direct reads of `summary_metrics.json`, `metadata.json`, `power_trace.csv`. It has three classes: `non_claim`, `historical`, `strict_validation`. `events.jsonl` and the `raw/` telemetry files are **not** watched.
- **Amendment 51** (erratum §10) adds `behind_gate`. Its (b) 1 makes **every call** of a tolerant accessor, on any receiver, a read site of its own. Its (c) admits exactly two gate forms, `authenticate_window_members` and `X.metadata()` on a `BundleReader`. Its (d) 2 says a `try` body counts as a branch "unless every handler of that `try` has `raise` … as its last statement".

**Consequence for the seat's third row.** The row `bundle_read.py::BundleReader.raw_summary, direct:_tolerant_json, summary_metrics.json` is the accessor's **definition**, not a use. Every use of `raw_summary` is already a separate (b) 1 site with its own row. The definition row is a duplicate entry for reads that are inventoried at their callers. It is a classification question, not a text-8 gap.

### A.1 Executed evidence

| Id | Probe | Result (exact) |
|---|---|---|
| A1 | `shasum -a 256 /tmp/cg_r2/sweep49.py`; `python3 /tmp/cg_r2/sweep49.py . -v` at `cbfa9dc3` → `/tmp/oc_sw92/proto_cbfa.txt` | prefix `8e0d3bcdde3214e2` (the first ruling's prototype); `sites 126 distinct rows (path,function,operation,file) 120 functions 89 cross-module constants 11` |
| A2 | `/tmp/oc_sw92/q2_probe.py`: copy `tests/fixtures/d078_r01` to a temporary directory, put a `battery_float` record that is not a valid pair into `metadata.json`, then call every public `BundleReader` method on a **fresh** reader (nothing cached, no gate call first) | `metadata(): BatteryStatusRefusal battery_float_evidence_missing …`. **RAISED** `BatteryStatusRefusal`: `trace_rows`, `summed_curve`, `source_curve`, `measured_window`, `metadata`. **RETURNED with energy-bearing content:** `raw_summary` (markers `gross_energy_j`, `energy`, `power_w`), `raw_metadata` (`power_w`), `events` (`power_w`). **RETURNED, no energy marker:** `block_windows`, `config`, `is_complete`, `is_event_v2`, `is_frozen_legacy_identity`, `item_windows`, `level_windows`, `phase_windows`, `problems`, `rail_manifest`, `raw_config`, `request_phase_windows`, `runtime_cleanup_ok`, `suite_manifest`, `suite_window`, `token_timestamps`. Raised for a missing file (not the gate): `request_roster`, `request_rows`, `request_token_rows`, `suite_item_records`. |
| A3 | the same refused bundle: which energy fields `events()` returns; `raw_artifact_bytes("powermetrics.plist")`; the plist's keys | `('stage_completed/idle_baseline.power_w_mean', 'float')`; `raw_artifact_bytes powermetrics.plist -> 474874` bytes returned; plist keys include `cpu_energy`, `gpu_energy`, `ane_energy`, `combined_power`, `cpu_power`, `gpu_power` |
| A4 | `grep -rn --include='*.py' -E '\.raw_(summary\|artifact_bytes\|metadata\|config)\(' joulewise scripts`, then for each `raw_summary`/`raw_artifact_bytes` site the enclosing function and its gate calls (inline AST script) | see table A.3 |
| A5 | `grep` for callers of `derive_idle_mean_uncertainty`, `_reduce_v060(`, `_reduce(`; `sed -n 2648,2700p joulewise/reduce.py` | only `reduce.py:3302` (in `_reduce_v060`) and `:3563` (in `_reduce`); those two are called only at `:2673`, `:2686`, inside `reduce_bundle`, after `metadata = reader.metadata()` at `:2653`, which sits in `try … except BundleReadError: return summary_type(status=FAILED…)` |
| A6 | `/tmp/oc_sw92/try_return.py`: every `try` in tracked `joulewise/`, `scripts/` whose body calls a gate, with a handler whose last statement is not `raise` | `calibration_bracketing.py:2758 ['Return']`; `reduce.py:2651 ['Return']`; `window_duration_margins.py:944 ['Raise', 'Expr', 'Expr']`. The two `Expr` handlers are `_refuse(...)` calls; `window_duration_margins.py:134 def _refuse(...): raise WindowDurationMarginsRefusal(...)` |
| A7 | `sed` of `joulewise/envelope_gate.py:71-240`; `joulewise/cli.py:2057-2080`; exception MRO | `analyze_envelope_gate(bundle_dirs, …)` takes the bundle list from the command line (`_cmd_envelope_gate`, `args.bundle_dirs`); every admitted reader goes through `_manifest_record(reader)`, which calls `reader.metadata()` (`:233`) inside `try … except BundleReadError: return _refused(...)`; `BatteryStatusRefusal` MRO `['BatteryStatusRefusal', 'BundleReadError', …]`; `CustodyFailure` MRO `['CustodyFailure', 'RuntimeError', …]` (not caught there) |
| A8 | `sed` of `scripts/make_figures.py:160-245, 680-730`; `grep 'extract_rows('` | `--bootstrap-input-manifest` rebuilds the input manifest from any `--runs-root` (`build_input_manifest`), so the corpus is not fixed by committed code; but every output written after `gate_inputs` is a void placeholder ("its measurements are never read into a regenerated publication artifact"); `extract_rows` has **no caller** in the tracked tree |
| A9 | `grep` for direct reads of `raw/powermetrics*.plist` and `events.jsonl` in tracked `joulewise/`, `scripts/` | 28 files. Among them, `scripts/paper_anchor_correction_quantified.py:285-293,495` and `scripts/paper_excursion_decomposition.py:189,238` read `raw/powermetrics.plist` and `events.jsonl` (each checked against a recorded digest) and write paper payloads; `scripts/floor_reconciliation_receipt.py:40` (`_anchored_records`) reads `raw/powermetrics.plist`, and is called from `_bundle_row` after `reader.metadata()` (`:103`). None of these is visible to the sweep: the watched names do not include `raw/…` or `events.jsonl`. |
| A10 | `PairVerdict` fields (`battery_float.py:762-771`) | `kind, status, reasons, pre_raw_sha256, post_raw_sha256, pre_update_age_s, post_update_age_s, delta_q_mah, bundle_sha256`: `delta_q_mah` is a **charge** value, so a function returning verdicts fails `strict_validation`'s "digest, boolean, identity string, or list of problem strings" |

### A.2 Q1: reads inside the authentication and reader functions

**Independent answer.** There are three different things in the seat's table, and one class does not fit them all.

1. **The gates themselves**: `battery_float.py::authenticate_bundle`, `bundle_read.py::BundleReader.metadata`, `bundle_read.py::authenticate_window_members` (the prototype also reports this one: `direct:_strict_json metadata.json`). The read is the gate's input; nothing leaves the function before the verdict is formed and checked. None of the four classes fits: they return a verdict (A10: `delta_q_mah`) or full metadata. A new class is right, **but only as a closed list, checked by the sweep:**
   - The class `gate_implementation` admits exactly the keys listed in the test as a constant; the sweep asserts the constant equals `{battery_float.py::authenticate_bundle, bundle_read.py::BundleReader.metadata, bundle_read.py::authenticate_window_members}` (each with its reported operation and watched name). A new key needs a cold gate; the seat cannot add one.
   - `authenticate_bundle` is verified by the existing byte-identity pin of `battery_float.py` (any edit to the file, including a new function, fails the pin).
   - `BundleReader.metadata` is verified structurally: the sweep asserts that in its body every `return` and every store into `self._cache` comes after, and is dominated by, the call `self._battery_verdict(...)`, and that a `raise` guarded by a test on that verdict's `status` lies between them. Counterfactual: move `self._cache["metadata"] = raw` above the verdict call → RED.
   - `authenticate_window_members` is verified the same way against its authentication call (the row names the call).
2. **Tolerant-accessor definitions**: `BundleReader.raw_summary`, `BundleReader.raw_metadata` (both `direct:_tolerant_json`). These are not gates, and must not be called "gate implementation". Their reads are inventoried at every caller by (b) 1. Self-verifying rule: the row class `tolerant_accessor_definition` is admitted only for a method of `BundleReader` in `joulewise/bundle_read.py` whose name is in the test's `TOLERANT` set, whose body (docstring aside) is the single statement `return self._tolerant_json(<watched constant>)`; and the test asserts that `TOLERANT` equals text 8's four names. A function with any other body, name, or class fails.
3. **Reader internals that fit an existing class**: `BundleReader.events` (`direct:_strict_json metadata.json`) reads only whether the key `battery_float` is present → `non_claim` (i), field `battery_float` (presence). `BundleReader.problems`, `_check_power_trace`, `axi_v2_validation_problems`, `BundleReader.is_complete`/`is_event_v2`/`is_frozen_legacy_identity`/`rail_manifest` return problems, booleans or rail names → `strict_validation` or `non_claim` (i) under the existing table. No new class.

### A.3 Q2: `BundleReader` public methods and `raw_summary`'s callers

**Public methods** (A2, A3). "Gate first" = calls `self.metadata()` before returning.

| Method | Energy-bearing return? | Gate first? |
|---|---|---|
| `metadata` | yes (idle `power_w_mean`, battery pair, adapter watts) | **is** the gate |
| `trace_rows`, `summed_curve`, `source_curve` | yes (power samples) | yes |
| `measured_window` | no (integration bounds) | yes |
| `raw_summary` | **yes** (`gross_energy_j`, `idle_subtracted_energy_j`, `phase_energy_j`, …) | **no** (text 8: tolerant) |
| `raw_metadata` | **yes** (`power_w_mean`, battery current/voltage) | **no** (text 8: tolerant) |
| `raw_artifact_bytes` | **yes** (raw `powermetrics` samples: `cpu_energy`, `combined_power`, …) | **no** (text 8: tolerant) |
| `events` | **yes** (`idle_baseline.power_w_mean`) | **no**, and **not named by text 8 or text 12 at all** |
| `raw_config`, `config`, `is_complete`, `is_event_v2`, `is_frozen_legacy_identity`, `rail_manifest`, `phase_windows`, `token_timestamps`, `request_*`, `suite_*`, `item_windows`, `block_windows`, `level_windows`, `runtime_cleanup_ok`, `problems`, `path` | no | no |

**Every production call of `raw_summary`** (A4), with the enclosing function:

| Site | Gate first? | Where the energy goes |
|---|---|---|
| `determinism_gate.py:260` `_inspect_strict_valid_bundle` | yes, `reader.metadata()` `:259` | — |
| `aggregate.py:156` `_read_member` | yes, window gate `:155` | — |
| `analysis_engine/inputs.py:1928` `bind_floor_artifact_evidence` | yes, window gate `:1894` | — |
| `analysis_engine/inputs.py:2834` `_read_bundle` | yes, window gate `:2824` | — |
| `run_campaign.py:2020, 2093` `assert_production_uncertainty` | yes, `reader.metadata()` `:2019` | — |
| `scripts/paper/partial_record_enclosure.py:249` `_derive_bundle_authenticated` | yes, `reader.metadata()` `:228` | — |
| `bundle_read.py:760` `is_complete`; `:1433` `axi_v2_validation_problems`; `cli.py:424` `_strict_problems` | no | a boolean or problem strings only |
| `reduce.py:2756` `_resolve_reducer_version` | no (runs before `:2653`) | a reducer-version string only |
| `envelope_gate.py:133, 654` `analyze_envelope_gate`, `_level_window_energy_records` | **not in the function**; every reader passed `reader.metadata()` in `_manifest_record` first, and a refusal returns a `refused` verdict with no energy (A7) | `level_window_gross_energies_j` in the verdict artifact |
| `make_figures.py:241` `gate_inputs` | no | a status check; outputs are void placeholders (A8) |
| `report.py:216` `_discover_bundles` | no | the static HTML run browser under the `--output` directory |
| `analyze_phase_share.py:96` `analyze_bundle` | read first; `reader.summed_curve()` (gated) is called later and the payload is printed only if it returns | a stdout JSON diagnostic |
| `corpus_compat_receipt.py:146` `evaluate_bundle` | no | a compatibility receipt |

`raw_artifact_bytes` has one production caller, `idle_dependence.py:198` `derive_idle_mean_uncertainty`, reached only through `reduce_bundle` after `reader.metadata()` (A5).

**Plain statement.** On every path I traced at `cbfa9dc3`, no energy value read through `raw_summary` or `raw_artifact_bytes` reaches a claim artifact (the charge's list: a floor artifact, a whole-window verdict row, an analysis output, a results-registry fill, a figure) without a battery gate first. `report.py` and `corpus_compat_receipt.py` do emit energy with no gate, and they depend on the `non_claim` (ii) check of their outputs: the HTML run browser and the receipt must have no reader that is a claim artifact. That check is the refuter's to run, row by row; I have NOT EXECUTED it for those two outputs. **Closure: do not gate `raw_summary`.** Text 8 forbids it, and `is_complete`, `problems` and the strict validator must work on refused bundles (A2: `is_complete` returned on a refused bundle). Pin it per caller: (b) 1 already makes every call a row.

**But three existing allowlist reasons at `cbfa9dc3` are wrong** (`tests/test_bfgs_consumer_sweep.py`):
- `envelope_gate.py` rows carry `historical`, "Legacy affine-smoke … diagnostic". The class condition ("cannot be pointed at a later bundle") is **false**: the command takes any bundle directories (A7). The site is safe only because a callee (`_manifest_record`) gates every reader, which the sweep cannot see. No class admits it honestly: `behind_gate` has no "callee" form. This is a Q3 case.
- `idle_dependence.py::derive_idle_mean_uncertainty` carries `strict_validation`, but it returns an idle-power uncertainty (energy-bearing). Its true class is `behind_gate`, callers form, chain `_reduce_v060`/`_reduce` → `reduce_bundle`. **That chain fails under amendment 51 (d) 2 as ruled** (next section).
- `analyze_phase_share.py::analyze_bundle` carries `non_claim` "no governed claim output"; its real protection is the later `summed_curve()` gate, which (c) does not count as a gate.

### A.4 Q3: other reads of the same kind, and where the detector misjudges

1. **(d) 2 treats `return` as fall-through.** A6: all three `try` statements that the erratum's X7 counted as "swallowing" cannot actually let execution continue past the `try`. Two handlers end in `return` (`reduce.py:2651`, `calibration_bracketing.py:2758`); the third's handlers end in `_refuse(...)`, which always raises (`window_duration_margins.py:134`). Under (d) 2 as ruled, all three gates stop counting as dominating. The reads after them become reported sites that fit no class. `reduce.py:2651` is the reducer's own gate: it is the anchor of the `derive_idle_mean_uncertainty` callers chain. A seat that implements (d) 2 exactly will hit this NEEDS_RULING again.
2. **A gate in a callee is invisible** (`envelope_gate.py`, A7). Amendment 51 (h) does not list this.
3. **Text 12's watched names omit `events.jsonl` and `raw/`**, both energy-bearing (A2, A3). `BundleReader.events()` and `raw_artifact_bytes` return energy content from a refused bundle. Direct reads of `raw/powermetrics.plist` in `paper_anchor_correction_quantified.py`, `paper_excursion_decomposition.py` and `floor_reconciliation_receipt.py` (A9) are not in the 120 and cannot be. The two `paper_*` scripts check digests and derive timing bounds from calibration captures, and the receipt is gated by its caller. So I found no *leak* here, but the sweep's own claim, that every read is inventoried, is false for these files, and (h) does not say so.
4. Among the 120 reported rows, I found **no** site that returns energy to a claim artifact with no gate at all, beyond the two `non_claim` (ii) outputs above whose readers I did not check. The prototype does not implement (b) 3, (c) [E] or (d) 2–5 (A1 is the first ruling's prototype, unchanged), so the final count is NOT EXECUTED.

### A.5 Not executed in Section A

- The (ii) reader search for `report.py`'s HTML output and `corpus_compat_receipt.py`'s receipt.
- `analyze_envelope_gate` on a refused suite bundle (no suite fixture was at hand); the gating claim rests on code reading (A7).
- A full re-classification of the 120 rows; the prototype with amendment 51's (b) 3 and (d) 2–5.

---

## Section B: refutation of `21-coldgate-fable-ruling.md` (read at 22:16 PDT, after Section A was written)

### B.0 Where the ruling and Section A agree (independent convergence)

These points were reached independently, before I read the ruling:
- `raw_summary` is not one of text 8's four; it is tolerant by ruled text; do not gate it.
- The seat's third row is the accessor's **definition**, inventoried at its callers by (b) 1. The ruling's `tolerant_definition` matches my "body is exactly `return self._tolerant_json(<const>)`" check.
- The gates need a closed class, checked by structure. `authenticate_window_members` is a third gate-body row the seat did not list.
- (d) 2 must accept `return`: `reduce.py:2651`. `derive_idle_mean_uncertainty` is mis-classed; it is `behind_gate` through `reduce_bundle`.
- The stage journal (`events()`, `idle_baseline.power_w_mean`) is an unwatched energy channel.

I confirm the ruling's X1 count (120 rows / 89 functions) and its X12/X15 facts from my own runs (A1, and `git status` empty).

### B.1 Executed evidence (new in Section B; `/tmp/oc_sw92/`, SHA-256 prefix)

| Id | Probe | Result (exact) |
|---|---|---|
| B1 | `alias.py` (`6cb3252d585493c4`): the judge's own detector `/tmp/cg_sweep/sweep59.py`, `S.sweep("joulewise/zz_new.py", src, {})`, on four sources | `A1 bound-method alias -> silent` (`get = BundleReader(b).raw_summary; return get()["gross_energy_j"]`); `A2 getattr by string -> silent`; `A3 map over readers -> silent` (`map(BundleReader.raw_summary, …)`); `A4 direct call (control) -> REPORTED` |
| B2 | an AST scan of tracked `joulewise/`, `scripts/`: every attribute named `raw_metadata`/`raw_config`/`raw_summary`/`raw_artifact_bytes` that is not a callee, and every string constant equal to one | `non-call attribute refs 17 string refs 0`; all 17 are `raw_config` (dataclass fields in `analysis_engine/inputs.py`, `scripts/mint_floor_artifact.py`); **zero** for `raw_summary`, `raw_metadata`, `raw_artifact_bytes` |
| B3 | `cache_probe.py` (`bc7042a2a202fa38`): the judge's charging bundle (`reader_probe_lib.build(charging=True)`); `r._cache.update(metadata=r.raw_metadata())`; then `r.trace_rows()` | `trace_rows after _cache.update on a CHARGING bundle: RETURNED 2 rows; sentinel True` |
| B4 | AST scan for writes to `_cache` in tracked `joulewise/`, `scripts/`; `grep '\._cache\b'` outside `bundle_read.py` | only `ASSIGN joulewise/bundle_read.py 420 self._cache` (`__init__`); no `update`/`setdefault`/`pop`/`clear` call on `_cache`; no `._cache` outside `bundle_read.py` |
| B5 | `rebind.py` (`cf36ebbb20fafb88`), the judge's `sweep59.py` | `R1 import then module-level rebind -> silent` (`from joulewise.bundle_read import authenticate_window_members` / `authenticate_window_members = lambda members: {}` / gate call / read); `R2 import then local def of same name -> silent`; `R3 … raw_summary on reader rebound from a param -> REPORTED` |
| B6 | AST scan: any binding of the names `authenticate_window_members` or `BundleReader` in tracked `joulewise/`, `scripts/` other than `from joulewise.bundle_read import <name>` (and the one definition in `bundle_read.py`) | none (`done`, no line) |
| B7 | `envelope_probe.py` (`d60ee9f109d11b99`): the judge's charging bundle, `BundleReader.suite_manifest` stubbed so `_manifest_record` is reached, `analyze_envelope_gate([b], lambda p: [])` | `tree: bundle_refused ['suite_manifest_missing'] battery_float_confounded: pre IsCharging is not No; …  \| energy key present: False`. So the battery gate is reached **only** through the callee `_manifest_record` (`envelope_gate.py:233`, the one `metadata()` call in the file), and the verdict reports it under the wrong reason code. The counterfactual (callee without `metadata()`) crashed on my stub (`config` is `None`): NOT EXECUTED. |
| B8 | `grep -rn 'envelope_gate.v1\|level_window_gross_energies_j\|envelope-gate'` over `joulewise scripts docs/paper configs analysis`; `grep extract_rows` | only `envelope_gate.py`, `cli.py`, and a comment hit in `reduce.py` (no reader of the verdict JSON); `extract_rows` is called only by `tests/test_rpt001_report_slice.py:269` |
| B9 | `journal58e.py` (`ae1fa9d48361837a`) / `journal58e_eq.py` (`8fb822ce1978926e`): amendment 58 (e)'s screen over **every** function of tracked `joulewise/`, `scripts/`, with "holds the constant `events.jsonl`" read as *contains* and as *equals or ends in `/events.jsonl`* | contains: `count 5`, the four of X14 **plus `joulewise/reduce.py::_reduce`** (it holds `"no measured_run window in events.jsonl "`); equals: `count 4`, exactly X14's |
| B10 | AST scan for functions (outside `joulewise/adapters/`) that hold a string constant matching `^(raw/)?(powermetrics(_idle)?\.plist\|nvidia_smi[^ ]*\.csv)$` | `functions 28`. Among them are `window_duration_margins.py::_observe_member` (a consumer; called after the window gate at `:950`), `floor_reconciliation_receipt.py::_anchored_records` (called after `reader.metadata()` `:103`), `paper_anchor_correction_quantified.py::analyse_capture`, `paper_excursion_decomposition.py::rederive`/`build_payload`, and `check_paper_replay_fence.py::derive_from_artifacts` (digest-pinned timing re-derivations for the paper). **None is visible to the sweep.** |
| B11 | `joulewise/controller.py:2030-2068`: the keys written to `outputs/requests.jsonl` | `acceptance_rate batch_group_id failure_reason output_policy_name output_token_count request_id request_input_id request_ordinal requested_output_tokens response_text stop_reason target_emitted_count terminal_status tokens_accepted tokens_proposed`: no energy-class key (resolves the ruling's §9 NOT EXECUTED item for `request_rows`) |
| B12 | `git status --short` in the working tree after every probe | `0` lines |

### B.2 Findings

**No BLOCKER.** I found no energy value that reaches a claim artifact without a battery gate at `cbfa9dc3` on any path I traced (Section A.3 and B7, B10). Every finding below is a hole in the **self-verification** the charge asked for, or a row the seat will be forced to return again. Each closure is GREEN on the tree today (B2, B4, B6), so it costs nothing to land now.

#### RSW-1 (SHOULD-FIX). 57 (d)'s premise is false: a tolerant accessor used without a call expression is not a read site

The ruling justifies `tolerant_definition` with this sentence (§4.4): "membership of that constant is exactly what causes every call to be reported". But (b) 1 matches only a **call whose callee is an attribute** with that name. A bound-method alias, a `getattr` by string, or a `map(BundleReader.raw_summary, …)` returns a charging bundle's energy, and the ruled detector reports nothing (B1: A1–A3 silent, A4 reported). So a new ungated energy read can be added and nothing fails. The tree has zero such references for the three energy-bearing names (B2), so the closure is free.

**Replacement text.** Append to amendment 57 (d):

> 5. Amendment 51 (b) 1 is extended: a read site is also **any reference to the name `raw_summary`, `raw_metadata` or `raw_artifact_bytes` that is not the callee of a call**: an attribute of that name on any expression, or a string constant equal to it. It is reported as operation `ref:<name>`, watched name `-`. (`raw_config` is excluded: 17 tracked references are dataclass fields of that name, and `config.json` holds no energy-class value.)

**Test row.** R57-10: sources A1, A2, A3 of B1 → each reported as `ref:raw_summary`. Counterfactual: (b) 1 as ruled (executed silent on the judge's `sweep59.py`, B1).

#### RSW-2 (SHOULD-FIX). 57 (b) 4 guards the gate's cache slot against one write form only

Rule 4 looks only for an assignment whose target is `<expr>._cache["metadata"]`. `r._cache.update(metadata=r.raw_metadata())` fills the same slot. After it, `trace_rows()` returns a charging bundle's power rows (B3). The gated energy accessors trust that slot, because `self.metadata()` returns it without re-checking. R57-6 tests only the subscript form. On the tree, `_cache` is named only in `bundle_read.py`, and is written only by `__init__` and by subscript assignments (B4).

**Replacement text** for 57 (b) 4:

> 4. **The cache slot.** The attribute name `_cache` occurs in no tracked file under `joulewise/` or `scripts/` other than `joulewise/bundle_read.py`. Inside that file, `_cache` is written only by the assignment `self._cache = {}` in `BundleReader.__init__` and by assignments to a subscript of `self._cache`. No method of `self._cache` other than `get` is called. An assignment whose target is `self._cache["metadata"]` occurs in `BundleReader.metadata` and in no other function.

**Test row.** R57-6b: a function in `joulewise/zz_new.py` with `r = BundleReader(b); r._cache.update(metadata=r.raw_metadata()); return r.trace_rows()` → fails, naming the file and the call. Counterfactual: rule 4 as ruled (it has no subscript target to find). Behaviour companion, executed: B3.

#### RSW-3 (SHOULD-FIX). A gate **call** can still be claimed by name alone

The charge asks that no new function claim the gate by name. 57 (b) 1 blocks a second *definition* of the gate. But it asserts "not assigned at the module's top level" **only for `joulewise/bundle_read.py`**. In any other module, 51 (c) accepts `authenticate_window_members(...)` as the window gate if the module imports the name, even when the module then rebinds it. With a module-level rebinding (R1) or a local `def` of the same name (R2), the read after the call is silent (B5). No tracked module binds either name other than by importing it (B6).

**Replacement text.** Append to 57 (b) 1:

> … and that in every tracked file under `joulewise/` and `scripts/`, the names `authenticate_window_members` and `BundleReader` are bound only by `from joulewise.bundle_read import <name>` without `as`, or by their one definition in `joulewise/bundle_read.py`. No assignment, `def`, `class`, parameter, `for`/`with`/`except` target, comprehension target, or other import may bind either name.

**Test row.** R57-11: sources R1 and R2 of B5 → the sweep fails, naming the binding. Counterfactual: 51 (c) as ruled (executed silent, B5).

#### RSW-4 (SHOULD-FIX). Two row groups keep a class whose condition is false, so the seat must return them

The ruling leaves the eight `historical` rows of 51 (g) 4 to "the seat's and the refuter's" check (§5.2), and it states "No further site needs a new class" (§6). The condition of `historical` is that the function "cannot be pointed at a later bundle". That is false for two files:
- `envelope_gate.py::analyze_envelope_gate` and `::_level_window_energy_records` (`raw_summary`). The command takes any `bundle_dirs` (A7). The rows emit `level_window_gross_energies_j`. They are safe only because the callee `_manifest_record` calls `reader.metadata()` on every reader. The sweep cannot see that, and no `behind_gate` form describes a gate in a callee. Executed: a charging bundle yields `bundle_refused`. The verdict reports the refusal as **`suite_manifest_missing`** (B7).
- `make_figures.py` (`gate_inputs`, `extract_rows` ×3, `realized_output_tokens`). `--input-manifest` and `--bootstrap-input-manifest` re-point the corpus. The outputs are void placeholders, and `extract_rows` has no production caller (A8, B8).

Under 58 (d), the envelope rows (which return energy) may carry only `behind_gate`, `historical`, or `non_claim` (ii). Only (ii) is true. I found no reader of the verdict JSON (B8).

**Replacement text.** A new paragraph in §6 and 51 (g) 4:

> 51 (g) 4 is amended. The two `joulewise/envelope_gate.py` rows carry `non_claim` (ii). Their reason is: "writes the envelope-gate verdict (`envelope_gate.v1`), returned only to `joulewise/cli.py::_cmd_envelope_gate`, which writes `--output` or stdout; no tracked file reads it. Every reader passes `reader.metadata()` in `_manifest_record` first (a callee; the sweep cannot check it, see (h))." `scripts/make_figures.py::gate_inputs` carries `non_claim` (i), field read `status`. `extract_rows` (three rows) and `realized_output_tokens` carry `non_claim` (ii): no production caller, and `main` writes void placeholders. `historical` stays on the rows whose corpus is pinned by committed code. The refuter re-checks each of those against the condition. 51 (h) gains: "**A gate in a callee.** A gate call inside a function that the row's function calls first is not seen."

**Lane (outside S1's WRITE_SCOPE).** `envelope_gate` reports a battery refusal under `suite_manifest_missing` (B7). It should name the battery status.

#### RSW-5 (SHOULD-FIX). The raw meter capture is a second unwatched energy channel, and (h) does not name it

58 (e) names the stage journal. It does not name path reads of `raw/powermetrics.plist`, `raw/powermetrics_idle.plist` or `nvidia_smi` captures. Those files hold `cpu_energy`, `combined_power` and similar keys (A3). Twenty-eight functions name them (B10), including one consumer and three scripts that re-derive paper numbers. Each one I read is gated by its caller, is digest-pinned, or derives timing only. But the sweep sees none of them. So text 8's sentence "every byte-level re-derivation passes the gate" holds only for re-derivation through the reader. 58 (a) says this for the tolerant accessors and not for path reads.

**Replacement text.** A new 58 (f):

> (f) **The meter's raw capture.** Amendment 51 (h) gains: "**A read of the meter's raw capture by path.** `raw/powermetrics.plist`, `raw/powermetrics_idle.plist` and `nvidia_smi` captures are not watched files, and they hold energy-class values." The sweep holds the constant `RAW_CAPTURE_READERS`: the set of `path::qualified function` for every function in a tracked file under `joulewise/` (excluding `joulewise/adapters/`) or `scripts/` that holds a string constant matching `^(raw/)?(powermetrics(_idle)?\.plist|nvidia_smi[^ ]*\.csv)$`. The computed set must equal the constant (28 at `cbfa9dc3`). The refuter states, for each new member, whether its energy-class content reaches a claim artifact ungated.

**Test row.** R58-7: a function added to `joulewise/aggregate.py` that reads `(p / "raw" / "powermetrics.plist").read_bytes()` → the sweep fails. Counterfactual: no such constant.

#### RSW-6 (NIT). 58 (e)'s screen is ambiguous by one function

"holds the constant `events.jsonl`" gives X14's four when read as equality, and five when read as containment (it adds `reduce.py::_reduce` through a message string) (B9). **Replacement:** "holds a string constant equal to `events.jsonl` or ending in `/events.jsonl` (the form of a watched constant in 51 (a))".

#### RSW-7 (NIT). 58 (b) files `events` as `other`, against its own last sentence

§5.1 and 58 (e) say `events` returns an energy-class value (`power_w_mean`). 58 (b)'s last sentence says that giving such a method `other` "is a finding". **Replacement:** add the kind `journal`, with the name `events`, and the assertion: "the one public method that parses `events.jsonl`; its energy-class content is governed by 58 (e)". Remove `events` from `other`.

#### RSW-8 (NIT, resolves a NOT EXECUTED item). `request_rows` and `request_token_rows` hold no energy-class key

B11 lists the keys the controller writes. `other` is correct for them. No text change.

#### RSW-9 (NIT, no text change). 59 (a) still counts a handler ending in an always-raising helper as a branch

`window_duration_margins.py:944`'s handlers end in `_refuse(...)`, and `_refuse` always raises (`:134`). X3 shows no watched read after that `try`, so no row arises today. If one arises, the seat classes it or returns it. It does not widen the rule by name.

### B.3 Answers to the three refutation questions

- **Wrong or incomplete?** The rulings on Q1 and Q2 are right in substance and agree with Section A. The ruling is incomplete in RSW-1 to RSW-5.
- **Could a new function claim the new class by name alone?** `gate_body`: no. Rules (b) 1, 2 and 6 hold, and I found no way around them. `tolerant_definition`: no, but the protection behind it (every use is a read site) fails for non-call uses (RSW-1). The gate **call** can still be claimed by name after a rebinding (RSW-3), and the gate's **cache slot** can be filled without the gate (RSW-2).
- **Does an ungated energy read survive?** Not one that reaches a claim artifact on any path I traced at `cbfa9dc3`. Latent paths that the sweep cannot see do survive: RSW-1, RSW-2, RSW-3 and RSW-5. Each closure is GREEN on the tree (B2, B4, B6, B10).

### B.4 Not executed in Section B

- The `envelope_gate` counterfactual (B7; my stub could not go past `config`).
- A full re-read of the 28 raw-capture functions of B10: I read six.
- The R57-10, R57-11, R57-6b and R58-7 rows as mutations of the repository's sweep: they were run against the judge's prototype (B1, B5) or as behaviour (B3) only.
