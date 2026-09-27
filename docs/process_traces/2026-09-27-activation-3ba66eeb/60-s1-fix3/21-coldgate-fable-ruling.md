# Cold gate S1-FIX3-RETURNS-01: ruling (Fable 5.1, cold judge) on the three returns of the fix-round-3 seat

Candidate: working tree `/Users/edr/code/JouleWise-wt-s1ret-3ba66eeb`, detached @ `8953c7a5` (the S1 branch with the seat's partial work, committed unchanged). Parent: `315364b2`. Main: `97082508`. Base (the commit S1 branched from): `1417c0c4`.
Charge: `60-s1-fix3/20-coldgate-charge.md`, committed at `ccf9aa9b` (checked: `git log -1 ccf9aa9b` names the charge).
Session: one session, no subagents. No repository file edited: `git status --short` in the working tree printed 0 lines after every probe. Scratch: `/tmp/cg_s1ret/`. Session clock: started 05:57:17 local; last probe ended 06:10:37; this file written after that (budget 35 minutes).

---

## 0. Contamination disclosure and protocol deviations (written first)

The charge told me not to read `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAUDE*.md`, `AGENTS.md`, the decision log, or memory or skill files. I opened none of them. These exposures happened anyway:

1. **Placed in my context by the harness before the charge arrived:** the owner's global `CLAUDE.md` (a pointer to orchestration doctrine, and a writing standard), this working tree's `CLAUDE.md` (notes on the bridge to a second model), the memory index `MEMORY.md` (about 110 one-line summaries), and the names of installed skills. One index line says that a measurement window is armed for a stated time today, that "SAMESIG ruled (steps 13-19 owed)", and that a "cooldown-anchor lane" comes "before next scored campaign". I opened no file any line points to and invoked no skill. I did **not** use the index to decide anything. Every order I rule is stated against "S1's merge" and "the next scored campaign" in general, and rests on no belief about what is armed or running.
2. **File names seen, files not opened.** One `ls` of the earlier judge's export of main (`/tmp/cg_samesig_err/main_tree`) printed the names `AGENTS.md`, `AGENT_PLAN.md`, `CLAIMS_STATUS.md`, `CLAUDE.md`, `LICENSE`. I opened none.
3. **Earlier rulings I opened, to quote amendment text exactly:** the round-1 erratum, lines 385 to 412 (amendment 51 (f), (g), (h)); the round-2 erratum, lines 376 to 409 (amendment 58 (f)), and three single lines found by `grep` (its lines 391, 480, 512; and line 606 of the round-1 erratum).
4. **The rulings I apply and I are the same model.** That is a shared-blind-spot risk. Against it: every disposition below rests on a line I quote or a probe I ran, and one of them goes against the seat's reading and the ruled text together (the kinds table has no place for a function that parses power and returns only problem strings, §5.2).

The writing standard in the global `CLAUDE.md` asks that every term be defined at first use. The charge asks the same of the summary. I followed it. It changes wording, not rulings.

**Protocol deviations, stated.**
- The protocol says no background tasks. One probe (the two inventory tests of the sweep, R12) ran 118 s, longer than the harness's limit, and the harness moved it to the background by itself. I started nothing in the background, and used its output only after it had exited.
- One command used the shell tool `timeout`, which this machine does not have (exit code 127). Nothing ran under it. I re-ran the probe without it.

**What I read.** The charge; the SAMESIG ruling and its erratum, in full; the seat's report, in full; the amendment texts of item 3; in the tree, the functions named in §2. **Not read:** the fix-round-3 brief (`10-fix-brief.txt`); the round-1 and round-2 rulings beyond the quoted lines; FT §E's text.

---

## 1. Terms used in this ruling

Each term is defined once. Terms marked (R) are those of the two rulings I apply, repeated so this file stands alone.

- **Bundle** (R). The directory one measured run leaves behind. It holds `metadata.json` (what ran, and two battery readings), `summary_metrics.json` (the reduced numbers, energy included), `power_trace.csv` (the power samples), and other files.
- **Charging bundle** (R). A bundle whose battery readings show current flowing into the battery during the run. Its energy and power numbers cannot be trusted.
- **The gate, bundle forms** (R). The check that a bundle's battery readings pass. **Window form:** the function `authenticate_window_members(members)`, which returns all verdicts or raises. **Reader form:** the method `BundleReader.metadata()`.
- **Energy-class value** (R). An energy, power, current, charge or voltage value, or a value computed from one.
- **The sweep** (R). The test `tests/test_bfgs_consumer_sweep.py`. It parses tracked Python files and lists every **read site**: a place that reads one of the three **watched files** (`summary_metrics.json`, `metadata.json`, `power_trace.csv`) or calls a tolerant accessor (a reader method that returns a file's content without the battery check), with no gate call before it. Each listed place is a **row** and must have an entry in the test's **allowlist**, with a **class** (a named reason category whose condition the row must meet).
- **Raw capture** (R). The power meter's own output, stored as the meter wrote it (`raw/powermetrics*.plist`, `raw/nvidia_smi*.csv`). Every energy number is computed from it.
- **Raw-capture inventory** (R). The sweep's closed mapping `RAW_CAPTURE_READERS`: every function that names a raw capture (48 at this tree), each with a **kind** that says what the function does with the capture. A function in the mapping is a **member**.
- **Claim artifact** (R). A file a paper number is taken from or licensed by.
- **Consumer** (R). One of the eight modules that turn bundles into claimed numbers (listed in §9).
- **Dominates** (R). Said of a gate call and a later statement: execution cannot reach the statement unless the gate call ran and returned normally.
- **Counterfactual** (R). For a test row: the specific wrong implementation under which the row must fail. A row **goes RED** when it fails and is **GREEN** when it passes.
- **Stop rule, A1 to A5** (R). The five conditions of amendment 61 (c) that end the review of the sweep. A2 is "the reported rows equal the allowlist, and every entry has a true class or kind". A3 is "no energy-class value reaches a claim artifact without a gate, on the routes through the eight consumers and through the envelope gate".
- **The seat, the refuter, the lead** (R). The model session that implements fix round 3; the model that checks the result; the session that commits and merges.
- **WRITE_SCOPE** (R). The closed list of files a seat may edit in one round.
- **Aborted attempt.** New here. A bundle of a run that stopped during its idle measurement, before any workload ran, because the machine failed the check that it was quiet. It holds no energy result.
- **Salvage license.** New here. The record that `joulewise/salvage_dangler.py` builds from an aborted attempt. It lets a campaign treat that one attempt as excluded, where otherwise the window would count as having a member missing.
- **Leaves.** New here (amendment 72). A value leaves a function when the function returns it, writes it to a file, stores it on an object that outlives the call, or puts it in the message of an exception it raises.
- **Tested and dropped.** New here (amendment 72). Said of a field whose value a function only checks (is it null; does it parse as a number; is it finite) and then discards. What leaves is one fact, pass or fail.
- **Calibration capture.** New here. A run in which the machine is made to draw power in timed pulses, so that the meter's clock can be lined up with the machine's clock. Its result is the **fiducial bound** (`b_fiducial_s`): a number of seconds that bounds how far the two clocks can disagree. The bound is a time, and it is computed by fitting the pulse edges in the power samples.
- **Capture directory.** New here. The directory a calibration capture leaves behind: `manifest.json`, `instrument_evidence.json`, `events.jsonl`, `raw/powermetrics.plist`, and, for captures recorded since the battery check exists, two battery readings. It is **not** a bundle, and neither bundle form of the gate applies to it.
- **The gate, capture form.** New here as a ruled form (amendment 74). The function `battery_float.authenticate_capture(directory)`. It returns a verdict whose `status` is `pass` when the capture directory's battery readings pass.
- **Validation shape.** New here (amendment 73). A function whose return annotation is exactly `list[str]`, `tuple[str, ...]`, `set[str]` or `bool`.

---

## 2. Executed evidence (this session, working tree `8953c7a5`, Python 3.14, `PYTHONDONTWRITEBYTECODE=1`)

| Id | Probe | Result (exact) |
|---|---|---|
| R1 | `git rev-parse HEAD`; `git diff --stat 315364b2 8953c7a5`; the diff of `joulewise/envelope_gate.py` | `8953c7a5e1df…`. Two files changed: `joulewise/envelope_gate.py` (9 lines), `tests/test_bfgs_consumer_sweep.py` (1686 lines). The envelope diff holds the helper `_gated_summary` (`reader.metadata()` then `return reader.raw_summary()`) and two replaced calls, and nothing else: amendment 63 (a) as ruled. |
| R2 | `git diff --stat 97082508 8953c7a5` and `git diff --stat 1417c0c4 8953c7a5`, over the 11 files that hold the returned functions | Changed against main and against base: `joulewise/calibration_bracketing.py` (109 lines added), `joulewise/controller.py` (74 added). **Unchanged against both:** `salvage_dangler.py`, `cli.py`, `reduce.py`, `environment_admission.py`, `powermetrics_fiducial.py`, `check_paper_replay_fence.py`, `paper_anchor_correction_quantified.py`, `paper_excursion_decomposition.py`, `validate_powermetrics_fiducial.py`. |
| R3 | `salvage_probe.py`: the production function `inspect_preworkload_abort`, unpatched, on copies of the repository's fixture `tests/fixtures/salvage_dangler/r5a_idle_abort` (prepared as `tests/test_salvage_dangler.py:83-101` prepares it) | **S1, fixture:** returned a license with 9 keys: `failure_reason`, `failure_signature_sha256`, `failure_timestamp_s` 100.0, `license_branch`, `licensed` true, `teardown_s` 0.171, `telemetry_first_timestamp_s` 99.8, `telemetry_last_timestamp_s` 100.171, `terminal_stage`. **S2, every `power_w` of the trace replaced by `power_w × 1000 + 7`:** the same license, `equal: True`. **S3, every number inside the summary's `idle_baseline` set to 9999:** `equal: True`. **S4, `gross_energy_j: 12.5` added to the summary:** `RAISED SalvageAuthorizationError: failed attempt contains measurand bytes`. **S5, one `power_w` set to `nan`:** `RAISED SalvageAuthorizationError: power trace numeric evidence is invalid`. **The bundle gate on the fixture:** `battery_float_evidence_missing` (`pre evidence missing: phase not recorded`, the same for post). |
| R4 | Read of `joulewise/salvage_dangler.py:634-834` and `:140-185` | Quoted in §4. |
| R5 | `members.py`: for each of the 12 returned members, by AST: the lines that name a capture, the gate-like calls, the return annotation, the callers | Gate-like calls: **one**, `authenticate_capture` at `controller.py:448`; none in the other 11. Annotations: the three `cli.py` members `list[str]`; `_window_thermal_pressure_refusals` `tuple[str, ...]`; `_verify_instrument_calibration` `tuple[float | None, str | None]`; `_load_calibration_candidate_unbounded` `CalibrationCandidate | None`; the script members `dict[...]` and `int`. Callers: listed in §5. |
| R6 | `dom.py`: statement positions, by AST | `controller._load_instrument_calibration_attachment`: statement 16 of the function's own body is the assignment at `:448`; statement 17 is `if verdict.status != 'pass':` with a body that ends in `raise`; the only statement that names a capture is statement 26 (the `try` at `:489-498`). `whole_window…_prepare`: the gate call `authenticate_window_members` is statement 8 of the body (`:680-682`); the call of `_verify_instrument_calibration` (`:788`) is inside statement 22. `_current_core_rederivation_reasons`: annotation `set[str]`; its only return expression is `reasons`. The four validation-shaped members: every `return` is a list or tuple literal, the name `problems`, or the call `_compare_raw_derived_samples(…)`. |
| R7 | `cal.py`: the call chain above `_load_calibration_candidate_unbounded`, by AST over the 209 tracked files under `joulewise/` and `scripts/` | One chain, no branch: called in `load_calibration_candidate.inspect` (`:1540`); `load_calibration_candidate` called once, in `_candidate_from_observation` (`:1686`); that called once, in `discover_calibration_candidates` (`:1911`), where `_battery_exclusion_for_observation` is called at `:1909`. References to any of the names: none. `_battery_exclusion_for_observation` calls `_battery_classification_for_observation` (`:1863`), which calls `battery_float.authenticate_capture` (`:1854`). |
| R8 | Read of `calibration_bracketing.py:1893-1915` | `if _battery_exclusion_for_observation(observation) is not None: continue` is followed directly by `candidate = _candidate_from_observation(observation, mode=mode)`. |
| R9 | The earlier judge's `f1_probe.py` (SHA-256 prefix `186e2a466569e861`, the value the SAMESIG erratum records), unchanged, on this tree; then on the export of main | **This tree:** the gate refuses bundle `C` (`battery_float_confounded`); `evaluate_member(C)` returns idle power `9.99`; `_first_eligible_cooldown_anchor` gives `bundle_id 'C'`, `9.99`; `prior_campaign_cooldown_anchor -> ('C', 9.99)`; with a meter reading 5.0 W: `result=recovered … reference_power_w=9.99 effective_upper_w=10.989 waited_s=30.0`, reasons `[]`; with 0.2 W in the anchor: `cap_hit`, `waited_s=300.0`, `['cooldown_cap_hit']`; with no anchor: `unknown`, `['campaign_cooldown_evidence_missing']`. **Main:** `diff` of the two outputs shows **one** differing line: main's `joulewise/bundle_read.py` has no `authenticate_window_members`. |
| R10 | `git diff 97082508 8953c7a5 -- scripts/run_campaign.py`, counting changed lines that hold `anchor`, `idle_baseline` or `cooldown`; `git diff --stat 315364b2 8953c7a5` over `run_campaign.py`, `cooldown_anchor.py`, `campaign_provenance.py` | `0` changed lines. No file listed. |
| R11 | The fences: `shasum`; `git diff --quiet 1417c0c4 8953c7a5` for three files; an import search over the eight consumers | `battery_float.py` hashes to prefix `4b4d7bb20625`; it, `reduce.py` and `bundle.py` are identical to base; each of the eight consumers holds 0 lines that import `battery_float`. |
| R12 | `python3 -B -m unittest` on the two tests the seat reports failing: `…ConsumerSweepTests.test_all_supported_ungated_reads_have_checked_reasons` and `….test_raw_capture_inventory` | `Ran 2 tests in 118.124s`, `FAILED (failures=2)`. The first names two unlisted reads, both in `joulewise/salvage_dangler.py`; the one printed in full is `('joulewise/salvage_dangler.py', '_inspect_preworkload_abort', 'direct:_read_json_object', 'summary_metrics.json')`. The second lists unlisted raw-capture readers. The seat's report reproduces. |

**Limits of the probes, stated so they are plain.**
- R3 uses one fixture, an aborted attempt recorded before battery readings existed. It shows which values leave the function. It does not show what a salvage license does inside a whole campaign: `authorize_salvage_dangler_exclusion` and `run_campaign` were read (`run_campaign.py:5881-5903`), not run.
- R5, R6 and R7 match by name and by position in the syntax tree. They do not run the functions.
- R9 calls the campaign script's functions in the script's order with a fake meter. It does not run two whole campaigns.
- R12 runs the seat's sweep. I did not re-implement the seat's detector, and I did not run the rest of the sweep's tests.

---

## 3. Rulings at a glance

| Item | Ruling |
|---|---|
| **1. Two watched reads in `salvage_dangler.py`** | **Class `non_claim`, clause (i), under a corrected text of that clause** (amendment 72). No energy-class value leaves either function: executed (R3, S2 to S5). Test-only. No gate is added: the bundle gate refuses the repository's own aborted-attempt fixture for missing readings (R3), so a gate there is a production decision that no evidence here asks for. |
| **2. Twelve raw-capture members** | **Four get a new kind, `validation`** (amendment 73): the three `cli.py` verifiers and the thermal-pressure function return only problem or refusal strings. **Eight stay kind `energy`:** a fiducial bound is computed from power samples, and the project itself runs a battery check on calibration captures. Of the eight, **three are gated today** and get a checkable gate value (amendment 74): the controller's attach function, the calibration candidate loader, and the reducer's calibration verifier. **Five are script functions with no gate**; they are unchanged since main, lie on no route through a consumer, and go to lane BFGS-RAWCAPTURE-01 with a closed list (amendment 75). |
| **3. The 64 (b) conflict** | **Disposed by amendment 66.** The seat's probe and the earlier judge's probe show the same route; I re-ran the latter on this tree and on main (R9, R10). The three `evaluate_member` rows stay `behind_gate`. Their reason text, which says something false, is replaced (amendment 76). Lane BFGS-COOLDOWN-ANCHOR-01, order as ruled. |
| **Production code** | **None is ruled inside S1.** Every step in §7 edits test files only. |
| **Blocks S1's merge** | Nothing in the three returns, once §7 is applied and GREEN. |

None of the three returns is a form of the deliberate class (code that reaches into the gate's own machinery, amendment 61 (b)). Each is ordinary code that exists in the tree today.

---

## 4. Item 1: the two watched reads in `joulewise/salvage_dangler.py`

### 4.1 The forcing problem

The sweep reports every read of a watched file that has no gate before it, and each report needs a class. Two reads in the module that builds salvage licenses fit none as the classes are written. The seat was right to return them:

- `non_claim` clause (i) says "no field the function **reads** from the file is an energy, power, current, charge or voltage value". Both functions do read such fields.
- `non_claim` clause (ii) says nothing the function returns is consumed by a claim artifact. The license reaches `authorize_salvage_dangler_exclusion`, which `run_campaign.py:5891` calls while it decides a window's membership.
- `strict_validation` allows a digest, a boolean, an identity string or problem strings. The license holds timestamps.

### 4.2 What the two functions do with the energy-class fields (quoted)

**`_inspect_preworkload_abort`, `summary_metrics.json`** (`salvage_dangler.py:776-779`):

```python
if summary.get("status") != "failed":
    raise SalvageAuthorizationError("summary status is not failed")
if any(summary.get(field) is not None for field in _MEASURAND_FIELDS):
    raise SalvageAuthorizationError("failed attempt contains measurand bytes")
```

`_MEASURAND_FIELDS` (`:159-179`) holds 17 names, among them `gross_energy_j`, `idle_subtracted_energy_j`, `energy_request_j`, `phase_energy_j`. The function requires each to be **null**. Every other key must be null or be one of six names (`:180-189`), of which one, `idle_baseline`, can hold an idle power; the function tests that key's presence and never takes its value. The one summary field whose value goes into the license is `failure_reason`, a string (`:790`, `:828`).

**`_telemetry_timestamp_bounds`, `power_trace.csv`** (`:671-697`):

```python
timestamp = float(row["timestamp_s"])
power_w = float(row["power_w"])
...
if not all(math.isfinite(value) for value in (timestamp, power_w, interval_start, interval_end)) ...
    raise SalvageAuthorizationError("power trace numeric evidence is invalid")
...
timestamps.extend((timestamp, interval_start, interval_end))
...
return min(timestamps), max(timestamps)
```

`power_w` is parsed, tested for being finite, and dropped. Two times are returned.

### 4.3 Worked example (executed, R3)

| Input | Output |
|---|---|
| the fixture (trace holds `power_w` 0.2) | a license: failure at 100.0 s, telemetry from 99.8 s to 100.171 s, teardown 0.171 s |
| every `power_w` replaced by `power_w × 1000 + 7` | **the same license, key for key** |
| every number in the summary's `idle_baseline` set to 9999 | **the same license** |
| `gross_energy_j: 12.5` added to the summary | refused: `failed attempt contains measurand bytes` |
| one `power_w` set to `nan` | refused: `power trace numeric evidence is invalid` |

A power value changed by a factor of a thousand changes nothing that leaves. An attempt that holds an energy result cannot be licensed at all.

### 4.4 Ruling, and why

The purpose of clause (i) is that no energy-class value of an unchecked bundle travels on. The word "reads" says more than that purpose needs, and it fails two functions whose whole job is to confirm that an attempt holds **no** energy. I correct the word, and I do not add a class.

**Why no gate is ruled.** A salvage license concerns an attempt that measured nothing. Whether its battery was charging cannot distort a number, because it has none. The bundle gate, run on the repository's own fixture, returns `battery_float_evidence_missing` (R3): gating the license would refuse every aborted attempt recorded before battery readings existed. That is a change of what the project can salvage, and no evidence before me asks for it.

**What stays true.** The license is an exclusion decision about a bundle that is not a member of the window, so the window's gate never sees that bundle. That shape is the same as the cooldown anchor's (item 3). The difference is what travels: there an idle power, here two times, a string and digests. If a later change makes the license carry an energy-class value, row R72-1 goes RED.

### Amendment 72 (amends the class table of 51 (f), clause (i) of `non_claim`)

72. **Clause (i) speaks of what leaves the function.**

**(a) Clause (i) is replaced by:**

> (i) no energy-class value that the function reads from the file, and no value computed from one, **leaves** the function. A value leaves a function when the function returns it, writes it to a file, stores it on an object that outlives the call, or puts it in the message of an exception it raises. A field whose value the function only **tests** (is it absent or null; does it parse as a number; is it finite) and then drops does not leave.

**(b) The reason of a row under (i)** states the fields whose values leave. If the function tests and drops an energy-class field, the reason also states: "tested and dropped: `<fields>`, test: `<the test>`". Rows granted before this amendment keep their reasons.

**(c) Two rows, granted by this gate.**

| Key | Class | Reason (exact) |
|---|---|---|
| `("joulewise/salvage_dangler.py", "_inspect_preworkload_abort", "direct:_read_json_object", "summary_metrics.json")` | `non_claim` (i) | "fields that leave: `failure_reason`; tested and dropped: `status`, the 17 names of `_MEASURAND_FIELDS`, every other key; test: `status` equals `failed`, each measurand is null, each other key is null or named in `_ALLOWED_FAILED_SUMMARY_NONNULL`" |
| `("joulewise/salvage_dangler.py", "_telemetry_timestamp_bounds", <operation>, "power_trace.csv")` | `non_claim` (i) | "fields that leave: `timestamp_s`, `interval_start_s`, `interval_end_s`, as their minimum and maximum; tested and dropped: `power_w`, `source`, `rail`; test: `power_w` parses as a number and is finite, `source` and `rail` hold no workload marker" |

`<operation>` is the operation the seat's detector reports for the read at `:641` (the call `open_authentication_input`). The test's output printed that key shortened (R12), so I do not write it from memory.

**Test rows for amendment 72.**

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R72-1 | `salvage_dangler._telemetry_timestamp_bounds`, called at `salvage_dangler.py:802` | a copy of the fixture `tests/fixtures/salvage_dangler/r5a_idle_abort`, prepared as `tests/test_salvage_dangler.py:83-101` does; then the same with every `power_w` replaced by `power_w × 1000 + 7` | the two results of `inspect_preworkload_abort` are equal | a function that puts a value computed from `power_w` into the license, for example a key `mean_power_w`. GREEN on the tree: executed (R3, S2). The mutation: NOT EXECUTED. |
| R72-2 | `salvage_dangler._inspect_preworkload_abort`, the test at `:778` | the fixture with `gross_energy_j: 12.5` added to its summary | `SalvageAuthorizationError` | a function without the test of `_MEASURAND_FIELDS`, which returns a license for an attempt that holds energy. GREEN on the tree: executed (R3, S4). The mutation: NOT EXECUTED. |
| R72-3 | the allowlist | the allowlist | every `non_claim` row whose reason holds "tested and dropped" also holds "fields that leave:" and "test:" | a reason that says "tested and dropped" and names no test |

---

## 5. Item 2: the twelve raw-capture members

### 5.1 The forcing problem

The raw-capture inventory has four kinds: `names`, `custody`, `timing`, `energy`. A member of kind `energy` needs a gate. The only gates the ruled text knows are the two **bundle** forms. Eleven returned members parse power samples, so the seat called them `energy` and found no bundle gate. The twelfth parses a label that is not a time and not an energy.

Reading the twelve shows three different things under one label:

1. functions that parse power only to **compare** it with what the bundle stores, and return problem strings;
2. functions that read a **capture directory**, which is not a bundle, so that no bundle gate could ever apply;
3. among those, some that the project already protects with the **capture form** of the gate, which the sweep does not know.

### 5.2 Is a fiducial bound an energy-class value? Yes

The charge asks whether reading the capture "for the timing fiducial or calibration rather than for claim energy" makes a member non-energy. **It does not.** Two reasons.

1. **By the definition.** An energy-class value includes "a value computed from" a power value. The bound is computed by refitting the pulse edges in the power samples. `powermetrics_fiducial.py:1300-1305` and `:1353`:
   ```python
   fresh = rederive_detection_from_artifacts(raw_powermetrics, events_jsonl, evidence.get("clock_anchor"), protocol_id=...)
   ...
   return max(float(stored_bound), float(fresh.b_fiducial_s))
   ```
   The kind `timing` is for a function that "uses **only** times, durations or sample counts". These use the power samples.
2. **By the project's own practice.** S1 runs a battery check on calibration captures before it uses them: `controller.py:448` refuses to attach a capture whose verdict is not `pass`, and `calibration_bracketing.py:1909` excludes a capture whose status is `battery_float_confounded` or `battery_float_evidence_missing`. A kind ruled here must not say the opposite of what the code enforces.

I did **not** execute a probe that shows how far a charging battery moves a fitted pulse edge. NOT EXECUTED. The ruling rests on the definition and on the code's own gates.

**What does make a member non-energy** is what leaves it. A function that parses power, compares, and returns only strings that name a problem hands no energy-class value to anyone. The kinds table has no place for that. The class table for watched files has one (`strict_validation`), and the three `cli.py` members already hold rows of that class for their metadata reads (rows 26 to 37 of the seat's allowlist). Amendment 73 gives the raw-capture inventory the same place.

### 5.3 The twelve, one by one

"Leaves" is quoted from the function's `return` statements (R5, R6, and the lines named).

| # | Member | What it reads | What leaves | Kind | Gate | Finding? |
|---|---|---|---|---|---|---|
| 1 | `cli.py::_verify_powermetrics_raw_to_trace` (`:1493`) | a bundle's raw capture, re-derived into samples and compared with `power_trace.csv` | `list[str]`: problem strings (`:1496`, `:1499`, `:1540`, `:1541`) | **`validation`** | none needed | no |
| 2 | `cli.py::_strict_rich_telemetry_problems` (`:1568`) | the same, compared byte for byte with the stored telemetry file (`:1622`) | `list[str]` | **`validation`** | none needed | no |
| 3 | `cli.py::_strict_uncertainty_evidence_problems` (`:1219`) | three raw captures of a bundle | `list[str]` | **`validation`** | none needed | no |
| 4 | `environment_admission.py::_window_thermal_pressure_refusals` (`:279`) | two raw captures; of each record it uses the start, the end, and the thermal-pressure label (`:366-377`) | `tuple[str, ...]`: `()`, `("environment_admission_missing",)` or `("thermal_pressure_elevated_in_window",)` | **`validation`** | none needed | no |
| 5 | `controller.py::_load_instrument_calibration_attachment` (`:370`) | a capture directory, at the moment a run attaches it to a new bundle | the attachment, with `verified_effective_b_fiducial_s` (`:507`) | `energy` | **`"capture_in_function"`**: the capture gate at `:448-450` precedes the only parse, at `:490` (R6) | no |
| 6 | `calibration_bracketing.py::_load_calibration_candidate_unbounded` (`:1545`) | a capture directory | `CalibrationCandidate` with `b_fiducial_s` (`:1666-1674`) | `energy` | **capture chain**: one chain of callers, ending where the battery exclusion directly precedes the call (R7, R8) | no |
| 7 | `reduce.py::_verify_instrument_calibration` (`:1171`) | the copy of a capture directory that a bundle carries under `instrument_calibration/` | `tuple[float | None, str | None]`: the bound, or a refusal detail | `energy` | **`callers`**, three functions (§5.4) | no, if row R74-3 is GREEN |
| 8 | `scripts/check_paper_replay_fence.py::derive_from_artifacts` (`:401`) | one capture directory, named in committed code (`:83`) | a dictionary of bounds and residuals in seconds (`:509-528`) | `energy` | none: **lane** | yes, routed (§5.5) |
| 9 | `scripts/paper_excursion_decomposition.py::rederive` (`:212`) | the same directory (`:85`) | the detection, the anchor, the evidence (`:266-272`) | `energy` | none: **lane** | yes, routed |
| 10 | `scripts/paper_anchor_correction_quantified.py::analyse_capture` (`:444`) | a capture directory given by its caller | a row of bounds and their differences (`:533-559`) | `energy` | none: **lane** | yes, routed |
| 11 | `scripts/validate_powermetrics_fiducial.py::rederive_artifact` (`:1239`) | a capture directory | writes a new evidence file with a re-derived bound (`:1329-1331`) | `energy` | none: **lane** | yes, routed |
| 12 | `scripts/validate_powermetrics_fiducial.py::main` (`:1800`) | the capture it records in the same call; it takes the two battery readings itself (`:2269-2270`, `:2498`) | writes the capture directory | `energy` | none: **lane** | yes, routed |

**On member 4.** The seat is right that no ruled kind fits: a thermal-pressure label is not a time. It is also not an energy-class value (the definition lists energy, power, current, charge, voltage). The function hands the parsed records to a routine that rebuilds the clock anchor, and those records carry power fields (`adapters/powermetrics.py:1853-1854`). I did not trace whether that routine uses them. NOT EXECUTED. The kind `validation` does not depend on the answer, because it is decided by what leaves: three fixed strings.

**On what a `validation` member's strings do.** Some become reasons to exclude a member. The ruled order "authentication precedes every exclusion decision" is kept by the consumers, where the gate call precedes the assignment of any reason (the round-1 erratum, line 606). This ruling changes no production line, so that order is as it was. The refuter's A3 pass reads it; I did not.

### 5.4 Member 7: the reducer's calibration verifier

`reduce.py` is a frozen file, so no gate can be written into it. Its three callers (R5, R6):

| Caller | How the chain closes there |
|---|---|
| `reduce.py::_derive_anchor_context` (`:1820`) | it is itself a member of kind `energy` with a `callers` gate, in the seat's mapping |
| `whole_window.py::AuthenticatedConsumptionSession._prepare` (`:788`) | the window-form gate at `:680-682` is a statement of the function's own body and comes before the loop that holds the call (R6) |
| `whole_window.py::_current_core_rederivation_reasons` (`:4585`) | no gate. The bound is compared with two stored numbers (`:4603-4611`), and the function returns `reasons`, a `set[str]` (R6). The value does not leave. |

The third caller is why the seat found "no qualifying gate": the ruled callers form accepts a dominating gate or a `behind_gate` row, and nothing else. Amendment 74 (c) adds the two closures that are true here.

**A limit, stated.** The gate at `:680` is the **bundle** gate. It checks the battery readings of the run. The capture a bundle carries has battery readings of its own, and they are checked when the capture is attached (`controller.py:448`), not again at reduction. Whether a bundle can pass the bundle gate while it carries a capture whose own readings fail or are absent, I did not trace. NOT EXECUTED. It is an item of the refuter's A3 pass and of lane BFGS-RAWCAPTURE-01 (§5.5, item 5). It is not a reason to hold the inventory RED: the file that would change is frozen.

### 5.5 Members 8 to 12: the script functions, and lane BFGS-RAWCAPTURE-01

**What they are.** Five functions in four scripts. Three re-derive the paper's numbers about the meter's timing from a capture that committed code names: `runs_window_a_20260722/instrument_validation/<MEMBER_ID>` (`check_paper_replay_fence.py:83`, `paper_excursion_decomposition.py:85`). Two belong to the script that records calibration captures.

**Are they failures of A3?** No. A3 covers the routes through the eight consumers and through the envelope gate. None of the five is called from a consumer (R5: their callers are their own `main` or `build_payload`, and `arm_readiness._run_under_lease_rehearsal` for the recording script). They are failures of the **inventory**: members of kind `energy` with no gate.

**Do they block S1's merge?** The SAMESIG ruling says a member of kind `energy` with no gate does. I rule that these five do not, on the reasoning of the erratum's §4.5, with the facts executed:

1. **S1 changed none of them.** All four files are byte-identical to main and to base (R2).
2. **Holding S1 back removes nothing.** The five functions are the same on main, where no battery check exists at all.
3. **What the recording script produces is gated where it is used.** A capture directory enters a measured run through `controller.py:448` and a calibration bracket through `calibration_bracketing.py:1909`. Both are gated by the capture form (R6, R8).
4. **The capture the paper scripts read was recorded in July,** before battery readings existed. No gate can be run on it. Whether the paper pins it as a historical capture, or states a limitation, is a decision about the paper, and S1 changes nothing about it.

**What keeps this from becoming a way to wave findings through:** the list is closed (five members, by name), the sweep fails if a sixth member takes the lane value, and the sweep fails if any of the four files changes (row R75-2), which sends the member back to a cold gate.

**The lane.** BFGS-RAWCAPTURE-01 changes production code. It gets its own cold gate. I rule its items and its order, not its code.

| Item | Question the lane answers |
|---|---|
| 1 | Members 8, 9, 10: is the capture pinned so that the scripts cannot be pointed at a later one (a digest in committed code, or a corpus that a committed artifact names)? If yes, a `historical` gate value. If no, the capture form of the gate. |
| 2 | Member 12: it records the capture it parses. Is it excluded from the inventory as the meter adapters are, which write the capture? |
| 3 | Member 11: the capture form of the gate before the refit. |
| 4 | Carried from the SAMESIG erratum: `docs/paper/figures/reproduce_worked_examples.py::historical`. |
| 5 | From §5.4: is the capture form of the gate run again on the capture a bundle carries, and where, given that `reduce.py` is frozen? |

**Order.**
- The lane opens when S1 merges. The description of S1's merge names it and this order.
- **Against the next scored campaign: no constraint.** None of the five is on a campaign's path (R5), and a capture enters a campaign only through the two gated sites of point 3.
- **Against the paper:** the lane merges before any of members 8 to 11 is run on a capture recorded after battery readings existed, and before the paper's numbers about the meter's timing are frozen for submission.
- **Until then:** before running one of members 8 to 11 on a capture directory that holds battery readings, the lead runs `battery_float.authenticate_capture(<directory>)` and records the verdict in the trace. The script runs only on `pass`. For the July capture, which holds no readings, the paper states that its battery state was not recorded.

### Amendment 73 (adds a kind to the table of 58 (f) 4)

73. **The kind `validation`.**

**(a) The kinds table gains the row:**

| Kind | The function | Second field |
|---|---|---|
| `validation` | parses the capture, and every value that leaves it is a boolean, a digest, an identity string, or a list, tuple or set of strings that name a problem or a refusal | none |

**(b) The sweep asserts,** for every member of kind `validation`, that the function has validation shape: its return annotation is exactly `list[str]`, `tuple[str, ...]`, `set[str]` or `bool`. **The refuter checks by reading** that the function writes no file and stores nothing on an object that outlives the call, and that no tracked caller parses a number out of one of its strings.

**(c) Four members take the kind:** `joulewise/cli.py::_verify_powermetrics_raw_to_trace`, `joulewise/cli.py::_strict_rich_telemetry_problems`, `joulewise/cli.py::_strict_uncertainty_evidence_problems`, `joulewise/environment_admission.py::_window_thermal_pressure_refusals`.

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R73-1 | the four members of (c) | (i) the tree; (ii) `joulewise/cli.py` with the annotation of `_verify_powermetrics_raw_to_trace` changed, in memory, to `-> list[float]` | (i) passes (annotations executed, R5); (ii) the sweep fails, naming the function | a kind with no check, under which a function that returns power values keeps the kind. The mutation: NOT EXECUTED. |

### Amendment 74 (amends 58 (f) 4 and 5: the capture form of the gate, and how a chain of callers closes)

74. **A member that reads a capture directory is gated by the capture form.**

**(a) In the kinds table,** the second field of `energy` becomes: "`gate`: the string `"in_function"`, the string `"capture_in_function"`, a `callers` tuple, or a capture chain".

**(b) 58 (f) 5 gains:**

> **`"capture_in_function"`.** The sweep asserts three things about the function's own body (the statements directly inside the `def`, not inside a branch or a loop): it holds a statement `<V> = battery_float.authenticate_capture(…)`; the next statement of the body is an `if` whose test is exactly `<V>.status != "pass"` and whose last statement is a `raise`; and every statement of the body that mentions a capture constant or a capture name comes after that `if`.
>
> **Capture chain,** written `("capture_chain", (f1, …, fn))`, each element a `path::qualified function`. The sweep asserts: every call of the member's name, and every reference to it (amendment 62 (b)), lies in `f1`; for each `k`, every call of and reference to the function `fk` lies in `fk+1`; in `fn`, the statement that holds the call of `fn-1` with a plain name `<X>` as its first argument is directly preceded, in the same body, by the statement `if _battery_exclusion_for_observation(<X>) is not None: continue`, with the same `<X>`; `_battery_exclusion_for_observation` holds a call of `_battery_classification_for_observation`; and that function holds a call of `battery_float.authenticate_capture`.

**(c) In the callers form, as it applies to raw-capture members,** a listed function closes the chain if one of three holds: a bundle-form gate call comes before and dominates the call (as ruled); the listed function is itself a member of kind `energy` that has a gate; or the listed function has validation shape (amendment 73 (b)). For the third, the refuter checks by reading that the value received from the member is compared and dropped.

**(d) Three members.**

| Member | Entry |
|---|---|
| `joulewise/controller.py::_load_instrument_calibration_attachment` | `("energy", "capture_in_function")` |
| `joulewise/calibration_bracketing.py::_load_calibration_candidate_unbounded` | `("energy", ("capture_chain", ("joulewise/calibration_bracketing.py::load_calibration_candidate.inspect", "joulewise/calibration_bracketing.py::load_calibration_candidate", "joulewise/calibration_bracketing.py::_candidate_from_observation", "joulewise/calibration_bracketing.py::discover_calibration_candidates")))` |
| `joulewise/reduce.py::_verify_instrument_calibration` | `("energy", ("joulewise/reduce.py::_derive_anchor_context", "joulewise/whole_window.py::AuthenticatedConsumptionSession._prepare", "joulewise/whole_window.py::_current_core_rederivation_reasons"))` |

If the seat's implementation of (b) or (c) fails on the tree for one of the three, the seat returns that member with the failing assertion. It does not change the entry and does not edit production code.

**(e) The two idioms of (b) are a closed list.** A third way of writing a capture gate needs a cold gate.

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R74-1 | `controller.py:448-450`, before the parse at `:490` | (i) the tree; (ii) the three lines removed, in memory; (iii) the test changed to `verdict.status == "confounded"` | (i) passes (positions executed, R6); (ii) and (iii) the sweep fails, naming the function | a check that looks for the name `authenticate_capture` anywhere in the function. Mutations: NOT EXECUTED. |
| R74-2 | `calibration_bracketing.py:1909-1911` | (i) the tree; (ii) the `if … continue` at `:1909-1910` removed, in memory; (iii) a file `joulewise/zz_new.py` holding `def f(d, r): return load_calibration_candidate(d, runs_root=r)` | (i) passes (chain executed, R7, R8); (ii) fails, naming `discover_calibration_candidates`; (iii) fails, naming `joulewise/zz_new.py::f` | a chain that is listed and not checked. Mutations: NOT EXECUTED. |
| R74-3 | `whole_window.py:680-682`, `:788`, `:4585` | (i) the tree; (ii) the gate statement at `:680-682` removed, in memory; (iii) the annotation of `_current_core_rederivation_reasons` changed to `-> dict[str, float]` | (i) passes; (ii) fails, naming `_prepare`; (iii) fails, naming `_current_core_rederivation_reasons` | a callers form that accepts any listed function. Mutations: NOT EXECUTED. |
| R74-4 | `calibration_bracketing.discover_calibration_candidates` and the bracket evaluator | the two tests that exist in `tests/test_bfgs_calibration_bracketing.py`: `test_confounded_ordinary_row_does_not_empty_discovery` (`:126`), `test_confounded_row_is_excluded_from_evaluator_universe` (`:147`) | both GREEN in V1, named in the seat's report | the exclusion removed. I did not run the two tests: NOT EXECUTED. |

### Amendment 75 (amends 58 (f) 6, §8.2 of the SAMESIG ruling, 51 (h); names five members)

75. **Five script members are routed to a lane, on a closed list.**

**(a) 58 (f) 6 is replaced by:** "A member of kind `energy` that has no gate is not given a gate by the seat. The seat returns it. A cold gate then rules one of two things. If the member lies on a route through the eight consumers or the envelope gate, amendment 66 (a) applies, rows 1b and 1c. If it lies on no such route and its file is byte-identical to main, it may take the entry `("energy", ("lane", "<lane name>"))`."

**(b) The sweep holds the constant `RAW_CAPTURE_LANE_MEMBERS`** and asserts that the set of members whose gate is a `("lane", …)` pair **equals** it. Its content, all with lane `BFGS-RAWCAPTURE-01`:

```python
RAW_CAPTURE_LANE_MEMBERS = {
    "scripts/check_paper_replay_fence.py::derive_from_artifacts",
    "scripts/paper_anchor_correction_quantified.py::analyse_capture",
    "scripts/paper_excursion_decomposition.py::rederive",
    "scripts/validate_powermetrics_fiducial.py::main",
    "scripts/validate_powermetrics_fiducial.py::rederive_artifact",
}
```

A sixth member needs a cold gate.

**(c) In §8.2 of the SAMESIG ruling, "Does block S1's merge",** the words "a raw-capture member of kind `energy` with no gate" become "a raw-capture member of kind `energy` with no gate, other than the five of amendment 75 (b)".

**(d) 51 (h) gains the item:** "**A calibration capture parsed by a script.** Five functions in four scripts under `scripts/` refit power pulses from a capture directory with no battery check (amendment 75 (b)). The capture directory is not a bundle, so no bundle gate applies. A capture enters a measured run or a calibration bracket only through the capture form of the gate (`controller.py:448`, `calibration_bracketing.py:1909`). Lane BFGS-RAWCAPTURE-01."

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R75-1 | the raw-capture inventory | (i) the mapping; (ii) the mapping with `joulewise/aggregate.py::zz_new` added with a `("lane", …)` gate | (i) passes; (ii) fails, naming the member | a lane value that any member may take |
| R75-2 | the four files of (b) | `git diff --quiet 97082508 -- <file>` for each. If the commit `97082508` is absent from the repository the test runs in, the row calls `skipTest` with the message `R75-2: commit 97082508 absent`; the seat's report and the lead's re-run show it **executed and passing**. | each file identical (executed, R2) | a change to one of the four files, after which its members are returned to a cold gate |

**The count.** 48 members: the 36 of the seat's mapping, 4 of kind `validation`, 3 of amendment 74, 5 of amendment 75. `RETURNED_RAW_CAPTURE_ENERGY` and `RETURNED_RAW_CAPTURE_UNCLASSIFIED` become empty and are removed.

---

## 6. Item 3: the 64 (b) conflict on `evaluate_member`

### 6.1 Does the seat's probe match amendment 66? Yes

The seat's probe printed: the source bundle refused (`battery_float_confounded`); the stored anchor reused (`selection= frozen_clean_anchor`); the result `cap_hit`; `readiness_has_cap_hit= True`. It stubbed the cooldown result to isolate the path. The earlier judge's probe drives the same five links with a fake meter. I re-ran that probe, unchanged, on the seat's tree (R9):

| Link | The seat's probe | R9 on `8953c7a5` |
|---|---|---|
| the gate refuses the source bundle | `REFUSED battery_float_confounded` | `battery_float_confounded` |
| `evaluate_member` keeps the idle power all the same | stated | returned, idle power `9.99` |
| the campaign stores it as the anchor, the next campaign reads it back with no gate | `anchor_reused= True` | `prior_campaign_cooldown_anchor -> ('C', 9.99)` |
| the anchor decides the cooldown result | `result= cap_hit` (stubbed) | `recovered` at 9.99 W, `cap_hit` at 0.2 W |
| the result becomes a reason on the next member | `readiness_has_cap_hit= True` | `['cooldown_cap_hit']` |

Same route, same links. The two probes differ only in the numbers they plant.

### 6.2 Is the route pre-existing? Yes, by the three things amendment 66 (a) requires

1. **A probe that drives the route:** R9, and the seat's.
2. **The same probe, unchanged, on main:** one differing line, and it is the line where main has no window gate at all (R9).
3. **No changed line on the route:** 0 changed lines that hold `anchor`, `idle_baseline` or `cooldown` between main and `8953c7a5`; the seat's commit touches two files, neither on the route (R1, R10).

Row 1c applies. **Amendment 66 disposes of the item.** It does not block S1's merge. Lane BFGS-COOLDOWN-ANCHOR-01 opens now and merges **before the next scored campaign starts**. Until it has merged, the pre-check that the SAMESIG erratum gives in full (its §4.6) runs before every scored campaign, and the campaign starts only on exit code 0.

### 6.3 What the seat still has to change

The three rows are right to stay `behind_gate`. Their **reason** is wrong. The seat wrote: "content should reach only the listed gated campaign chains". That is the claim R9 shows to be false, and a class whose reason "must state nothing beyond the third field" should not make it.

### Amendment 76 (the reason of the three `evaluate_member` rows)

76. **(a)** The three rows of amendment 64 (b) carry the class `behind_gate`, consumers form, with the fields `consumers` (64 (b)), `collection_uses` (66 (d)) and `producers` (67 (b)), and the reason, exact: "consumers form, amendment 66 (c); verdict uses are gated; collection uses are listed; `_first_eligible_cooldown_anchor` stores a value another campaign reads: lane BFGS-COOLDOWN-ANCHOR-01".
**(b)** Row R58-5 gains: "no reason in the allowlist holds the words `only to` or `reach only`".

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R76-1 | the three allowlist rows of `scripts/run_campaign.py::evaluate_member` | (i) the allowlist; (ii) the allowlist with the seat's reason of `8953c7a5` put back on one row | (i) passes; (ii) fails, naming the row | the allowlist at `8953c7a5`, whose reason states what the executed route contradicts |

---

## 7. The complete, ordered list the seat applies next

One seat. Working tree from `8953c7a5`. **Every step is test-only.** WRITE_SCOPE: the test files that fix round 3's WRITE_SCOPE already holds (the sweep, and the file that holds row R60-7). `joulewise/envelope_gate.py` is **no longer** in scope: amendment 63 (a) is done (R1). If a step seems to need any other file, the seat returns it.

Authority: amendment 51, as amended by 57 to 60, by 61 to 65, by 66 to 71, and by 72 to 76 (§4 to §6 above). Where two texts differ, the later one holds.

The steps are applied **in the order of the first column**. Steps 13 to 19 are those of the SAMESIG erratum, as written there unless a line here says otherwise.

| Order | Step | What | Rows to show RED under the counterfactual, then GREEN |
|---|---|---|---|
| 1 | 20 | **The two salvage rows** (amendment 72): clause (i) as replaced; the two rows of 72 (c) with their reasons. The read-site inventory is then GREEN: the reported keys equal the allowlist's keys. **Count: 117** (the seat's 115 rows and these 2). | R72-1, R72-2, R72-3 |
| 2 | 21 | **The kind `validation`** (amendment 73): the row of the kinds table, the check of 73 (b), four members. | R73-1 |
| 3 | 22 | **The capture form of the gate** (amendment 74): the two idioms, the closures of 74 (c), three members. | R74-1, R74-2, R74-3; R74-4 named |
| 4 | 23 | **The lane members** (amendment 75): the closed list, five members. The raw-capture inventory is then GREEN: 48 members. | R75-1, R75-2; R58-7, R58-8 re-run |
| 5 | 13 | The swept roots (68 (a) to (d)). | R61-1, R61-2 |
| 6 | 14 | The two rows under `docs/paper/` (68 (e)). **The count becomes 119** (117 and these 2), or up to 121 under 68 (e). The erratum's 120 was the prototype's count; the seat's detector counts one row fewer (§8). A different count is returned with the differing rows listed. | R51-27 re-run with the new count |
| 7 | 15 | The consumers form (66 (c), 66 (d), 67), **with the reason of amendment 76**. | R51-17b, R51-17c, R51-17d, R51-17e, R76-1; R51-17 re-run |
| 8 | 16 | Lambda and nested scopes under a gate (69). | R51-23b, R51-23c |
| 9 | 17 | Rule (d) 6 wording (71 (a), (b)); R60-7's skip clause (71 (c)). | R51-28 with input (e); R60-7 executed, not skipped |
| 10 | 18 | **Texts.** As the erratum states, and in addition: clause (i) of `non_claim` as replaced by 72 (a), in the class table the sweep's docstring holds; the item of 75 (d) in the list the test holds for 51 (h); 58 (f) 6 as replaced by 75 (a). | none: text |
| 11 | 19 | **Returns, and the suites again.** V1, V2, the builder's forward check and the three fences of A5, after step 18. V1 is expected GREEN: its two failures are the two inventories (R12), and orders 1 to 4 close them. | |

**Not applied by the seat:** lane BFGS-COOLDOWN-ANCHOR-01 and its pre-check, which the lead runs; lane BFGS-RAWCAPTURE-01; any change to `joulewise/salvage_dangler.py`.

**Then:** one refuter pass on the merge candidate, under the stop rule of 61 (c) as amended by 66. It gains three reading tasks, all inside the one pass: the four `validation` members against 73 (b); the third closure of 74 (c) at `_current_core_rederivation_reasons`; the limit of §5.4.

**The stop rule stays finite.** This ruling adds one kind, two gate idioms and one lane value. Each is a closed list or has a check the sweep runs. None is a rule about the deliberate class, and no form of that class was returned. A finding of the refuter pass is still handled by the table of 61 (c) as amended by 66 (a), in one pass.

**Lanes after this ruling.**

| Lane | What it does | Order | Blocks S1? |
|---|---|---|---|
| BFGS-COOLDOWN-ANCHOR-01 (ruled by 66) | the gate runs on a cooldown anchor's source bundle when the anchor is stored and when it is reused | opens now; merges before the next scored campaign starts; until then the pre-check before every scored campaign | no |
| **BFGS-RAWCAPTURE-01** (opened by this ruling; five items, §5.5) | the capture form of the gate, or a historical pin, for five script functions; the capture a bundle carries | opens at S1's merge; no constraint against the next scored campaign; merges before the paper's timing numbers are frozen | no |
| BFGS-READER-ROOT-01, BFGS-GATED-SUMMARY-01, BFGS-ENVELOPE-REASON-01, BFGS-MANIFEST-CUSTODY-01 | carried | unchanged | no |

---

## 8. The seat's count (its flag F4)

The seat's detector reports 117 rows after amendment 63 (a), and the prototype 118. The seat names the difference: a read inside the nested function `check_a3` of `scripts/check_window_provenance.py::_run_assertions`, which the prototype also reported under the enclosing function.

**Ruling: the seat's count stands.** Amendment 62 (a) gives a nested `def` its own scope and qualified name, and says no scope inherits from another. A read belongs to the scope whose body holds it. I did **not** run the prototype against the seat's detector: NOT EXECUTED. The refuter checks under A2 that the key for `_run_assertions.check_a3` exists and that `_run_assertions` holds no read of its own.

---

## 9. Kept intact

- **Custody is never a status.** No amendment here adds a status, a handler or a conversion. The capture gate idiom of 74 (b) tests the verdict's `status` and nothing else; a custody failure raised inside `authenticate_capture` leaves as an exception, as it does today. No production line changes.
- **Authentication precedes every exclusion decision.** No amendment here reorders production code. Two places where a decision to exclude rests on a bundle that the window's gate does not see are named, not hidden: the cooldown anchor (lane BFGS-COOLDOWN-ANCHOR-01), and the salvage license, where what travels is two times, a string and digests (executed, R3).
- **`joulewise/battery_float.py` and FT §E's excluded list stay byte-identical.** `battery_float.py` hashes to prefix `4b4d7bb20625`; it, `reduce.py` and `bundle.py` are identical to base (R11). This ruling edits no production file. I did not open FT §E's text.
- **The eight consumers do not import `battery_float`** (R11): `scripts/run_campaign.py`, `joulewise/whole_window.py`, `joulewise/analysis_engine/inputs.py`, `joulewise/floor_extraction.py`, `joulewise/aggregate.py`, `joulewise/window_duration_margins.py`, `scripts/mint_floor_artifact.py`, `scripts/extract_detection_floors.py`. `controller.py` and `calibration_bracketing.py` do import it; neither is one of the eight.

---

## 10. Not executed

- V1, V2 and the builder's forward check. Of the repository's tests I ran two (R12).
- Every mutation named as a counterfactual in rows R72-1, R72-2, R73-1, R74-1 to R74-3, R75-1, R76-1. The tree side of each is executed where the row says so.
- The two tests of row R74-4.
- A whole campaign with a salvage license. `authorize_salvage_dangler_exclusion` and its call site were read.
- How far a charging battery moves a fitted pulse edge (§5.2).
- Whether the routine that rebuilds the clock anchor uses the power fields of its records (§5.3, member 4).
- Whether a bundle can pass the bundle gate while it carries a capture whose own battery readings fail or are absent (§5.4).
- The pins of the three paper scripts beyond the two path constants quoted; `build_payload`, which chooses the directories for member 10.
- The body of `rederive_detection_from_artifacts`. I read its caller, `verify_stored_evidence_physics`.
- The prototype against the seat's detector (§8).
- The pre-check of the SAMESIG erratum's §4.6 on a real runs directory.
- The steps of §7. The seat applies them; none exists as code yet.

---

## 11. Probes written in this session (`/tmp/cg_s1ret/`; SHA-256 prefix)

| File | Prefix | What it is |
|---|---|---|
| `salvage_probe.py` | `3778dda88034c043` | R3: what leaves the two salvage reads, five inputs |
| `members.py` | `00207c90d6b4b28d` | R5: the 12 members, by AST |
| `dom.py` | `800e119cf4f82751` | R6: statement positions and return shapes |
| `cal.py` | `d54bc6695e41de67` | R7: the calibration call chain |
| `extract.py`, `ctx.py` | `49f4101002c3864e`, `4b34fa5a7b58d0a9` | the 12 functions written out with line numbers; gate calls in the callers |
| `f1_on_8953c7a5.out`, `f1_on_main.out` | | R9: outputs of the earlier judge's probe |
| `sweep2.out` | | R12 |

R1, R2, R8, R10 and R11 were run as commands typed into the shell and are given in §2. Files under `/tmp` are not durable. Each probe is described by its inputs and its calls so that it can be rebuilt.

---

## 12. Plain summary for Ed (5 lines)

1. The work package under review (S1) wires a battery check into everything that turns measured runs into numbers, because a run recorded while the battery was charging has untrustworthy energy. A test that reads the source code (the "sweep") lists every place that reads a run's files without that check. The model doing the work stopped on three things it had no rule for, and asked. None of the three holds up the merge once the steps below are applied, and none needs production code changed inside S1.
2. Two reads belong to the code that handles a run which aborted before any workload started. I ran it: multiplying every power value in its trace by a thousand changes nothing it returns (two timestamps, a failure reason, digests), and adding an energy result makes it refuse. The rule it failed said "reads no power field" where it meant "passes no power value on", so I corrected that wording. No check is added there.
3. Twelve functions read the power meter's raw output. Four only compare it with stored files and return problem messages; they get a new category for exactly that. Eight compute a timing bound from power pulses in calibration recordings, which does count as energy-derived. Three of those eight are already protected by a battery check made for calibration recordings, which the test did not recognise and now will. Five are script functions with no check, unchanged since the main branch and not on any path a measurement campaign uses; they go to a separate task (BFGS-RAWCAPTURE-01) on a fixed list of five, to be finished before the paper's timing numbers are frozen.
4. The third item is the known defect from the previous ruling: a campaign stores the idle power of a run that the battery check refuses, and the next campaign uses it to decide that the machine has cooled down. I re-ran the test on this code and on the main branch: same result (9.99 W stored, "recovered" after 30 s). It is older than S1, so it stays its own task (BFGS-COOLDOWN-ANCHOR-01), which must merge before the next scored campaign starts, with the read-only pre-check before every scored campaign until then.
5. Next the model applies eleven steps, all in test files: four from this ruling, then the seven already owed (13 to 19). Expected afterwards: 119 listed read sites, 48 raw-output readers, and the main test suite passing. Not run by me: the full suites, the deliberately broken variants each new test must catch, a whole campaign end to end, and how much a charging battery actually shifts a calibration timing fit.
