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
