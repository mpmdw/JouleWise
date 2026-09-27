# Cold gate BFGS-S1-SWEEPCLASS-01: ruling (Fable 5.1, cold judge) on how the read sweep classes the gate's own reads, and on whether `BundleReader.raw_summary` is gated

Candidate: working tree detached @ `cbfa9dc3` (S1 fix round 3, partial). Base `1417c0c4`.
Charge: `90-coldgate-sweep/00-charge.md`, committed at `fbd7bec1`. Session: one foreground session, no subagents, no background tasks. No repository file edited; `git status --short` in the working tree printed 0 lines after the last probe. Scratch: `/tmp/cg_sweep/`. Session clock: 21:53 to about 22:30 local.

---

## 0. Contamination disclosure

The charge told me not to read `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAUDE*.md`, `AGENTS.md`, the decision log, or memory and skill files. I opened none of them. **The harness that started this session placed three of them in my context before the charge arrived:** the owner's global `CLAUDE.md` (a pointer to orchestration doctrine, and a writing standard), the project `CLAUDE.md` (notes on the bridge to a second model), and the index file `MEMORY.md` (about 110 one-line summaries of earlier sessions; several name this lane, the battery gate, and standing directives of the owner). The harness also listed the names and one-line descriptions of the installed skills. I opened no file that any of those lines points to, and invoked no skill.

What this exposure could bias, and what I did about it:

- The index says gates should be sensible on science grounds and that one model has the final say. I used neither as authority. Every ruling below rests on the ruled texts in the packet, the code at `cbfa9dc3`, and probes I ran.
- The global writing standard asks that every term be defined at first use. The charge asks the same of the summary. I followed it; it changes wording, not rulings.
- The earlier cold judge and I are the same model. That is a shared-blind-spot risk. One consequence is visible in this ruling: I found that the first judge's prototype, and my first extension of it, did not implement a rule the erratum states correctly (§2, X4). A refuter of a different model should check amendments 57 to 59.

A file I did not read: while I worked, `90-coldgate-sweep/11-opus-contract-refuter.md` appeared beside the charge (written 22:01; I saw it in a directory listing at 22:15, after this ruling was written). It is not in my packet. I did not open it, and nothing here responds to it.

What I read from the packet: the charge; the erratum ruling §0 to §5 and its amendments 51 and 52 in §10; text 8 and text 12 in the addendum ruling §4 C (and its §1 to §2 for the reasons); the seat's brief and report in full. **Not read:** the first ruling's §6 and §10 (the brief says the erratum's §10 supersedes them). I used that ruling's prototype file and its recorded output.

---

## 1. Terms used in this ruling

Each term is defined once and used in that sense only. Terms marked (E) are the erratum's, repeated so this file stands alone.

- **Bundle** (E). The directory one measured run leaves behind. It holds `config.json` (what was asked), `metadata.json` (what ran; it also holds the idle power measured before the run and the two battery records), `summary_metrics.json` (the reduced numbers, energy included), `power_trace.csv` (the power samples), `events.jsonl` (the **stage journal**: one line per stage start, stage end and token) and the directory `raw/` (the meter's output as captured, and the two battery readings).
- **Battery pair** (E). Two readings of the laptop battery, one before the measured span and one after. If either shows current flowing into or out of the battery, part of the energy the run drew did not pass through the meter's accounting, so the run's energy cannot be trusted.
- **Charging bundle.** A bundle whose battery pair shows the battery charging. In the probes it is built by the repository's own test helper (`WindowMembersTests.pair_bundle(..., charging=True)`), from a real captured reading.
- **Verdict** (E). The object the battery checker returns for one bundle. Its `status` is `pass`, `battery_float_confounded` (a reading shows charging or discharging), `battery_float_evidence_missing`, `not_applicable` (a simulated run) or `unobserved_historical` (one of 69 listed runs measured before the check existed).
- **Custody failure** (E). The exception `CustodyFailure` and its subclass `CustodyUnreadable`: a file the evidence depends on is missing, unreadable, or does not hash to its recorded digest. It is never a status. It stops the whole computation.
- **Energy-class value.** An energy, power, current, charge or voltage value, or a value computed from one. (This is the list amendment 51's class table already uses.)
- **The reader.** The class `BundleReader` in `joulewise/bundle_read.py`. One reader object reads one bundle.
- **The gate** (E). The check that a bundle's battery pair passes, in one of two forms. **Window form:** the function `authenticate_window_members(members)`, which takes a list of (label, bundle path), classes every one, and returns all verdicts or raises. **Reader form:** the method `BundleReader.metadata()`, which returns the parsed `metadata.json` only if the bundle's verdict is acceptable, and raises otherwise.
- **Gated energy accessors.** The four reader methods `trace_rows`, `summed_curve`, `source_curve`, `measured_window`. Text 8 (the ruled text for the reader) requires each to call `self.metadata()` before anything else. These are "the four energy accessors" of the charge.
- **Tolerant accessors** (E). The four reader methods `raw_metadata`, `raw_config`, `raw_summary`, `raw_artifact_bytes`. Each returns a file's content, or `None` if the file is damaged, **without** the battery check. They exist so that a damaged or refused bundle can still be inspected and reported.
- **The sweep** (E). The test `tests/test_bfgs_consumer_sweep.py`. It parses every tracked Python file under `joulewise/` and `scripts/` and lists every **read site**: a place that reads one of the three **watched files** (`summary_metrics.json`, `metadata.json`, `power_trace.csv`) or calls a tolerant accessor, with no gate call before it in the same function. Each listed place is a **row**, keyed (path, function, operation, watched file), and must have an entry in the test's **allowlist** with a **class** (a named reason category whose conditions the row must meet) and a reason.
- **Dominates** (E). Said of a gate call and a later statement: execution cannot reach the statement unless the gate call ran and returned normally.
- **Consumer** (E). One of the eight modules that turn bundles into claimed numbers (listed in §8).
- **Counterfactual** (E). For a test row: the specific wrong implementation under which the row must fail. A row **goes RED** when it fails and is **GREEN** when it passes.
- **Frozen file.** A file the ruled texts require to stay byte-identical to base. Here: `joulewise/battery_float.py`, `joulewise/reduce.py`, `joulewise/bundle.py`.

**How a read reaches a bundle's files.** Every element of the diagram is named below it.

```
                        a swept function (89 of them hold a read site)
                 ________________|_____________________________________
                |                        |                             |
        [A] window gate           [B] reader gate            [E] tolerant accessors
  authenticate_window_members   BundleReader.metadata()   raw_summary, raw_metadata,
                |                        |                 raw_config, raw_artifact_bytes
                +-----------+------------+                             |
                            v                                          |
             [C] BundleReader._battery_verdict                         |
                            v                                          |
             [D] battery_float.authenticate_bundle                     |
                            | reads                                    | reads
                            v                                          v
      metadata.json, events.jsonl,                      summary_metrics.json, metadata.json,
      raw/battery_float.{pre,post}.ioreg                config.json, raw/<any name>
                            |
                 a verdict, or an exception
                            |
        [F] gated energy accessors: trace_rows, summed_curve, source_curve,
            measured_window. Each calls [B] first, then reads power_trace.csv
            or the stage journal.
```

- [A] and [B] are the two forms of the gate. [C] is the private method both call. [D] is the function in the frozen file that reads the battery evidence and returns the verdict.
- [A], [B] and [D] each read `metadata.json` **as the input of the check**. No gate can come before that read: the read is how the gate learns what to check. These are the first two rows of the charge, plus one the seat did not list ([A]).
- [E] is the path with no check on it. The third row of the charge is the definition of one [E] method.
- [F] is the path text 8 closed.

---

## 2. Executed evidence (this session, foreground, working tree `cbfa9dc3`)

| Id | Probe | Result (exact) |
|---|---|---|
| X1 | The first judge's prototype `/tmp/cg_r2/sweep49.py` (SHA-256 prefix `8e0d3bcdde3214e2`, the value the erratum records), run on my tree; `diff` against its recorded output `/tmp/cg_r2/sweep49.out` | `sites 126 distinct rows (path,function,operation,file) 120 functions 89`; the diff is empty. The seat's "120 sites in 89 functions" is this prototype's count. 126 is the count of source lines; 120 the count of rows. |
| X2 | `/tmp/cg_sweep/sweep51.py`: the prototype with the erratum's rules added ((b) 3 stores; (c) the reader form bound to its reader; (d) 2 to 5). Self-test `/tmp/cg_sweep/cases59.py` run against it: the erratum's sources K1 to K10, G1 to G5, H1 to H6, the store case, and four I added (G6, H7, H8, H9; see X4) | self-test: `mismatches: 0`. Tree: `120` rows, `89` functions, `126` lines; **the row set is identical to X1's** (diff empty). The erratum expected "a small number" more than 120; executed, the number more is zero. |
| X3 | Every `try` statement in tracked `joulewise/` and `scripts/` whose body holds a gate call | 8 such statements. In 3 of them some handler does not end in `raise`: `calibration_bracketing.py:2758`, `reduce.py:2651`, `window_duration_margins.py:944`. In `reduce.py:2651` the one handler ends in **`return`** (it returns a `FAILED` summary). None of the 8 functions has a watched read after its `try`, which is why X2 adds no row. |
| X4 | **A defect in the prototype, found by my own added case.** Erratum rule (d) 3 says a read inside a handler or a `finally` is never gated by a gate call in that `try`'s body. `sweep49.py` and my first `sweep51.py` reported H4 (the read inside a handler) only because H4's handler does not end in `raise`, which makes the body a branch. With a handler that ends in `raise` or `return`, the read inside it was **silent**. I corrected both detectors (`dominates`, shared) and added H8 (`try:` gate `except RuntimeError:` read, then `raise`) and H9 (`try:` gate `finally:` read) | after the correction: H4, H8, H9 `REPORTED` under the rule as it stands and under amendment 59; `mismatches: 0` both ways. The erratum's text is right. Its test rows do not force it: R51-20 is H4 only. Rows R59-4 and R59-5 close that. |
| X5 | `/tmp/cg_sweep/reader_methods.py`: every method of `BundleReader` by syntax tree | 30 public (29 methods and the property `path`), 8 private. `self.metadata()` is the first statement of exactly four: `trace_rows`, `summed_curve`, `source_curve`, `measured_window`. |
| X6 | `/tmp/cg_sweep/reader_probe.py`. A passing bundle and a **charging bundle** from the repository's helper; I added `summary_metrics.json`, `power_trace.csv`, `raw/powermetrics_idle.plist` and one metadata field, each carrying the sentinel value `4242.4242` so that a returned value can be traced to the bundle's files. Every public method is called on a **fresh** reader (no earlier gate call on it) | Charging bundle: `authenticate_bundle -> battery_float_confounded`; `window gate: raised WindowBatteryRefusal`; `metadata`, `trace_rows`, `summed_curve`, `source_curve`, `measured_window`: `raised BatteryStatusRefusal`. **`raw_summary`, `raw_metadata`, `raw_artifact_bytes`: `RETURNED`, `energy_sentinel_in_value=True`.** All other methods returned or raised for a missing file, sentinel `False`. Full table in §5.1. |
| X7 | `/tmp/cg_sweep/custody_probe.py`: a passing bundle with `raw/battery_float.post.ioreg` deleted | `authenticate_bundle`, `BundleReader.metadata`, `BundleReader.trace_rows`: `raised CustodyFailure`. `authenticate_window_members`: `raised CustodyFailure`, `window_member=m`. `BundleReader.raw_summary`: `RETURNED dict energy in value: True`. |
| X8 | `/tmp/cg_sweep/reduce_probe.py`: the frozen reducer `reduce_bundle` on the charging bundle (summary file removed, as at the controller's reduce stage), with the tolerant accessors and the idle-power derivation wrapped to record calls | `status=RunStatus.FAILED failure_message='battery_float_confounded: pre IsCharging is not No; …' energy_sentinel_in_value=False calls=[('raw_summary', '')]`. The idle-power derivation was not reached. One tolerant read happens **before** the gate: `_resolve_reducer_version` (`reduce.py:2650`, the gate is at `:2653`). |
| X9 | `/tmp/cg_sweep/gate57.py`: a prototype of the checks ruled in amendments 57 and 58, on the tree, then on nine mutated copies of the source held in memory | Tree: `PASS`. RED: CF1 (`metadata()` stores the content before the verdict call), CF2 (`metadata()` returns the content when the verdict call raises), CF3 (the window gate returns a member's metadata beside the verdicts), CF4 (a consumer calls `authenticate_bundle` itself), CF5 (`raw_summary` does more than forward), CF6 (`trace_rows` loses its gate call), CF9 (a second method writes the gate's cache slot). **GREEN: CF7** (`metadata()` ignores the verdict's status). CF8: a function named `authenticate_window_members` in another module is not a gate definition, and fails the content check. |
| X10 | `/tmp/cg_sweep/cf7_behaviour.py`: the reader class compiled from the CF7 source, on the charging bundle | tree: `metadata raised BatteryStatusRefusal`, `trace_rows raised BatteryStatusRefusal`. CF7: `metadata RETURNED, energy in value: True`, `trace_rows RETURNED, energy in value: True`. So the structure check cannot see CF7 and the behaviour row can. Both are needed. |
| X11 | `/tmp/cg_sweep/chain59.py`: the `behind_gate` check for `derive_idle_mean_uncertainty`, followed through its callers, under rule (d) 2 as it stands and as amended | as it stands: fails, naming the four callers of `reduce_bundle` (the gate in `reduce_bundle` does not count as dominating, because its handler ends in `return` and not `raise`). Amended: `PASS`. Amended, with `_reduce_v060` left off the row: fails, `call of derive_idle_mean_uncertainty in unlisted joulewise/reduce.py::_reduce_v060`. Row counts under the amended rule: 120 rows, 89 functions (unchanged). |
| X12 | `grep` for calls of `authenticate_bundle(`, `_battery_verdict(`, `authenticate_pair(` under `joulewise/`, `scripts/` | `authenticate_bundle`: `bundle_read.py:476`, `:481`, both inside `BundleReader._battery_verdict`. `._battery_verdict(`: `bundle_read.py:326` (window gate), `:452` (`metadata`). One **unrelated** module-level function of the same name is called by bare name at `scripts/issue_calibration_acceptance_generation.py:1564`. |
| X13 | `grep` for calls of the tolerant accessors under `joulewise/`, `scripts/` | `raw_summary`: 18 call sites. `raw_metadata`: 20. `raw_artifact_bytes`: 1 (`idle_dependence.py:198`). Listed in §5.2. |
| X14 | A search of every swept function that touches the stage journal (`.events()`, `_strict_jsonl_objects`, or the constant `events.jsonl`) and names an energy-class key; `controller.py:1141-1143` read | The controller writes `power_w_mean` (the idle mean power) into the metadata of the journal's `stage_completed` / `idle_baseline` event. Four functions touch the journal and name an energy-class key: `cli.py::_strict_uncertainty_evidence_problems`, `reduce.py::_reduce_v060`, `scripts/analyze_phase_share.py::analyze_bundle`, `scripts/paper/partial_record_enclosure.py::_derive_bundle_authenticated`. The search is by key name and is a screen, not a proof. |
| X15 | `shasum joulewise/battery_float.py`; `git diff --quiet 1417c0c4 HEAD -- joulewise/battery_float.py joulewise/reduce.py joulewise/bundle.py`; an import grep over the eight consumers; `git status --short` | prefix `4b4d7bb20625`; all three identical to base; no `battery_float` import line; 0 status lines. |

**Limits of the probes, stated so they are plain.**

- X6's fixture is a hand-extended bundle, not a finalized production bundle. It shows which methods consult the gate, which is a property of the code and not of the fixture. It does not show what a real summary holds.
- X8's passing bundle has no measured window, so the reducer stops before the idle-power derivation on the passing path too. That the derivation is reached on a complete passing bundle is from reading (`reduce.py:3302`, `:3563`), **NOT EXECUTED**.
- X9's checks are a prototype of mine, 120 lines, written in this session. The seat implements from the amendment text, not from the prototype.
- The keyword screen of §6 looked at all 89 functions by pattern and I then read 9 of them. I did **not** read the other 80.

---

## 3. Rulings at a glance

| Question | Ruling | Where the text is |
|---|---|---|
| Q1. The gate's own reads | **A new class, `gate_body`, closed at three rows, checked by the sweep by structure and by behaviour.** Not a detector exemption: all three reads stay in the inventory. The seat's recommendation is adopted in substance; "named functions and reasons" alone is rejected, because a name and a reason are what a wrong function would also supply. | amendment 57 (a) to (c) |
| Q1. The tolerant accessors' definitions | **A second new class, `tolerant_definition`, two rows.** A definition may carry it only if its name is in the constant that makes every call of that name a read site. | amendment 57 (d) |
| Q2. Is `raw_summary` one of the four energy accessors? | **No.** Text 8 names the four, and in its next sentence names `raw_summary` among the accessors that "stay tolerant and are governed by the sweep". The code matches text 8 (X5, X6). | §5 |
| Q2. Is `raw_summary` an ungated energy read? | **Yes, by design, and so are `raw_metadata` and `raw_artifact_bytes`** (X6, X7). Text 8 is not broken. The control is at each call site, and it was incomplete in three ways, each now pinned. I do **not** rule that the accessors be gated: §5.3 gives the reason. | amendment 58 |
| Q3. Anything else of the same kind | **One row is mis-classed and cannot be classed correctly under amendment 51 as it stands** (`idle_dependence.py::derive_idle_mean_uncertainty`). One row's reason is false as written (`reduce.py::_resolve_reducer_version`). Two blind spots are named (the stage journal; a read inside a handler that ends in `raise`). **No further site needs a new class.** Rows I did not examine are listed. | §6; amendment 59 |

The seat's second flag (F2: whether a comment fix is authorized in `tests/test_battery_float_consumers.py`) is not in my charge and is **not ruled here**.

---

## 4. Q1: the gate's own reads

### 4.1 The forcing problem

The sweep asks of every read: did a gate call come first? For three functions the question has no answer, because the function is the gate. [A], [B] and [D] in the diagram each read `metadata.json` to find the battery records. Amendment 51 offers four classes. None fits:

- `strict_validation` requires that every returned value be a digest, a boolean, an identity string or a list of problem strings. [B] returns the whole metadata. [A] and [D] return verdicts, which hold `delta_q_mah` (a charge).
- `non_claim` (i) requires that no field read be an energy-class value. The battery records hold currents. `non_claim` (ii) requires that nothing returned reach a claim artifact. Verdicts are written into window-level outputs.
- `historical` is about old bundles.
- `behind_gate` requires a gate before the function. There is none; this is the gate.

The seat is right that the four classes do not fit. It listed [B] and [D]. [A] is a fourth row of the same kind (`joulewise/bundle_read.py::authenticate_window_members`, `direct:_strict_json`, `metadata.json`, X1).

### 4.2 Why a class and not an exemption

A detector exemption would remove the three reads from the inventory. Then a second read added to a gate's body (say, of `summary_metrics.json`, returned beside the verdict) would be invisible. Kept as rows, any new read in a gate body is a new key, and the sweep's equality test (reported keys equal allowlist keys) fails until someone classes it.

### 4.3 Why a name and a reason are not enough

A class that says "this function is a gate implementation" and lists names can be claimed by writing a name into the list. The rule must state what makes a gate's read safe, in a form the sweep can check. Two things make it safe:

1. **The file's content does not leave the function before a verdict exists.** Checked from the syntax tree: every statement that returns or stores a value taken from the read comes after, and is dominated by, a call that produces the verdict. X9 shows this check RED under CF1, CF2, CF3.
2. **The verdict is acted on.** A gate that computes a verdict and ignores it satisfies (1). X9 shows the structure check GREEN under CF7, and X10 shows a behaviour row RED under CF7. So the class also requires a behaviour row: on a charging bundle the function refuses, and on a bundle whose battery reading was deleted it raises a custody failure.

And the class is **closed**: its members are the definitions that amendment 51 (c) already resolves gate calls to, plus the one function they obtain the verdict from. The sweep computes that set from the tree; the allowlist cannot add to it. X9's CF8 shows that a function with the gate's name in another module is not a member.

### 4.4 The tolerant accessors' definitions

`BundleReader.raw_summary` is one line: `return self._tolerant_json("summary_metrics.json")`. The detector reports it because it hands a watched file name to a call. This row is the **definition** of an accessor whose every **call** the sweep already reports, by amendment 51 (b) 1, in the caller. The definition returns energy content and no class fits it; that is the seat's third row. `BundleReader.raw_metadata` is the same case (X1) and the seat did not list it.

The check belongs at the call sites, and is there. The definition row is kept in the inventory under a class that can be carried only by a method whose name is in the tolerant-accessor constant, because membership of that constant is exactly what causes every call to be reported. A method outside the constant cannot carry the class; a method added to the constant has all its calls swept.

---

## 5. Q2: the reader's methods, and `raw_summary`

### 5.1 Every public method of `BundleReader` (X5, X6, X7)

"Gate first" means `self.metadata()` is the method's first statement. "On the charging bundle" is the executed result on a fresh reader.

| Method | Reads | Can return an energy-class value | Gate first | On the charging bundle |
|---|---|---|---|---|
| `metadata` | `metadata.json` | yes (idle power, battery records) | it is the gate | raised `BatteryStatusRefusal` |
| `trace_rows` | `power_trace.csv` | yes | **yes** | raised |
| `summed_curve` | `power_trace.csv` | yes | **yes** | raised |
| `source_curve` | `power_trace.csv` | yes | **yes** | raised |
| `measured_window` | stage journal | the bounds of the energy integral | **yes** | raised |
| `raw_summary` | `summary_metrics.json` | **yes** | **no** | **returned, sentinel present** |
| `raw_metadata` | `metadata.json` | **yes** | **no** | **returned, sentinel present** |
| `raw_artifact_bytes` | `raw/<name>` | **yes** (the meter's captured output) | **no** | **returned, sentinel present** |
| `raw_config` | `config.json` | no | no | returned |
| `events` | stage journal; whether `metadata.json` has the key `battery_float` | **yes, one field**: `power_w_mean` in the `idle_baseline` completion event (X14) | no, and it cannot: the gate itself reads the journal through `events()` | returned |
| `config` | `config.json` | no | no | returned |
| `problems` | all five files | no: a list of problem strings | no | returned |
| `is_complete`, `is_event_v2`, `is_frozen_legacy_identity` | summary or metadata | no: a boolean | no | returned |
| `rail_manifest` | `metadata.json` | no: rail names | no | returned |
| `phase_windows`, `request_phase_windows`, `suite_window`, `item_windows`, `block_windows`, `level_windows`, `token_timestamps`, `runtime_cleanup_ok` | stage journal | no: times and a boolean | no | returned |
| `suite_manifest`, `request_roster` | their own files | no | no | returned `None`; raised for a missing file |
| `request_rows`, `request_token_rows`, `suite_item_records` | files under `outputs/` | **NOT EXECUTED** (the fixture has none). By reading, `_suite_item_records` names no energy-class key; the two request accessors were not read. | no | raised for a missing file |
| `path` (property) | nothing | no | no | not called |

### 5.2 Production callers of the three energy-returning tolerant accessors (X13, X2)

"Reported" means the detector lists the call as a read site, so it has or needs an allowlist row. "Gated" means a gate call dominates it in the same function.

| Accessor | Call site | Function | Detector | What I verified |
|---|---|---|---|---|
| `raw_summary` | `aggregate.py:156` | `_read_member` | gated | read: the window gate on the same member is the line before |
| | `determinism_gate.py:260` | `_inspect_strict_valid_bundle` | gated | read: `reader.metadata()` on the same reader is the line before |
| | `run_campaign.py:2020` | `assert_production_uncertainty` | gated | X3: the gate is in a `try` whose handler ends in `raise` |
| | `scripts/paper/partial_record_enclosure.py:249` | `_derive_bundle_authenticated` | gated | X3: the same |
| | `inputs.py:1928`, `inputs.py:2834`, `run_campaign.py:2093` | (three functions) | gated | detector only; **not read** |
| | `reduce.py:2756` | `_resolve_reducer_version` | reported | X8: it runs **before** the gate. It returns a version string. |
| | `analyze_phase_share.py:96` | `analyze_bundle` | reported | read: it takes the energy bounds from the summary before any gate; `reader.summed_curve()` later gates the same reader; see §6 |
| | `report.py:216`, `cli.py:424`, `bundle_read.py:760`, `:1433`, `envelope_gate.py:133`, `:654`, `make_figures.py:241`, `:324`, `corpus_compat_receipt.py:146` | (eight functions) | reported | rows exist at `cbfa9dc3`; classes are the seat's and the refuter's to check |
| `raw_artifact_bytes` | `idle_dependence.py:198` | `derive_idle_mean_uncertainty` | reported | read and X11: see §6 |
| `raw_metadata` | 20 call sites | | 2 gated, 18 reported | the detector's output (18 reported source lines); not read one by one |

### 5.3 Ruling

**`raw_summary` is not one of the four energy accessors.** Text 8, in full: "The four energy accessors `summed_curve`, `source_curve`, `trace_rows`, `measured_window` call `self.metadata()` first, so every byte-level re-derivation passes the gate. `raw_metadata`, `raw_config`, `raw_summary`, `raw_artifact_bytes` stay tolerant and are governed by the sweep (text 12)." The code does what text 8 says (X5, X6).

**It is an ungated read of energy content**, as are `raw_metadata` and `raw_artifact_bytes`. A charging bundle's energy comes back from each (X6). So does the energy of a bundle whose battery evidence was destroyed (X7). Text 8 accepted this and placed the control at the call sites.

**I do not rule that the tolerant accessors be gated.** Three reasons, each from the code:

1. The frozen reducer calls `raw_summary` before its own gate (`reduce.py:2650`, X8), to learn which reducer version to use. A gate inside `raw_summary` would raise there, inside a frozen file, where today the reducer returns a structured `FAILED` summary.
2. The bundle validator and the run browser use these accessors to show a refused or damaged bundle. That is the purpose the module's own header states for them. Gated, they could not show the bundle the operator most needs to see.
3. `events()` cannot be gated by `metadata()` at all: the gate reads the journal through it, and the call would never end.

**The call-site control had three holes. Amendment 58 closes each.**

- **A new reader method.** Nothing at `cbfa9dc3` stops a fifth tolerant accessor, or a fifth energy accessor without the gate call, from being added. Calls are matched by name against a fixed list of four, so calls of a new method would not be swept. *Closure:* the sweep holds a table of all 30 public methods with a kind each, and asserts it equals the class (58 (b)).
- **The gate call inside the four energy accessors is pinned by no test of the sweep.** *Closure:* a structure row and a behaviour row (58 (c)). X9's CF6 is the counterfactual.
- **A caller that returns energy can carry a class meant for validators.** `derive_idle_mean_uncertainty` carries `strict_validation` at `cbfa9dc3` and returns an idle-power uncertainty. *Closure:* 58 (d) limits the classes such a row may carry; amendment 59 makes the right class checkable.

---

## 6. Q3: the other rows

**Method.** I ran the detector (X2) and screened the source of all 89 functions for energy-class key names. 37 matched. After removing matches on the package's own name, I read the 9 functions below. **I did not read the other 80 functions.** The 28 rows in the eight consumer modules (14 in `whole_window.py`, 10 in `run_campaign.py`, 4 in `floor_extraction.py`; counted from X2's output) are governed by amendment 51 (g) 1 and (g) 2, which already limit the energy-returning ones to "gated" or `behind_gate`; I did not examine them one by one.

| Row | Finding | Ruling |
|---|---|---|
| `joulewise/idle_dependence.py::derive_idle_mean_uncertainty`, `raw_artifact_bytes` | It parses the meter's raw idle capture and returns the uncertainty of the idle mean power, which the reducer subtracts from every energy it reports. At `cbfa9dc3` its row is `strict_validation`, reason "follows BundleReader.metadata authentication". The class is wrong (it returns an energy-class value) and the reason is a `behind_gate` claim that nothing checks. **It is behind the gate in fact:** its two callers are `_reduce` and `_reduce_v060`, whose only caller is `reduce_bundle`, which calls `reader.metadata()` first and returns `FAILED` on refusal (X8, X11). **But amendment 51 as it stands cannot verify that,** for two reasons: `reduce_bundle`'s handler ends in `return`, which rule (d) 2 does not accept; and `_reduce` has no read site of its own, so it can have no row, which the callers form requires of a caller that is not itself gated. `reduce.py` is frozen, so the code cannot be changed to suit the rule. | `behind_gate`, callers form. Amendment 59 amends (d) 2 and the callers form. Without it the seat must return this row again. |
| `joulewise/reduce.py::_resolve_reducer_version`, `raw_summary` | Runs before the gate (X8). Returns a reducer version string. At `cbfa9dc3` its reason says "authenticates BundleReader.metadata first". That sentence is false. | `strict_validation` is the right class (an identity string). The reason is rewritten to say what is true: "reads `summary_provenance.reducer_version` before the gate; returns the version string only". Refuter confirms the single `return`. |
| `joulewise/reduce.py::_resolve_reducer_version`, `raw_config`; `_verify_instrument_calibration`, `raw_config` | `config.json` holds no energy-class value. | Reasons rewritten the same way; class by the seat. |
| `scripts/analyze_phase_share.py::analyze_bundle`, `raw_summary` and `direct:_sha256` | Reads the phase energy bounds from the summary with no gate before. Later calls `reader.summed_curve()`, which gates the same reader, so nothing is returned for a charging bundle. Returns energy intervals. I found no tracked Python file that imports or runs it. Outside S1's WRITE_SCOPE. | `non_claim` (ii) **only if** the refuter's search of amendment 51 (f) confirms no claim artifact reads its output. The reason names what it writes. Otherwise returned to the lead. Not a new class. |
| `scripts/summarize_g2a_prefill_probe.py::summarize` (2 rows, new) | Hands the summary and metadata to `_run_provenance`. I saw it read `run_id` and the prompt provenance; I did not read the whole helper. | The seat states every field read. `non_claim` (i) if none is energy-class; otherwise returned. |
| `joulewise/cli.py::_cmd_reduce` (new) | Reads `summary_provenance.reducer_version` from the stored summary. | `strict_validation` or `non_claim` (i); the seat's choice, reason names the field. |
| `joulewise/output_identity.py::_bundle_reference` (3 rows, new) | Returns a run id, digests and reasons. | `strict_validation`. |
| `scripts/corpus_compat_receipt.py::evaluate_bundle` | Returns four pass/fail results. | Class by the seat; the current `non_claim` needs the form amendment 51 (f) requires. |
| `joulewise/report.py::_discover_bundles` | Returns the whole summary to the run browser. | `non_claim` (ii), refuter's search. |
| `scripts/check_window_provenance.py` (2 rows) | Named already in amendment 51 (f). | As ruled there. **NOT EXAMINED** by me. |
| `joulewise/bundle_read.py::BundleReader.events`, `direct:_strict_json` | Reads `metadata.json` only to learn whether the key `battery_float` is present. | `non_claim` (i); the field read is the presence of one key. |
| `joulewise/bundle_read.py::BundleReader.problems`, `_check_power_trace` | Return lists of problem strings. | `strict_validation`. |

**Two blind spots, named.**

1. **The stage journal.** `events.jsonl` is not a watched file, and one of its events carries the idle mean power (X14). `events()` cannot be gated (§5.3). I found four functions that touch the journal and name an energy-class key; each is a validator, is behind the reducer's gate, or gates the same reader. Amendment 58 (e) adds this to the list of what the sweep cannot see and pins the four.
2. **A read inside a handler that ends in `raise` or `return`.** The erratum's rule (d) 3 covers it. The erratum's test rows do not (X4). Rows R59-4 and R59-5.

**Answer to Q3.** Among the rows I examined, none returns energy-class content ungated in a way that no class should admit, **provided amendment 59 lands**. Without it, `derive_idle_mean_uncertainty` is such a row: gated in fact, unclassable in the sweep.

---

## 7. Amendments 57 to 59 (exact text; the fix-round brief quotes these)

All three amend amendment 51 of the BFGS-S1-R2-01 erratum. All changes are in `tests/test_bfgs_consumer_sweep.py`, which is in S1's existing WRITE_SCOPE. **No production file is edited by these amendments.** The behaviour rows may be placed in that file or in `tests/test_bundle_read.py` (also in scope).

### Amendment 57 (amends amendment 51 (f), the class table: two classes are added)

57. **The gate's own reads, and the definitions of the tolerant accessors, are rows of two closed classes that the sweep checks itself.**

**(a) Terms.**
- A **gate definition** is one of two definitions in `joulewise/bundle_read.py`: the top-level function `authenticate_window_members`, and the method `metadata` of the class `BundleReader`. These are the definitions that a gate call of amendment 51 (c) resolves to.
- The **verdict source** is the function `authenticate_bundle` in `joulewise/battery_float.py`.
- A **gate body** is a gate definition or the verdict source. There are three.
- A **verdict call** is a call whose callee is named `_battery_verdict`, `authenticate_bundle` or `authenticate_pair`.
- A **content name**, inside one function, is a plain name bound (by assignment, annotated assignment, `:=`, or a `for` target) from an expression that holds a read-site call of amendment 51 (b) 2, or that mentions a content name. Binding is repeated until no name is added. A name bound from a verdict call is **not** a content name. A store to an attribute or a subscript binds nothing.
- A **leaving statement** is a `return` or `yield` whose value mentions a content name, or an assignment to an attribute or a subscript whose value mentions a content name.

**(b) The class `gate_body`.** A row may carry it only if the sweep asserts all six:

1. **Resolution.** The row's (path, qualified function) is a gate body. The sweep computes the three from the tree, and asserts that `joulewise/bundle_read.py` holds exactly one top-level function `authenticate_window_members` and exactly one class `BundleReader` with exactly one method `metadata`, and that neither `authenticate_window_members` nor `BundleReader` is assigned at the module's top level.
2. **Closed callers.** Every call of `authenticate_bundle`, by bare name or as an attribute, in a tracked file under `joulewise/` or `scripts/` lies in `joulewise/bundle_read.py::BundleReader._battery_verdict`. Every call of `_battery_verdict` **as an attribute** lies in a gate definition. (A module-level function of that name called by bare name is another function; one exists, `scripts/issue_calibration_acceptance_generation.py:1564`.)
3. **Content.** The function binds at least one content name and holds at least one verdict call. Every leaving statement comes after a verdict call, in source order, that dominates it by the rules of amendment 51 (d) as amended by 59 (a).
4. **The cache slot.** An assignment whose target is `<expression>._cache["metadata"]` occurs in `BundleReader.metadata` and in no other function of any tracked file under `joulewise/` or `scripts/`. (`metadata()` returns that slot; rule 3 guards the store into it.)
5. **Behaviour.** Rows R57-8 and R57-9 pass for the function.
6. **Count.** The set of rows whose class is `gate_body` equals these three keys, and the test holds them as a constant:
   - `("joulewise/battery_float.py", "authenticate_bundle", "direct:_required_object", "metadata.json")`
   - `("joulewise/bundle_read.py", "BundleReader.metadata", "direct:_strict_json", "metadata.json")`
   - `("joulewise/bundle_read.py", "authenticate_window_members", "direct:_strict_json", "metadata.json")`

   A fourth `gate_body` row needs a cold gate.

The reason field of a `gate_body` row states which of the three it is. `joulewise/battery_float.py` is parsed by the sweep and is not edited.

**(c) What `gate_body` does not cover.** A second read site inside a gate body (another operation or another watched file) is a new key. It is not covered by the row that exists, and fails the equality test of R51-14 until it is classed. It may carry `gate_body` only if rule 3 holds for it and a cold gate extends the constant of rule 6.

**(d) The class `tolerant_definition`.** A row may carry it only if the sweep asserts all four:

1. The function is a method of the class `BundleReader` in `joulewise/bundle_read.py`.
2. Its name is a member of the test's tolerant-accessor constant, **the same object** that amendment 51 (b) 1 matches calls against. (So every call of that name, on any receiver, in any tracked file, is a read site in its caller.)
3. Its body, a docstring aside, is the single statement `return self._tolerant_json(<string constant>)`.
4. That string constant equals the row's watched file.

Two rows carry it: `BundleReader.raw_metadata` (`metadata.json`) and `BundleReader.raw_summary` (`summary_metrics.json`). `raw_config` names `config.json` and `raw_artifact_bytes` names no watched file, so neither definition is reported; both names stay in the constant.

**Test rows for amendment 57.** R57-1 to R57-7 call the sweep's check on the tracked source with one replacement made in memory. "The tree" is the tracked source unchanged.

| Row | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R57-1 | the tree | rules (b) 1 to 4 and (b) 6 hold; (d) holds for both rows | an allowlist with a fourth `gate_body` row; an allowlist where `BundleReader.problems` carries `gate_body` |
| R57-2 (CF1) | `metadata()` with `self._cache["metadata"] = raw` moved before the verdict call | fails, naming the store | a check that requires only that a verdict call exist somewhere in the function (executed RED under the ruled check, X9) |
| R57-3 (CF2) | `metadata()` with the verdict call wrapped in `try:` … `except BundleReadError: return raw` | fails, naming the `return` | a check that tests source order and not dominance (X9) |
| R57-4 (CF3) | the window gate with `verdicts[label + ":metadata"] = metadata` added after the read | fails, naming the store | a check that looks only at `return` statements (X9) |
| R57-5 (CF4) | `aggregate._read_member` with its gate call replaced by `battery_float.authenticate_bundle(runs_root / member)` | fails, naming the caller | a class with no check on callers (X9) |
| R57-6 (CF9) | a method `prime(self, value)` added to the reader whose body is `self._cache["metadata"] = value` | fails, naming `BundleReader.prime` | a check limited to the body of `metadata()` (X9) |
| R57-7 (CF8, CF5) | (i) source for `joulewise/zz_new.py` defining its own `authenticate_window_members` that returns `(b / "summary_metrics.json").read_text()`, with an allowlist row of class `gate_body`; (ii) `raw_summary` with a body that also stores the value on `self` | (i) fails rule (b) 1; (ii) fails rule (d) 3 | a class claimed by function name or by reason text (X9) |
| R57-8 | a charging bundle from `WindowMembersTests.pair_bundle(charging=True)`; each gate body called on it, the reader form on a fresh reader | `authenticate_bundle(b).status == "battery_float_confounded"`; `BundleReader(b).metadata()` raises `BatteryStatusRefusal` with that status; `authenticate_window_members((("m", b),))` raises `WindowBatteryRefusal` naming `m` | **CF7:** `metadata()` with its status test replaced by `if False:`. The structure rows are GREEN under CF7 (X9); this row is RED (X10). |
| R57-9 | a passing bundle with `raw/battery_float.post.ioreg` deleted | each of the three raises, and `isinstance(exc, battery_float.CustodyFailure)`; the window form's exception has `window_member == "m"`; **no verdict is returned** | a gate that turns the missing file into the status `battery_float_evidence_missing` (executed GREEN on the tree, X7; the counterfactual is NOT EXECUTED) |

### Amendment 58 (adds pins to text 8's sentence on accessors; changes no behaviour of the reader)

58. **The reader's public methods are a closed, classed list; the four energy accessors are pinned; a caller that returns energy cannot carry a validator's class.**

**(a) Stated, so that no later reader takes it for an oversight.** `raw_summary`, `raw_metadata` and `raw_artifact_bytes` return energy-class content from a bundle the gate refuses, and from a bundle whose battery evidence is missing (executed, X6, X7). Text 8 ruled this. They are not gated. Their control is the sweep's row at every call site.

**(b) The method table.** The sweep holds the constant `READER_METHODS`, a mapping from each public name of `BundleReader` to one kind:

| Kind | Names | What the sweep asserts of a name of this kind |
|---|---|---|
| `gate` | `metadata` | it is the reader-form gate definition of 57 (a) |
| `gated_energy` | `trace_rows`, `summed_curve`, `source_curve`, `measured_window` | the method's first statement, a docstring aside, is the expression statement `self.metadata()` |
| `tolerant` | `raw_metadata`, `raw_config`, `raw_summary`, `raw_artifact_bytes` | the name is in the tolerant-accessor constant, and the constant has no other member |
| `other` | `path`, `config`, `events`, `problems`, `is_complete`, `is_event_v2`, `is_frozen_legacy_identity`, `rail_manifest`, `request_roster`, `request_rows`, `request_token_rows`, `request_phase_windows`, `runtime_cleanup_ok`, `phase_windows`, `token_timestamps`, `suite_manifest`, `suite_item_records`, `suite_window`, `item_windows`, `block_windows`, `level_windows` | nothing beyond the sweep's ordinary rows |

The sweep asserts that the set of names defined in the class body that do not begin with `_` **equals** the table's keys (30 at `cbfa9dc3`). A new public method fails the test until it has a kind. Giving a new method the kind `other` when it returns an energy-class value is a finding for the refuter, who checks the table as it checks the allowlist.

**(c) Behaviour of the accessors**, on a fresh reader over the charging bundle of R57-8: each `gated_energy` method raises `BatteryStatusRefusal`; each `tolerant` method returns without raising. The second half is asserted so that a later change that gates a tolerant accessor is seen and ruled, not so that it is forbidden.

**(d) Callers that return energy.** A row whose operation is `raw_summary`, `raw_metadata` or `raw_artifact_bytes`, in a function that returns, writes or passes on an energy-class value taken from the accessor's result, may carry only `behind_gate`, `historical`, or `non_claim` under clause (ii). It may not carry `strict_validation` or `non_claim` under clause (i). This extends amendment 51 (g) 1, which says the same of the eight consumer modules, to every module. Applied at `cbfa9dc3`:
1. `joulewise/idle_dependence.py::derive_idle_mean_uncertainty`: `behind_gate`, callers form, by amendment 59 (c).
2. `joulewise/reduce.py::_resolve_reducer_version`, `raw_summary`: `strict_validation`, reason "reads `summary_provenance.reducer_version` before the gate; returns the version string only". The words "authenticates … first" are removed from all three `reduce.py` reasons: they are false (executed, X8).

**(e) The stage journal.** Amendment 51 (h) gains the item: "**A value read from the stage journal.** `events.jsonl` is not a watched file. One of its events holds the idle mean power (`power_w_mean`). `BundleReader.events()` cannot call the gate, because the gate reads the journal through it." The sweep holds the constant `JOURNAL_ENERGY_READERS`, the set of `path::qualified function` for every swept function that (i) calls `.events()` or `._strict_jsonl_objects(...)` as an attribute, or holds the constant `events.jsonl`, and (ii) holds a string constant of at most 40 characters, without a space, that matches `power_w`, `energy`, `idle_power`, `joules`, or ends in `_j`. The computed set must equal the constant. At `cbfa9dc3` it is the four functions of X14. This is a screen by key name. It will not see a key built at run time.

**Test rows for amendment 58.**

| Row | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R58-1 | the tree | the class's public names equal the table's 30 keys | the reader with a public method `raw_trace` added that returns `self._tolerant_json("summary_metrics.json")` |
| R58-2 (CF6) | `trace_rows` with its `self.metadata()` statement removed | fails, naming `trace_rows` | a table with no check per kind (executed RED under the ruled check, X9) |
| R58-3 | the charging bundle | the four `gated_energy` methods raise `BatteryStatusRefusal` | `measured_window` without its gate call, under which it returns a window. NOT EXECUTED as a mutation; the tree's behaviour is executed (X6). |
| R58-4 | the charging bundle | the four `tolerant` methods return without raising | a `raw_summary` that calls `self.metadata()` first |
| R58-5 | the allowlist | no row with a tolerant operation in `joulewise/idle_dependence.py` carries `strict_validation` or `non_claim`; no reason in the allowlist holds the words "metadata first" or "follows BundleReader.metadata" outside a `behind_gate` row | the allowlist at `cbfa9dc3` |
| R58-6 | the tree | the computed journal set equals `JOURNAL_ENERGY_READERS` | a function added to `joulewise/aggregate.py` that reads `event["metadata"]["power_w_mean"]` from `BundleReader(p).events()` |

### Amendment 59 (amends amendment 51 (d) 2, and the callers form of `behind_gate` in 51 (f))

59. **A handler that ends in `return` cannot let execution past its `try`; and a `behind_gate` chain may pass through a function that holds no read of its own.**

**(a)** In amendment 51 (d) 2, "unless every handler of that `try` has `raise` (bare, or with an exception) as its last statement" is replaced by "unless every handler of that `try` has `raise` or `return` as its last statement". Reason: after a handler that ends in `return`, no statement of that function runs, so every statement after the `try` was reached through a body that finished. A handler that ends in `continue`, `break`, `pass`, or any other statement still makes the body a branch. Rule (d) 3 is unchanged: a read inside the handler, before its `raise` or `return`, is never gated by a gate call in the body.

This amendment does not touch amendment 52. Whether a handler may convert the gate's exception is that amendment's question. In `reduce_bundle` the handler names `BundleReadError`, which amendment 52 (e) leaves untouched, and a custody failure is not a `BundleReadError`, so it still leaves `reduce_bundle` as an exception (executed for `metadata()`, X7).

**(b)** In amendment 51 (f), the callers form's second assertion is replaced by: "and that in each listed function either (i) a gate call comes before and dominates that call, or (ii) the listed function itself has a `behind_gate` row, or (iii) every call of the listed function's own name, in any tracked file under `joulewise/` or `scripts/`, lies in a listed function to which this same assertion is applied. A chain that returns to a function already visited fails." A row's `callers` tuple therefore lists every function of the chain, up to and including the ones that hold the gate call.

**(c)** `joulewise/idle_dependence.py::derive_idle_mean_uncertainty`, operation `raw_artifact_bytes`, carries `behind_gate`, callers form, with `callers = ("joulewise/reduce.py::_reduce", "joulewise/reduce.py::_reduce_v060", "joulewise/reduce.py::reduce_bundle")`. `joulewise/reduce.py` stays byte-identical.

**Test rows for amendment 59.**

| Row | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R59-1 (G6) | `try:` gate `except ValueError: return None`, then the read after the `try` | not reported | rule (d) 2 as it stands, under which it is reported (executed, X4) |
| R59-2 (H7) | inside a `for`: `try:` gate `except ValueError: continue`; the read after the loop | reported | a rule that accepts any handler that leaves the `try` by a jump |
| R59-3 | the row of (c), on the tree; then with `_reduce_v060` removed from `callers` | passes; then fails naming `joulewise/reduce.py::_reduce_v060` | the callers form as it stands, under which the full row fails (executed, X11) |
| R59-4 (H8) | `try:` gate `except RuntimeError:` the read, then `raise` | reported | a detector that treats a `try` whose handlers all end in `raise` as no branch at all, handlers included. **The first judge's prototype is that detector** (executed, X4). |
| R59-5 (H9) | `try:` gate `finally:` the read | reported | the same |

---

## 8. Kept intact

- **Custody is never a status.** No amendment here adds a status, a handler or a conversion. R57-9 asserts that each gate body raises a custody failure when a battery reading is missing (executed on the tree, X7).
- **`joulewise/battery_float.py` and the excluded list are byte-identical.** The file's SHA-256 prefix is `4b4d7bb20625`; it, `reduce.py` and `bundle.py` are identical to base (X15). Amendments 57 to 59 edit one test file. They parse the frozen files and edit none.
- **The eight consumers do not import `battery_float`** (X15). They are `scripts/run_campaign.py`, `joulewise/whole_window.py`, `joulewise/analysis_engine/inputs.py`, `joulewise/floor_extraction.py`, `joulewise/aggregate.py`, `joulewise/window_duration_margins.py`, `scripts/mint_floor_artifact.py`, `scripts/extract_detection_floors.py`. Rule 57 (b) 2 adds a second guard: a consumer that called `authenticate_bundle` itself would fail the sweep (R57-5).
- **Text 8 is not amended.** The reader's behaviour does not change.

---

## 9. Not executed

- No unit test of the repository was run. V1 and V2 of the seat's brief: NOT EXECUTED.
- The first ruling's §6 and §10: not read.
- The 80 swept functions outside §6's table, and the 28 rows of the eight consumer modules: not read one by one.
- `inputs.py:1928`, `inputs.py:2834`, `run_campaign.py:2093`: the detector calls them gated; I did not read which gate.
- The 20 `raw_metadata` call sites: counted, not read.
- `request_rows`, `request_token_rows`, `suite_item_records`: what they return on a real bundle.
- That the reducer reaches the idle-power derivation on a complete passing bundle (from reading only).
- `scripts/check_window_provenance.py`; the whole of `_run_provenance` in `scripts/summarize_g2a_prefill_probe.py`.
- The refuter's search that `non_claim` (ii) requires, for any row.
- The counterfactuals of R57-9, R58-1, R58-3, R58-4, R58-5, R58-6 and R59-2 were not run as mutations. For R59-2 the source itself was run and is reported (X4); its counterfactual detector was not built.
- Whether any tracked file outside `joulewise/` and `scripts/` reads a bundle. The sweep does not look there, and neither did I.

---

## 10. Probes written in this session (`/tmp/cg_sweep/`; SHA-256 prefix)

| File | Prefix | What it is |
|---|---|---|
| `sweep49_orig.py` | `8e0d3bcdde3214e2` | the first judge's prototype, copied unchanged |
| `sweep51.py` | `2caee19f62c80916` | the detector with the erratum's rules, (d) 3 corrected |
| `sweep59.py` | `c7ef17cab8b81b3b` | the same with amendment 59 (a) |
| `cases59.py` | `364b97c967e9a9ea` | the self-test sources; `cases51b.py` is the same against `sweep51.py` |
| `gate57.py` | `7384f8cf5082d196` | the checks of amendments 57 and 58 (b), with CF1 to CF9 |
| `chain59.py` | `7879fb1a0e108c98` | the callers-form chain of amendment 59 (b) |
| `reader_methods.py` | `b50833d9da080da6` | X5 |
| `reader_probe.py`, `reader_probe_lib.py` | `7d743c67eca9660e`, `db81fe202374ef90` | X6; the second is the first's fixture builder, split out for reuse |
| `custody_probe.py` | `86bf1cd8a504341e` | X7 |
| `reduce_probe.py` | `d87bf59defe8f75e` | X8 |
| `cf7_behaviour.py` | `b3ef228d6f451af9` | X10 |

The files under `/tmp` are not durable. The amendment text and the rows are written so the seat can implement without them.

---

## 11. The resumed fix round 3: contents for amendment 51

One seat, the same WRITE_SCOPE as fix round 3, working tree from `cbfa9dc3`. Authority: amendment 51 of the erratum **as amended by amendments 57, 58 and 59 of this ruling**. Order:

1. **The detector.** Implement amendment 51 (a) to (e) with 59 (a) in rule (d) 2. Implement rule (d) 3 on its own terms: a read inside a handler or a `finally` is tested against the `try` it belongs to, whatever that `try`'s handlers end in. Show R51-1 to R51-13, R51-18 to R51-22, and R59-1, R59-2, R59-4, R59-5 RED under each counterfactual and GREEN after.
2. **The count.** Report rows, functions and source lines. Executed here with a prototype that lacks nothing the rules name: **120 rows, 89 functions, 126 lines**, and the row set equals the first judge's (X2). A different count is a finding to return with the differing rows listed, not to explain away.
3. **The two new classes.** Implement 57 (b) and (d) as checks inside the sweep. Give the three `gate_body` rows and the two `tolerant_definition` rows. Show R57-1 to R57-9.
4. **The reader pins.** Implement 58 (b), (c), (e). Show R58-1 to R58-6.
5. **The chain.** Implement 59 (b). Give the row of 59 (c). Show R59-3.
6. **The allowlist, all 120 rows,** each with class and reason, in the report. The classes are now six: `strict_validation`, `non_claim`, `historical`, `behind_gate`, `gate_body`, `tolerant_definition`. Apply amendment 51 (g) 1 to 6, 58 (d), and the rulings of §6's table. For every `non_claim` row state clause (i) with the fields read, or clause (ii) with what is written and to whom it is returned.
7. **Returns.** A row that fits no class after all of the above is returned to the lead with the row, what the function returns, and its callers. The seat does not invent a class and does not edit a frozen file.
8. **Then** V1, V2 and the builder's forward check, as the fix-round-3 brief states them.

The refuter, a model other than this one, checks every allowlist row, the method table of 58 (b), and the three amendments of this ruling.

Not part of this round: the seat's flag F2 (not ruled here); the lane for `joulewise/analysis_manifest_v3.py` named in amendment 52 (g).

---

## 12. Plain summary for Ed (5 lines)

1. The "sweep" is a test that lists every place in the code that reads a measured run's files without first running the battery check (the "gate": a run whose battery was charging or discharging has untrustworthy energy). It listed three reads it could not classify, and the implementer stopped to ask.
2. Two of the three are the battery check reading its own input, which nothing can precede. I ruled a new category for exactly three named functions, which the test verifies itself: the file's content may not leave the function before a verdict exists, and each function must be shown refusing a real charging run. A function cannot enter the category by being given the right name.
3. The third, `raw_summary`, is one of four "tolerant" reader methods that return a run's files with no battery check, on purpose, so that a refused or damaged run can still be inspected. I ran it: it does return the energy of a charging run. The earlier ruled text (text 8) allows this and relies on checking every caller, so I did not gate it. I closed three holes in that reliance, all in the test: a closed list of the reader's 30 public methods, a pin on the four methods that must check first, and a rule that a caller returning energy cannot be filed as a mere validator.
4. One caller was filed wrongly: the function that derives the idle-power uncertainty from the meter's raw capture. It is behind the check in fact, but the sweep's rules could not prove it, and the file it lives in is frozen. I amended two sweep rules (amendments 57 to 59 are this ruling's three numbered changes) so the proof goes through. I also found that the earlier prototype of the sweep missed a read placed inside an error handler, and added test cases that force it.
5. Nothing in the measurement code changes; every change is in one test file. I read 9 of the 89 listed functions closely and screened the rest by keyword, and the next step is for the implementer to class all 120 rows and for a second model to check each one.
