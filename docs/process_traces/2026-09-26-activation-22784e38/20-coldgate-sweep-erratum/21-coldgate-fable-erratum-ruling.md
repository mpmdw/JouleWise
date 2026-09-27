# Cold gate BFGS-S1-SWEEPCLASS-01, erratum: ruling (Fable 5.1, cold judge) on the paired refuter's findings RSW-1 to RSW-9 against amendments 57 to 59

Candidate: working tree `/Users/edr/code/JouleWise-wt-s1swcg-92472459`, detached @ `cbfa9dc3` (S1 fix round 3, partial). Base `1417c0c4`.
Charge: `20-coldgate-sweep-erratum/00-charge.md`, committed at `405199bd` (the file on disk and the committed blob both hash to SHA-256 prefix `683a014cd7d36b0c`).
Session: one foreground session, no subagents, no background tasks. No repository file edited; `git status --short` in the working tree printed 0 lines after every probe. Scratch: `/tmp/cg_sw_erratum/`. Session clock: 22:42 to 23:01 local.

---

## 0. Contamination disclosure

The charge told me not to read `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAUDE*.md`, `AGENTS.md`, the decision log, or memory and skill files. I opened none of them. Three exposures happened anyway, and I state each.

1. **Placed in my context by the harness before the charge arrived:** the owner's global `CLAUDE.md` (a pointer to orchestration doctrine, and a writing standard), the project `CLAUDE.md` (notes on the bridge to a second model), the memory index `MEMORY.md` (about 110 one-line summaries; one says this lane "needs amendment 51 (+57–59)"), and the names of the installed skills. I opened no file any of those lines points to and invoked no skill. None of those lines takes a position on any of the nine findings.
2. **Three lines of two forbidden files appeared in the output of a search I ran** (`git grep "envelope-gate"` over the tracked tree, probe Y13): one line of `RUN_STATE.md` and two of `TASK_QUEUE.md`. They say that a campaign using the envelope gate is queued. I did not open either file. What the lines could bias: my ruling on RSW-4, by suggesting the envelope gate will be run on future bundles. The code shows the same thing on its own (the command takes any bundle directories, Y10), and the ruling rests on the code.
3. **The ruling under review and I are the same model.** That is a shared-blind-spot risk. Two results below go against it: the refuter's replacement text for the cache rule admits a write the rule must refuse (§5, RSW-2), and the refuter's screen for the meter's raw capture misses 20 functions (§5, RSW-5). I found both by executing, not by reading.

The writing standard in the global `CLAUDE.md` asks that every term be defined at first use. The charge asks the same of the summary. I followed it. It changes wording, not rulings.

**A file I did not read.** While I worked, `11-opus-contract-refuter.md` appeared in the directory this ruling is written to (written 22:52; I saw it in a directory listing at 23:00, after this ruling was written). It is not in my packet. I did not open it, and nothing here responds to it.

What I read from the packet: the original charge; the ruling under review, in full; the refuter's report, in full; amendments 51 and 52 in the earlier erratum ruling (§10, lines 344 to 483). **Not read:** the rest of the earlier erratum ruling; text 8 and text 12 in their source file (I used the quotations in the ruling under review and in the refuter's report, which agree with each other).

---

## 1. Terms used in this ruling

Each term is defined once and used in that sense only. Terms marked (R) are those of the ruling under review, repeated so this file stands alone.

- **Bundle** (R). The directory one measured run leaves behind. It holds `config.json` (what was asked), `metadata.json` (what ran, the idle power measured before the run, and the two battery records), `summary_metrics.json` (the reduced numbers, energy included), `power_trace.csv` (the power samples), `events.jsonl` (the **stage journal**: one line per stage start, stage end and token), and the directory `raw/`.
- **Raw capture.** The power meter's own output, stored in the bundle as the meter wrote it: `raw/powermetrics.plist` and `raw/powermetrics_idle.plist` on the Apple machine, `raw/nvidia_smi*.csv` on the NVIDIA machine. Every energy number in a bundle is computed from these files.
- **Battery pair** (R). Two readings of the laptop battery, one before the measured span and one after. If either shows current flowing into or out of the battery, part of the energy the run drew did not pass through the meter's accounting, so the run's energy cannot be trusted.
- **Charging bundle** (R). A bundle whose battery pair shows the battery charging. In my probes it is built by the repository's own test helper (`WindowMembersTests.pair_bundle(..., charging=True)`), extended by the first judge's fixture builder with files that carry the value `4242.4242` (the **sentinel**), so that a returned value can be traced to the bundle's files.
- **Verdict** (R). The object the battery checker returns for one bundle. Its `status` is `pass`, `battery_float_confounded` (a reading shows charging or discharging), `battery_float_evidence_missing`, `not_applicable` (a simulated run) or `unobserved_historical` (one of 69 listed runs measured before the check existed).
- **Custody failure** (R). The exception `CustodyFailure` and its subclass `CustodyUnreadable`: a file the evidence depends on is missing, unreadable, or does not hash to its recorded digest. It is never a status. It stops the whole computation.
- **Energy-class value** (R). An energy, power, current, charge or voltage value, or a value computed from one.
- **The reader** (R). The class `BundleReader` in `joulewise/bundle_read.py`. One reader object reads one bundle.
- **The gate** (R). The check that a bundle's battery pair passes, in one of two forms. **Window form:** the function `authenticate_window_members(members)`, which takes a list of (label, bundle path), classes every one, and returns all verdicts or raises. **Reader form:** the method `BundleReader.metadata()`, which returns the parsed `metadata.json` only if the bundle's verdict is acceptable, and raises otherwise.
- **Gated energy accessors** (R). The four reader methods `trace_rows`, `summed_curve`, `source_curve`, `measured_window`. Each calls `self.metadata()` before anything else.
- **Tolerant accessors** (R). The four reader methods `raw_metadata`, `raw_config`, `raw_summary`, `raw_artifact_bytes`. Each returns a file's content, or `None` if the file is damaged, **without** the battery check. They exist so that a damaged or refused bundle can still be inspected and reported.
- **The cache.** The dictionary `self._cache` inside a reader, in which the reader keeps what it has already parsed so that a second call costs nothing. Each entry is a **slot**, named by its key. The slot `"metadata"` holds the parsed `metadata.json`. `metadata()` fills it once, after the verdict, and on every later call returns it **without checking again**.
- **The sweep** (R). The test `tests/test_bfgs_consumer_sweep.py`. It parses every tracked Python file under `joulewise/` and `scripts/` (209 files at `cbfa9dc3`) and lists every **read site**: a place that reads one of the three **watched files** (`summary_metrics.json`, `metadata.json`, `power_trace.csv`) or calls a tolerant accessor, with no gate call before it in the same function. Each listed place is a **row**, keyed (path, function, operation, watched file), and must have an entry in the test's **allowlist** with a **class** (a named reason category whose conditions the row must meet) and a reason.
- **Dominates** (R). Said of a gate call and a later statement: execution cannot reach the statement unless the gate call ran and returned normally.
- **Call, callee, reference.** In `r.raw_summary()` the whole expression is a **call** and `r.raw_summary` is its **callee**. A **reference** is the same name used where it is *not* the callee of a call: `get = r.raw_summary` takes the method without calling it, and `get()` calls it later under another name.
- **Binding.** Any statement that gives a name its meaning in a file: an import, an assignment, a `def`, a `class`, a parameter, the target of a `for`, `with` or `except … as`.
- **Module constant** (R, amendment 51 (a)). A name assigned at the top level of a file from an expression that holds a file name. A function that uses the name reads the file without the file's name appearing inside the function.
- **Consumer** (R). One of the eight modules that turn bundles into claimed numbers (listed in §7).
- **Claim artifact** (R, amendment 51 (f)). A file a paper number is taken from or licensed by: a floor artifact, a whole-window verdict row, an analysis output, a fill of the paper's results registry, a figure.
- **Counterfactual** (R). For a test row: the specific wrong implementation under which the row must fail. A row **goes RED** when it fails and is **GREEN** when it passes.
- **Frozen file** (R). A file the ruled texts require to stay byte-identical to base. Here: `joulewise/battery_float.py`, `joulewise/reduce.py`, `joulewise/bundle.py`.

**The gate and the four side doors the refuter found.** Every element of the diagram is named below it.

```
        code in any tracked file under joulewise/ or scripts/
     ________________|______________________________________________________
    |                 |                    |                  |             |
 [D0] calls       [D1] takes a         [D2] fills        [D3] gives     [D4] reads the
 the gate, or     reference to a       slot [S]          the gate's     raw capture
 calls a          tolerant accessor    itself            name another   by its path
 tolerant         and calls it                           meaning
 accessor         under another name
    |                 |                    |                  |             |
    v                 v                    v                  v             v
 seen by the      not a call of        [S] the slot       the sweep      not a watched
 sweep as         that name, so        "metadata" of      matches the    file, so the
 ruled            the sweep is         the cache          gate by name   sweep is silent
                  silent                   |              and counts
                                           v              the call
                  [G] BundleReader.metadata(): returns [S] if filled, without a check
                                           |
                                           v
                  [F] the four gated energy accessors, which trust [G]
```

- [D0] is the door amendments 51 and 57 to 59 already watch.
- [D1] is RSW-1. [D2] is RSW-2. [D3] is RSW-3. [D4] is RSW-5.
- [S], [G] and [F] are the slot, the reader-form gate and the gated energy accessors defined above.
- None of [D1] to [D4] is used anywhere in the tree at `cbfa9dc3` to reach an energy value ungated, as far as the refuter and I traced. Each is a way a **later** change could do so with every test GREEN.

---

## 2. Executed evidence (this session, foreground, working tree `cbfa9dc3`, Python 3.14.7)

"As ruled" means under amendments 51 and 57 to 59 as the ruling under review wrote them. The first judge's detector prototype is `/tmp/cg_sweep/sweep59.py` (SHA-256 prefix `c7ef17cab8b81b3b`, the value that ruling records).

| Id | Probe | Result (exact) |
|---|---|---|
| Y1 | `sweep59.py` on the tree; `diff` of its row list against the first judge's recorded output | `sites 126 distinct rows (path,function,operation,file) 120 functions 89`; the diff is empty. |
| Y2 | The first judge's `gate57.py`, `cases59.py`, `chain59.py`, re-run unchanged | `TREE cbfa9dc3: PASS | public BundleReader methods: 30`; CF1 to CF6 and CF9 `RED`, CF7 `GREEN`; `mismatches: 0`; the chain `PASS`, and with one caller left off it names `joulewise/reduce.py::_reduce_v060`. The ruling's X9 and X11 reproduce. |
| Y3 | The refuter's `alias.py` (B1), re-run | `A1 bound-method alias -> silent`, `A2 getattr by string -> silent`, `A3 map over readers -> silent`, `A4 direct call (control) -> REPORTED`. Reproduces. |
| Y4 | The refuter's `rebind.py` (B5), re-run | `R1 … module-level rebind -> silent`, `R2 … local def of same name -> silent`, `R3 … -> REPORTED`. Reproduces. |
| Y5 | The refuter's `cache_probe.py` (B3), re-run | `trace_rows after _cache.update on a CHARGING bundle: RETURNED 2 rows; sentinel True`. Reproduces. |
| Y6 | The refuter's `try_return.py` (A6), `journal58e.py` and `journal58e_eq.py` (B9), re-run | three `try` statements, as the refuter reports; the journal screen gives `count 5` when "holds the constant" is read as *contains* and `count 4` when read as *equals or ends in `/events.jsonl`*. The fifth is `joulewise/reduce.py::_reduce`. Reproduces. |
| Y7 | The refuter's `envelope_probe.py` (B7), re-run | first half: `tree: bundle_refused ['suite_manifest_missing'] battery_float_confounded: pre IsCharging is not No; …`. Second half crashed (`AttributeError: 'NoneType' object has no attribute 'workload_profile'`), as the refuter reports. Replaced by Y11. |
| Y8 | **Mine.** `scan123.py`: over the 209 tracked files, every use of a tolerant accessor's name that is not the callee of a call; every occurrence of `_cache`; every binding of `authenticate_window_members` or `BundleReader` | **References:** for `raw_summary`, `raw_metadata`, `raw_artifact_bytes`: 0 attributes that are not callees, 0 string constants. (A local variable named `raw_summary` exists in `scripts/run_campaign.py:2093`; a plain variable is not a reference to the method.) `raw_config`: 17 attributes, 60 plain names, 11 parameters, 6 keyword names. **Cache:** 47 occurrences, all in `joulewise/bundle_read.py`, all `self._cache`. **Bindings:** 21 files import `BundleReader` and 8 import `authenticate_window_members`, every one as `from joulewise.bundle_read import <name>` with no `as`; the only other bindings are the two definitions (`bundle_read.py:282`, `:410`). No class has `BundleReader` as a base. No statement assigns to an attribute of either name. **No file imports the module `joulewise.bundle_read` as a module, and no gate call is written as an attribute** (`x.authenticate_window_members(…)`). |
| Y9 | **Mine.** `rules60.py`: a prototype of the three rules as I rule them below (57 (b) 1, 57 (b) 4, 57 (d) 5). `cases60.py`, `cases60b.py`: the tree with one source replaced or added in memory | Tree: 0 reference rows, 0 binding violations, 0 cache violations. **References:** A1, A2, A3 and A5 (`operator.methodcaller("raw_artifact_bytes", …)`) silent as ruled, reported as `ref:<name>` under the new rule; A6 (`getattr(r, "raw_" + "summary")`) silent under both. **Bindings:** R1, R2, R4 (a module's own `class BundleReader` whose `metadata()` does nothing), R6 (`BundleReader.metadata = lambda self: {}`), R7 (a second import of the name from another module), R8 (a parameter named as the gate) are **silent as ruled** and RED under the new rule; R5 (a subclass that replaces `metadata()`) RED under the new rule. **Cache:** C1 to C6, C8, C9, C11 are **GREEN under rule 4 as ruled** and RED under the new rule; C7 (the subscript form) is RED under both; C10 (a new slot with a constant key) GREEN under both. **The refuter's replacement text admits C6, C8 and C9** (a key taken from a parameter; an alias of the dictionary; an f-string key with no fixed prefix). |
| Y10 | **Mine.** `behaviour.py`: the evasions, run on the charging bundle | `verdict: battery_float_confounded`. Controls: `BundleReader(b).trace_rows()` and `.metadata()` `raised BatteryStatusRefusal`; the real window gate `raised WindowBatteryRefusal`. **Returned with the sentinel present:** the alias, `getattr`, and `map` forms of RSW-1; `_cache.update(metadata=…)` then `trace_rows()`; a subclass whose `metadata()` returns `raw_metadata()`, then `trace_rows()`; a rebound gate name followed by a read of the summary by path. `_cache[name] = …` with `name = "metadata"`, then `summed_curve()`: returned without a refusal; my sentinel test did not find the value in the summed curve, and I did not look into why. |
| Y11 | **Mine.** `envelope_cf.py`: the counterfactual the refuter could not run. A real suite bundle from the repository's own builder (`EnvelopeGateTests.make_bundle`, a simulated run). The gate's **verdict** is then replaced by `battery_float_confounded`, because a charging suite bundle could not be built in budget. Then the callee `_manifest_record` is compiled without its `reader.metadata()` call | Verdict replaced, tree: `verdict=bundle_refused reasons=['suite_manifest_missing'] energies_in_output=None`. Verdict replaced, **callee without its gate call: `energies_in_output=5`**, first record `energy_gross_j: 1.5224999999989564`. So `envelope_gate.py:233` is the only gate on that path, and the refusal is reported under a reason code that names something else. |
| Y12 | **Mine.** `envelope_custody.py`: the same bundle, the verdict call made to raise `CustodyFailure` | `raised CustodyFailure | is CustodyFailure: True`. The handler in `analyze_envelope_gate` names `BundleReadError`, and a custody failure is not one, so it leaves as an exception. |
| Y13 | **Mine.** `git grep` over the whole tracked tree for `envelope_gate.v1`, `level_window_gross_energies_j`, `calibration_evidence_only`; `grep` for calls of `extract_rows(` and `realized_output_tokens(` | The three strings occur in `joulewise/envelope_gate.py`, `tests/test_envelope_gate.py`, and three prose files under `docs/`. **No tracked code reads the verdict, and no verdict file is committed.** `extract_rows` is called only at `tests/test_rpt001_report_slice.py:269`. `realized_output_tokens` is called only at `scripts/make_figures.py:332`, inside `extract_rows`. |
| Y14 | **Mine.** `rawcap.py`: the refuter's screen for the raw capture (a string constant naming the capture, inside the function). `rawcap2.py`: the same, also following module constants | The refuter's screen: **28** functions (its B10 reproduces). **13 module constants** are bound from a capture name (for example `RAW_POWERMETRICS_NAME` at `joulewise/reduce.py:115`, `SOURCE_ARTIFACT` at `joulewise/idle_dependence.py:25`, `GOVERNED_ARTIFACTS` at `joulewise/calibration_ledger.py:133`). **21 functions use one of them; 20 of those are not in the refuter's 28.** Among the 20: `joulewise/reduce.py::_derive_anchor_context`, `joulewise/cli.py::_verify_powermetrics_raw_to_trace`, `joulewise/cli.py::_strict_uncertainty_evidence_problems`. Union: **48**. |
| Y15 | **Mine.** String constants in `joulewise/controller.py::_axi_output_artifacts` (`:1986`, the one function under `joulewise/` and `scripts/` that writes `outputs/requests.jsonl` and `outputs/request_tokens.jsonl`), matched against energy-class key patterns | 26 lower-case string constants, 0 matches. |
| Y16 | **Mine.** Which methods of the reader hold the constant `events.jsonl` | `events` (`bundle_read.py:531`) **and `problems`** (`:1058`, `:1059`, handing the path to `_check_events`). |
| Y17 | `sed` of `joulewise/window_duration_margins.py:134-136` and `:940-975` | `def _refuse(reason, detail) -> None: raise WindowDurationMarginsRefusal(reason, detail)`: its whole body is one `raise`. |
| Y18 | `shasum joulewise/battery_float.py`; `git diff --quiet 1417c0c4 HEAD` on the three frozen files; an import search over the eight consumers; `git status --short` | prefix `4b4d7bb20625`; all three identical to base; no line that imports `battery_float`; 0 status lines. |

**Limits of the probes, stated so they are plain.**

- `rules60.py` is a prototype of mine, about 130 lines, written in this session. The seat implements from the amendment text, not from the prototype. One place where the two differ: the prototype lets `self._cache.get(…)` pass, and the ruled text lets no method of the cache pass. On the tree the difference is empty: no method of the cache is called anywhere (Y8, Y9).
- Y11 replaces the gate's verdict and not the bundle's battery readings. It shows which call stands between a refused bundle and the output. It does not show that a real charging suite bundle is refused; Y7's first half shows that, on a bundle with a stubbed suite manifest.
- Y14 is a screen by file name. I sorted **none** of the 48 functions by what they do with the capture.
- Y15 is a search by key name in one function. It is a screen, not a proof.
- My probes imported the repository's modules. Python keeps compiled copies in `__pycache__` directories, which the repository ignores; the early probes (Y3 to Y7) may have refreshed some. From Y9 on I ran with `PYTHONDONTWRITEBYTECODE=1`.

---

## 3. Rulings at a glance

| Finding | Ruling | Text change |
|---|---|---|
| RSW-1: a tolerant accessor used without a call is not a read site | **UPHOLD**, text extended | new 57 (d) 5; one item added to 51 (h); the sentence in the ruling's §4.4 is corrected |
| RSW-2: the cache-slot rule sees one write form | **UPHOLD the finding; REJECT the refuter's replacement text** (it admits three of the writes it should refuse, Y9) | 57 (b) 4 replaced by my text |
| RSW-3: a gate call can be claimed by rebinding the gate's name | **UPHOLD**, text extended (a subclass, an assignment to an attribute, a class of the same name) and 51 (c) narrowed | 57 (b) 1 replaced; 51 (c) window form narrowed |
| RSW-4: two row groups keep `historical` though its condition is false | **UPHOLD**, with three pins added so that each new reason is checked and not only stated | new amendment 60 |
| RSW-4, the lane | **UPHOLD** as a lane outside S1 | §9 |
| RSW-5: the raw capture is a second unwatched energy channel | **UPHOLD the finding; REJECT the refuter's screen** (it misses 20 functions, Y14) | new 58 (f), my text |
| RSW-6: the journal screen is ambiguous by one function | **UPHOLD** | one clause of 58 (e) replaced |
| RSW-7: `events` is filed as `other` | **UPHOLD the new kind; REJECT the proposed assertion** (it is false: `problems` also reads the journal, Y16) | 58 (b) gains the kind `journal`, my assertion |
| RSW-8: `request_rows`, `request_token_rows` hold no energy key | **UPHOLD**, no text change | none |
| RSW-9: a handler ending in a helper that always raises | **UPHOLD the refuter's disposition** (the rule is not widened); one sentence added so the behaviour is written down | one item added to 51 (h) |

**No amendment in this ruling changes production code.** Every change is in `tests/test_bfgs_consumer_sweep.py` (or `tests/test_bundle_read.py` for behaviour rows), both in S1's existing WRITE_SCOPE. One finding (the envelope gate's reason code) can only be fixed in production code. I rule it a lane outside S1 and do not rule the change itself.

---

## 4. Why the refuter's findings matter although it found no blocker

The refuter found no energy value that reaches a claim artifact without a gate, on any path it traced. I found none either. The findings are about something else: what the sweep **promises**. The charge that produced amendments 57 to 59 asked for rules that are "self-verifying so a new function cannot claim it by name alone". A sweep that is GREEN is read, by everyone after us, as "no ungated energy read exists". If a future change can add one through [D1] to [D4] and leave the sweep GREEN, that reading is false, and nobody will know. Each closure below is GREEN on the tree today (Y8, Y9), so landing it costs the seat the rule and its rows and nothing else.

---

## 5. The nine findings

### RSW-1 (57 (d)). UPHOLD

**The forcing problem.** The ruling under review justified the class `tolerant_definition` with this sentence (§4.4): "membership of that constant is exactly what causes every call to be reported". The sentence is about calls. A method can be used without a call of its name: taken as a value and called under another name, fetched by `getattr` with the name in a string, or handed to `map`.

**Worked example (executed, Y3, Y10).** On the charging bundle:

```python
get = BundleReader(b).raw_summary      # a reference, not a call
return get()["gross_energy_j"]         # a call of the name `get`
```

The detector as ruled reports nothing. The function returns `4242.4242`, the energy of a bundle the gate refuses.

**Evidence.** Y3 (the refuter's probe reproduces), Y9 (A1, A2, A3, A5 reported under the new rule), Y10 (each returns the sentinel), Y8 (the tree holds 0 such references for the three energy-returning names).

**Changes to the refuter's text, and why.**
1. **A reference is always reported; dominance is not applied to it.** The sweep sees where the method is taken. It cannot see where, or in which function, it is later called. A gate call before the line `get = r.raw_summary` proves nothing about the moment `get()` runs.
2. A reference outside any function is reported with the function name `<module>`.
3. A name built while the program runs (`"raw_" + "summary"`, Y9 A6) stays invisible. That goes into the list of what the sweep cannot see.

`raw_config` stays excluded, as the refuter proposed: the name is also a field and a variable in 94 places (Y8), and `config.json` holds no energy-class value (the ruling's §5.1).

**Exact text.** 57 (d) 5 in §6. The sentence in §4.4 of the ruling under review is corrected to: "membership of that constant is what causes every call **and every reference** to be reported (57 (d) 5)".

### RSW-2 (57 (b) 4). UPHOLD the finding; the replacement text is mine

**The forcing problem.** `metadata()` returns the slot `"metadata"` without checking again. So the battery check protects the four gated energy accessors only as long as nothing but `metadata()` can fill that slot. Rule 4 as ruled looks for one way of filling it: an assignment to `<expression>._cache["metadata"]`.

**Worked example (executed, Y5, Y10).**

```python
r = BundleReader(b)                              # b is a charging bundle
r._cache.update(metadata=r.raw_metadata())       # fills the slot; no subscript assignment anywhere
r.trace_rows()                                   # returns 2 rows, sentinel present
```

**Why the refuter's replacement text is not enough.** It allows any "assignment to a subscript of `self._cache`" and forbids only the constant key `"metadata"` outside `metadata()`. Three writes pass it (Y9):
- C6: `self._cache[name] = value`, with `name` a parameter that is `"metadata"` when the program runs;
- C9: the same with `key = f"{name}"`;
- C8: `slots = self._cache`, then `slots["metadata"] = value` (the write is to a subscript of `slots`).

The rule must therefore say which **keys** a write may use, and must forbid using the dictionary as a value. The tree has four writes whose key is computed. Each key is built as an f-string with a fixed prefix that ends in a colon (`raw-bytes:`, `source_curve:`, `jsonl:`, `tolerant:`), so none can equal `metadata`. The rule admits exactly that form.

**Evidence.** Y5, Y8 (all 47 occurrences are `self._cache` in `bundle_read.py`), Y9 (C1 to C11), Y10.

**Exact text.** 57 (b) 4 in §6.

### RSW-3 (57 (b) 1). UPHOLD, extended

**The forcing problem.** The sweep decides that a call is a gate call by the **name** of what is called. Rule 1 as ruled stops a second *definition* in `joulewise/bundle_read.py`. It says nothing about any other file giving the name another meaning.

**Worked example (executed, Y4, Y10).**

```python
from joulewise.bundle_read import authenticate_window_members
authenticate_window_members = lambda members: {}          # the name now means "do nothing"
def f(b):
    authenticate_window_members(((b.name, b),))           # counted as the gate
    return (b / "summary_metrics.json").read_text()       # silent; returns the sentinel
```

**What I add to the refuter's rule, each executed (Y9, Y10).**
- **A class of the same name in another file (R4).** Amendment 51 (c) accepts `X.metadata()` as the reader-form gate when `X` is "a call of `BundleReader`", and does not require that the file import the name. A file with its own `class BundleReader` whose `metadata()` does nothing is silent as ruled. The refuter's list ("`def`, `class`") covers it; I state it because the refuter did not test it.
- **A subclass (R5).** `class Quick(BundleReader)` with its own `metadata()` makes all four gated energy accessors return a charging bundle's rows (Y10). The subclass binds the name `Quick`, not `BundleReader`, so the refuter's rule does not see it.
- **An assignment to an attribute of the name (R6):** `BundleReader.metadata = …`.
- **The window form of 51 (c) is narrowed.** As ruled it also accepts the call "as an attribute" in a file that "imports that module". The tree uses neither form (Y8), no prototype ever implemented the module form (Y9, R12: the control is *reported*), and keeping it would need a second binding rule for module names. Deleting it errs toward reporting.

**Evidence.** Y4, Y8, Y9, Y10.

**Exact text.** 57 (b) 1 in §6, and the replacement of 51 (c)'s window form there.

### RSW-4 (51 (g) 4 and the ruling's §6). UPHOLD, with pins

**The forcing problem.** The class `historical` has a condition: the function "cannot be pointed at a later bundle". The earlier erratum left the eight `historical` rows to be checked against that condition. The refuter checked. For seven of the eight the condition is false.

**Evidence.**
- `joulewise/envelope_gate.py`: `analyze_envelope_gate(bundle_dirs, …)` takes its bundles from the command line (`joulewise/cli.py:2065`, `args.bundle_dirs`). It reads `raw_summary` at `:133` and, through `_level_window_energy_records`, at `:654`, and writes `energy_gross_j` per level into its output. The only gate on the path is `reader.metadata()` at `:233`, inside the callee `_manifest_record` (Y11: with that call removed, 5 energy records of a refused bundle are in the output).
- `scripts/make_figures.py`: `--input-manifest` and `--bootstrap-input-manifest` re-point the corpus (`:679-702`, read). `gate_inputs` reads the summary's `status` and nothing else (`:241-243`, read). After `gate_inputs`, `main` writes placeholders only; the comment at `:718` says the corpus's "measurements are never read into a regenerated publication artifact", and the code below it matches (read to `:740`). `extract_rows` does read `gross_energy_j` (`:356`), and has no caller outside the tests (Y13).
- No tracked code reads the envelope verdict (Y13).

**What I add to the refuter's text, and why.** The refuter's proposed reason for the envelope rows says "Every reader passes `reader.metadata()` in `_manifest_record` first". That is a statement about a gate, placed in a reason field, where nothing checks it. Row R58-5 of the ruling under review forbids exactly that kind of sentence outside a `behind_gate` row, because the allowlist at `cbfa9dc3` held three such sentences and one was false. So each statement in the new reasons gets a check:
1. "no tracked file reads the verdict" is pinned by a search the sweep runs (60 (c) 1);
2. "the callee gates every reader" is pinned by a behaviour row (R60-3; its counterfactual is executed, Y11);
3. "no production caller" is pinned by a search the sweep runs (60 (c) 2).

`realized_output_tokens` reads `workload_observed.output_token_count` from the metadata (`:292-293`, read) and token counts from the journal. I read the function to line 300 and not to its end. It is `non_claim` under clause (i) if the seat, reading all of it, finds no energy-class field; the refuter proposed clause (ii), which is also true (its one caller is `extract_rows`), and the seat may use either.

**Custody.** A custody failure raised by the gate leaves `analyze_envelope_gate` as an exception (Y12). Custody is not turned into a status there.

**Exact text.** Amendment 60 in §6.

**The lane.** `analyze_envelope_gate` reports a battery refusal under the reason code `suite_manifest_missing` (Y7, Y11). The file is outside S1's WRITE_SCOPE and the fix is a change to production code. It is lane BFGS-ENVELOPE-REASON-01 (§9). I do not rule the change.

### RSW-5 (58). UPHOLD the finding; the screen is mine

**The forcing problem.** The sweep watches three files and four methods. The raw capture is none of them, and it is where every energy number starts. A function that opens `raw/powermetrics.plist` by its path, computes an energy, and writes it to a claim artifact passes the sweep and never meets the gate. Text 8's sentence "every byte-level re-derivation passes the gate" is true of re-derivation through the reader and of nothing else.

**Why the refuter's screen is not enough (executed, Y14).** The refuter's screen lists a function if a string constant naming the capture appears **inside the function**. 13 module constants hold a capture name, and 20 functions read the capture through one of them with no such string inside. `joulewise/reduce.py::_derive_anchor_context` is one: it uses `RAW_POWERMETRICS_NAME`, defined at `reduce.py:115`. This is the same defect the earlier erratum fixed for the watched files (its row R51-3, "the watched name in a module constant"). The screen must follow module constants.

**Why a bare set is not enough.** The refuter read 6 of its 28 functions. A set that must equal a constant catches the 49th function. It says nothing about the 48 already there. The constant is therefore a mapping: each member carries a **kind**, which says what the function does with the capture, and a member that uses an energy-class value says where its gate is.

**Evidence.** Y14. **I sorted none of the 48 by kind.** That work is the seat's, and the refuter checks each entry.

**Exact text.** 58 (f) in §6.

### RSW-6 (58 (e)). UPHOLD

"Holds the constant `events.jsonl`" gives 5 functions read as *contains* and 4 read as *equals* (Y6). The fifth, `joulewise/reduce.py::_reduce`, holds the message text `"no measured_run window in events.jsonl "` and no path. The ruling's own count is 4, so *equals* is what it meant. **Exact text:** in 58 (e), "holds the constant `events.jsonl`" is replaced by "holds a string constant equal to `events.jsonl` or ending in `/events.jsonl`".

### RSW-7 (58 (b)). UPHOLD the kind; the assertion is mine

`events()` returns the journal, one of whose events carries `power_w_mean` (the ruling's X14; the refuter's A3). The last sentence of 58 (b) says that giving a method that returns an energy-class value the kind `other` is a finding. So `events` needs a kind of its own.

The refuter's proposed assertion is "the one public method that parses `events.jsonl`". It is false on the tree: `problems` names `events.jsonl` twice and hands it to the journal checker (Y16). An assertion that is false cannot be a test. **Exact text:** 58 (b) gains the row for kind `journal` given in §6, whose assertion is that the method `events` holds the string constant `events.jsonl` and that `events` is the callee name clause (i) of 58 (e) matches.

### RSW-8 (NIT). UPHOLD, no text change

The one function that writes `outputs/requests.jsonl` and `outputs/request_tokens.jsonl` holds no string constant that matches an energy-class key (Y15). `other` is the right kind for `request_rows` and `request_token_rows`. The item "what they return on a real bundle" in §9 of the ruling under review is resolved for those two by this screen. It stays open for `suite_item_records`, which the first judge classed by reading only.

### RSW-9 (NIT). UPHOLD the disposition: the rule is not widened

`window_duration_margins.py:944` has two handlers that end in `_refuse(…)`, and `_refuse` is one `raise` (Y17). Rule (d) 2, as amended by 59 (a), judges a handler by its last statement and sees a call, so it treats the `try` body as a branch. A read after that `try` would be reported although it is gated in fact. The error is toward reporting. Widening the rule to "a call of a function that always raises" would need the sweep to follow calls by name into other functions, which is the kind of matching that RSW-3 shows can be fooled. **Exact text:** one item added to 51 (h), in amendment 60 (d), so that the behaviour is written down. The rule itself does not change.

---

## 6. Amendments 57 to 60 as they stand after this ruling (exact text; the fix-round brief quotes these)

All four amend amendment 51 of the BFGS-S1-R2-01 erratum. All changes are in `tests/test_bfgs_consumer_sweep.py`, which is in S1's existing WRITE_SCOPE. The behaviour rows may be placed in that file or in `tests/test_bundle_read.py` (also in scope). **No production file is edited by these amendments.**

Text marked **[E2]** is new or changed by this erratum. Everything else is the text of the ruling under review, unchanged.

In every table of test rows, the column **Production site** names the code whose behaviour the row protects. Rows that "call the sweep's check" do so on the tracked source with one replacement made in memory; "the tree" is the tracked source unchanged.

### Amendment 57 (amends amendment 51 (f), the class table: two classes are added; **[E2]** and amends 51 (b) 1 and 51 (c))

57. **The gate's own reads, and the definitions of the tolerant accessors, are rows of two closed classes that the sweep checks itself.**

**(a) Terms.**
- A **gate definition** is one of two definitions in `joulewise/bundle_read.py`: the top-level function `authenticate_window_members`, and the method `metadata` of the class `BundleReader`. These are the definitions that a gate call of amendment 51 (c) resolves to.
- The **verdict source** is the function `authenticate_bundle` in `joulewise/battery_float.py`.
- A **gate body** is a gate definition or the verdict source. There are three.
- A **verdict call** is a call whose callee is named `_battery_verdict`, `authenticate_bundle` or `authenticate_pair`.
- A **content name**, inside one function, is a plain name bound (by assignment, annotated assignment, `:=`, or a `for` target) from an expression that holds a read-site call of amendment 51 (b) 2, or that mentions a content name. Binding is repeated until no name is added. A name bound from a verdict call is **not** a content name. A store to an attribute or a subscript binds nothing.
- A **leaving statement** is a `return` or `yield` whose value mentions a content name, or an assignment to an attribute or a subscript whose value mentions a content name.
- **[E2]** The **gate names** are `authenticate_window_members` and `BundleReader`.
- **[E2]** The **cache** is the attribute `_cache` of a reader: the dictionary in which the reader keeps what it has parsed. `metadata()` returns the entry with the key `"metadata"` without checking the verdict again.

**(b) The class `gate_body`.** A row may carry it only if the sweep asserts all six:

1. **[E2]** **Resolution and binding.** The row's (path, qualified function) is a gate body. The sweep computes the three from the tree, and asserts that `joulewise/bundle_read.py` holds exactly one top-level function `authenticate_window_members` and exactly one class `BundleReader` with exactly one method `metadata`. It further asserts, over every tracked file under `joulewise/` and `scripts/`:
   - (i) a gate name is bound only by `from joulewise.bundle_read import <name>` without `as`, or by its one definition in `joulewise/bundle_read.py`. No assignment, `def`, `class`, parameter, target of `for`, `with`, `except … as` or a comprehension, `match` capture, `global` or `nonlocal` statement, or other import binds either name;
   - (ii) no class names `BundleReader` among its bases;
   - (iii) no statement assigns to, or deletes, an attribute of a gate name (`BundleReader.metadata = …`), and no call of `setattr` or `delattr` has a gate name as its first argument.

   **And the window form of amendment 51 (c) is narrowed** to: "a call of `authenticate_window_members` **by bare name**, in a file that binds the name by `from joulewise.bundle_read import authenticate_window_members`, or in `joulewise/bundle_read.py` itself". The words "or as an attribute" and "or imports that module" are deleted. The tree uses neither (executed, Y8).
2. **Closed callers.** Every call of `authenticate_bundle`, by bare name or as an attribute, in a tracked file under `joulewise/` or `scripts/` lies in `joulewise/bundle_read.py::BundleReader._battery_verdict`. Every call of `_battery_verdict` **as an attribute** lies in a gate definition. (A module-level function of that name called by bare name is another function; one exists, `scripts/issue_calibration_acceptance_generation.py:1564`.)
3. **Content.** The function binds at least one content name and holds at least one verdict call. Every leaving statement comes after a verdict call, in source order, that dominates it by the rules of amendment 51 (d) as amended by 59 (a).
4. **[E2]** **The cache.** The sweep asserts, over every tracked file under `joulewise/` and `scripts/`:
   - (i) the name `_cache` occurs as an attribute, as a string constant, or as the name of a keyword argument, in no file other than `joulewise/bundle_read.py`;
   - (ii) in that file, every occurrence is `self._cache` inside a method of `BundleReader`, in one of four forms and no other: the assignment of an empty dictionary to `self._cache` in `__init__`; a membership test (`<key> in self._cache`, `<key> not in self._cache`); a subscript that is read (`self._cache[<key>]`); a subscript that is assigned (`self._cache[<key>] = …`). No method of it is called. It is not deleted from, not the target of an augmented assignment, and not used as a value (bound to another name, passed as an argument, returned);
   - (iii) in a subscript that is assigned, the key is a string constant, or a name bound exactly once in that method, by a plain assignment from an f-string whose first part is a string constant ending in `:`. (At `cbfa9dc3` four keys have the second form, with the prefixes `raw-bytes:`, `source_curve:`, `jsonl:`, `tolerant:`. A key of that form cannot equal `metadata`.)
   - (iv) a subscript assignment with the key `"metadata"` occurs in `BundleReader.metadata` and in no other function.

   (`metadata()` returns that slot; rule 3 guards the store into it.)
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
2. Its name is a member of the test's tolerant-accessor constant, **the same object** that amendment 51 (b) 1 matches calls against. (So every call of that name, on any receiver, in any tracked file, is a read site in its caller; **[E2]** and by item 5 every reference is one too.)
3. Its body, a docstring aside, is the single statement `return self._tolerant_json(<string constant>)`.
4. That string constant equals the row's watched file.

Two rows carry it: `BundleReader.raw_metadata` (`metadata.json`) and `BundleReader.raw_summary` (`summary_metrics.json`). `raw_config` names `config.json` and `raw_artifact_bytes` names no watched file, so neither definition is reported; both names stay in the constant.

5. **[E2]** **References. Amendment 51 (b) is extended by a fourth kind of read site:** any use of the name `raw_summary`, `raw_metadata` or `raw_artifact_bytes` that is not the callee of a call: an attribute of that name on any expression, or a string constant equal to it. It is reported as operation `ref:<name>`, watched file `-`, in the function that holds it, or in `<module>` if no function holds it. **Rule (d) of amendment 51 is not applied to it: a reference is reported whatever gate call precedes it**, because the sweep sees where the method is taken and cannot see where it is called. A `ref:` row is classed like any other row, and 58 (d) applies to it. `raw_config` is excluded: the name is also a field and a variable in 94 places (executed, Y8), and `config.json` holds no energy-class value. At `cbfa9dc3` the sweep reports no `ref:` row (executed, Y9).

**Test rows for amendment 57.**

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R57-1 | the three gate bodies; the two accessor definitions (`bundle_read.py`) | the tree | rules (b) 1 to 4 and (b) 6 hold; (d) holds for both rows; no `ref:` row | an allowlist with a fourth `gate_body` row; an allowlist where `BundleReader.problems` carries `gate_body` |
| R57-2 (CF1) | `BundleReader.metadata` (`bundle_read.py:446-459`) | `metadata()` with `self._cache["metadata"] = raw` moved before the verdict call | fails, naming the store | a check that requires only that a verdict call exist somewhere in the function (executed RED under the ruled check, Y2) |
| R57-3 (CF2) | the same | `metadata()` with the verdict call wrapped in `try:` … `except BundleReadError: return raw` | fails, naming the `return` | a check that tests source order and not dominance (Y2) |
| R57-4 (CF3) | `authenticate_window_members` (`bundle_read.py:282`) | the window gate with `verdicts[label + ":metadata"] = metadata` added after the read | fails, naming the store | a check that looks only at `return` statements (Y2) |
| R57-5 (CF4) | `aggregate._read_member` (`aggregate.py:155`) | its gate call replaced by `battery_float.authenticate_bundle(runs_root / member)` | fails, naming the caller | a class with no check on callers (Y2) |
| R57-6 (CF9) | `BundleReader.metadata` and the four gated energy accessors | a method `prime(self, value)` added to the reader whose body is `self._cache["metadata"] = value` | fails, naming `BundleReader.prime` | a check limited to the body of `metadata()` (Y2; Y9 C7) |
| **[E2]** R57-6b | the same | six sources: (C1) in `joulewise/zz_new.py`, `r = BundleReader(b); r._cache.update(metadata=r.raw_metadata()); return r.trace_rows()`; (C3) a reader method with `self._cache \|= {"metadata": value}`; (C4) `setattr(r, "_cache", {"metadata": v})`; (C6) a reader method with `self._cache[name] = value`, `name` a parameter; (C8) a reader method with `slots = self._cache` then `slots["metadata"] = value`; (C9) a reader method with `key = f"{name}"` then `self._cache[key] = value`. Then (C10) a reader method with `self._cache["extra"] = 1` | C1, C3, C4, C6, C8, C9 each fail, naming the file and the statement; C10 passes | rule 4 as first ruled: all six GREEN (executed, Y9). The refuter's replacement text: C6, C8, C9 GREEN (executed, Y9). Behaviour behind the row, executed: Y5, Y10. |
| R57-7 (CF8, CF5) | the gate definitions; `BundleReader.raw_summary` | (i) source for `joulewise/zz_new.py` defining its own `authenticate_window_members` that returns `(b / "summary_metrics.json").read_text()`, with an allowlist row of class `gate_body`; (ii) `raw_summary` with a body that also stores the value on `self` | (i) fails rule (b) 1; (ii) fails rule (d) 3 | a class claimed by function name or by reason text (Y2) |
| R57-8 | the three gate bodies | a charging bundle from `WindowMembersTests.pair_bundle(charging=True)`; each gate body called on it, the reader form on a fresh reader | `authenticate_bundle(b).status == "battery_float_confounded"`; `BundleReader(b).metadata()` raises `BatteryStatusRefusal` with that status; `authenticate_window_members((("m", b),))` raises `WindowBatteryRefusal` naming `m` | **CF7:** `metadata()` with its status test replaced by `if False:`. The structure rows are GREEN under CF7 and this row is RED (the ruling's X9, X10; Y2 reproduces the GREEN). |
| R57-9 | the three gate bodies | a passing bundle with `raw/battery_float.post.ioreg` deleted | each of the three raises, and `isinstance(exc, battery_float.CustodyFailure)`; the window form's exception has `window_member == "m"`; **no verdict is returned** | a gate that turns the missing file into the status `battery_float_evidence_missing` (GREEN on the tree per the ruling's X7; the counterfactual is NOT EXECUTED) |
| **[E2]** R57-10 | every caller of `raw_summary`, `raw_metadata`, `raw_artifact_bytes` (39 call sites at `cbfa9dc3`) | four sources in `joulewise/zz_new.py`: (A1) `get = BundleReader(b).raw_summary; return get()["gross_energy_j"]`; (A2) `getattr(BundleReader(b), "raw_summary")()`; (A3) `map(BundleReader.raw_summary, readers)`; (A1g) A1 with `r = BundleReader(b); r.metadata()` placed before it and the alias taken from `r` | each reported as `ref:raw_summary`, A1g included | amendment 51 (b) 1 as ruled: A1 to A3 silent (executed, Y3, Y9). For A1g: a rule that applies dominance to a reference (my prototype, which applies none, reports A1g at line 5: executed after the table of §2 was written, with `rules60.py`). |
| **[E2]** R57-11 | every gate call in the tree (the 8 files that import the window gate, the 21 that import the reader) | six sources in `joulewise/zz_new.py`: (R1) import, then `authenticate_window_members = lambda members: {}`; (R2) import, then a local `def` of the same name; (R4) the file's own `class BundleReader` with a `metadata()` that returns `{}`; (R5) `class Quick(BundleReader)` with its own `metadata()`; (R6) `BundleReader.metadata = lambda self: {}`; (R7) a second import of the name from another module. Then (R9) the import and a call, nothing else | R1, R2, R4 to R7 each fail, naming the binding; R9 passes | amendment 51 (c) as ruled: R1, R2, R4, R6, R7 silent (executed, Y4, Y9). The refuter's text for R5: GREEN, because a subclass binds another name (by reading of that text; the behaviour is executed, Y10). |
| **[E2]** R57-12 | `BundleReader.trace_rows`, `summed_curve`, `source_curve`, `measured_window` | the charging bundle of R57-8; `class Quick(BundleReader)` whose `metadata()` returns `self.raw_metadata()`, defined inside the test; `Quick(b).trace_rows()` | returns rows **(this row asserts the hole is real, so that R57-11 is known to guard something)** | a reader whose gated accessors call `BundleReader.metadata(self)` by class, under which the subclass is refused. Executed on the tree: returned, sentinel present (Y10). |

### Amendment 58 (adds pins to text 8's sentence on accessors; changes no behaviour of the reader)

58. **The reader's public methods are a closed, classed list; the four energy accessors are pinned; a caller that returns energy cannot carry a validator's class; [E2] the two energy channels the sweep does not watch are inventoried.**

**(a) Stated, so that no later reader takes it for an oversight.** `raw_summary`, `raw_metadata` and `raw_artifact_bytes` return energy-class content from a bundle the gate refuses, and from a bundle whose battery evidence is missing (executed: the ruling's X6, X7; Y10). Text 8 ruled this. They are not gated. Their control is the sweep's row at every call site **[E2]** and at every reference.

**(b) The method table.** The sweep holds the constant `READER_METHODS`, a mapping from each public name of `BundleReader` to one kind:

| Kind | Names | What the sweep asserts of a name of this kind |
|---|---|---|
| `gate` | `metadata` | it is the reader-form gate definition of 57 (a) |
| `gated_energy` | `trace_rows`, `summed_curve`, `source_curve`, `measured_window` | the method's first statement, a docstring aside, is the expression statement `self.metadata()` |
| `tolerant` | `raw_metadata`, `raw_config`, `raw_summary`, `raw_artifact_bytes` | the name is in the tolerant-accessor constant, and the constant has no other member |
| **[E2]** `journal` | `events` | the method's body holds the string constant `events.jsonl`, and `events` is the callee name that clause (i) of 58 (e) matches. (It returns an energy-class value, `power_w_mean`; it cannot call the gate, because the gate reads the journal through it; its callers are governed by 58 (e).) |
| `other` | `path`, `config`, `problems`, `is_complete`, `is_event_v2`, `is_frozen_legacy_identity`, `rail_manifest`, `request_roster`, `request_rows`, `request_token_rows`, `request_phase_windows`, `runtime_cleanup_ok`, `phase_windows`, `token_timestamps`, `suite_manifest`, `suite_item_records`, `suite_window`, `item_windows`, `block_windows`, `level_windows` | nothing beyond the sweep's ordinary rows |

The sweep asserts that the set of names defined in the class body that do not begin with `_` **equals** the table's keys (30 at `cbfa9dc3`: 1 + 4 + 4 + 1 + 20). A new public method fails the test until it has a kind. Giving a new method the kind `other` when it returns an energy-class value is a finding for the refuter, who checks the table as it checks the allowlist.

**(c) Behaviour of the accessors**, on a fresh reader over the charging bundle of R57-8: each `gated_energy` method raises `BatteryStatusRefusal`; each `tolerant` method returns without raising. The second half is asserted so that a later change that gates a tolerant accessor is seen and ruled, not so that it is forbidden.

**(d) Callers that return energy.** A row whose operation is `raw_summary`, `raw_metadata` or `raw_artifact_bytes` **[E2]** (or `ref:` followed by one of those names), in a function that returns, writes or passes on an energy-class value taken from the accessor's result, may carry only `behind_gate`, `historical`, or `non_claim` under clause (ii). It may not carry `strict_validation` or `non_claim` under clause (i). This extends amendment 51 (g) 1, which says the same of the eight consumer modules, to every module. Applied at `cbfa9dc3`:
1. `joulewise/idle_dependence.py::derive_idle_mean_uncertainty`: `behind_gate`, callers form, by amendment 59 (c).
2. `joulewise/reduce.py::_resolve_reducer_version`, `raw_summary`: `strict_validation`, reason "reads `summary_provenance.reducer_version` before the gate; returns the version string only". The words "authenticates … first" are removed from all three `reduce.py` reasons: they are false (executed, the ruling's X8).
3. **[E2]** The rows of `joulewise/envelope_gate.py` and `scripts/make_figures.py`: by amendment 60.

**(e) The stage journal.** Amendment 51 (h) gains the item: "**A value read from the stage journal.** `events.jsonl` is not a watched file. One of its events holds the idle mean power (`power_w_mean`). `BundleReader.events()` cannot call the gate, because the gate reads the journal through it." The sweep holds the constant `JOURNAL_ENERGY_READERS`, the set of `path::qualified function` for every swept function that (i) calls `.events()` or `._strict_jsonl_objects(...)` as an attribute, or **[E2]** holds a string constant equal to `events.jsonl` or ending in `/events.jsonl`, and (ii) holds a string constant of at most 40 characters, without a space, that matches `power_w`, `energy`, `idle_power`, `joules`, or ends in `_j`. The computed set must equal the constant. At `cbfa9dc3` it is four functions (executed, Y6): `joulewise/cli.py::_strict_uncertainty_evidence_problems`, `joulewise/reduce.py::_reduce_v060`, `scripts/analyze_phase_share.py::analyze_bundle`, `scripts/paper/partial_record_enclosure.py::_derive_bundle_authenticated`. This is a screen by key name. It will not see a key built at run time.

**(f) [E2] The meter's raw capture.**

1. Amendment 51 (h) gains the item: "**A read of the meter's raw capture by its path.** `raw/powermetrics.plist`, `raw/powermetrics_idle.plist` and `raw/nvidia_smi*.csv` are not watched files. Every energy number in a bundle is computed from them."
2. A **capture constant** is a string constant that matches `^(raw/)?(powermetrics(_idle)?\.plist|nvidia_smi[^ ]*\.csv)$`. A **capture name** is a name assigned, at the top level of any tracked file under `joulewise/` or `scripts/` (the adapters included) or at the top level of a class body there, from an expression that holds a capture constant or another capture name. Capture names are collected over all those files first and matched by name, as amendment 51 (a) does for module constants.
3. The sweep computes the set of `path::qualified function` for every function, in a tracked file under `joulewise/` or `scripts/` and outside `joulewise/adapters/` (the meter adapters, which write the capture), that holds a capture constant, or uses a capture name as a plain name or as an upper-case attribute. Nested functions are separate functions and inherit nothing.
4. The sweep holds the constant `RAW_CAPTURE_READERS`, a mapping from each member to a **kind**. The computed set must **equal** the mapping's keys. The kinds:

| Kind | The function | Second field |
|---|---|---|
| `names` | names the capture in a list, a schema or a message, and opens nothing | none |
| `custody` | hashes the capture, tests that it exists, or copies it whole; parses no value inside it | none |
| `timing` | parses the capture and uses only times, durations or sample counts | none |
| `energy` | parses the capture and uses an energy-class value | `gate`: the string `"in_function"`, or a `callers` tuple |

5. For a member of kind `energy` the sweep asserts: with `"in_function"`, that the function holds a gate call that comes before, and dominates, every call in it whose receiver or argument mentions a capture constant or a capture name; with a `callers` tuple, the callers-form assertion of amendment 51 (f) as amended by 59 (b).
6. A member of kind `energy` that has no gate is **not** given a kind. The seat returns it to the lead with the function, what it returns, and its callers. It is a finding, and its fix is lane BFGS-RAWCAPTURE-01 (§9). The seat does not edit production code for it.
7. The refuter checks every entry's kind by reading the function.

**Size, so the seat can tell a wrong implementation from a right one.** My prototype counts 48 members at `cbfa9dc3`: 28 that hold a capture constant, and 20 more that use one of 13 capture names (executed, Y14). Three of the 48 use only `LOGICAL_FILE_COUNT`, a number computed from a list that holds a capture constant; they are of kind `names`. A count other than 48 is returned with the differing members listed, not explained away.

**Test rows for amendment 58.**

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R58-1 | `class BundleReader` (`bundle_read.py:410`) | the tree | the class's public names equal the table's 30 keys | the reader with a public method `raw_trace` added that returns `self._tolerant_json("summary_metrics.json")` |
| R58-2 (CF6) | `BundleReader.trace_rows` | `trace_rows` with its `self.metadata()` statement removed | fails, naming `trace_rows` | a table with no check per kind (executed RED under the ruled check, Y2) |
| R58-3 | the four `gated_energy` methods | the charging bundle | each raises `BatteryStatusRefusal` | `measured_window` without its gate call, under which it returns a window. NOT EXECUTED as a mutation; the tree's behaviour is executed (Y10, two of the four). |
| R58-4 | the four `tolerant` methods | the charging bundle | each returns without raising | a `raw_summary` that calls `self.metadata()` first |
| R58-5 | the allowlist | the allowlist | no row with a tolerant operation in `joulewise/idle_dependence.py` carries `strict_validation` or `non_claim`; no reason in the allowlist holds the words "metadata first" or "follows BundleReader.metadata" outside a `behind_gate` row | the allowlist at `cbfa9dc3` |
| R58-6 | every caller of `BundleReader.events` | the tree | the computed journal set equals `JOURNAL_ENERGY_READERS` | a function added to `joulewise/aggregate.py` that reads `event["metadata"]["power_w_mean"]` from `BundleReader(p).events()` |
| **[E2]** R58-6b | `joulewise/reduce.py::_reduce` | the tree | `joulewise/reduce.py::_reduce` is **not** in the computed journal set | a screen that reads "holds the constant" as *contains* (executed: 5 members, Y6) |
| **[E2]** R58-7 | every reader of the raw capture (48 functions) | a function added to `joulewise/aggregate.py` whose body is `return (p / "raw" / "powermetrics.plist").read_bytes()` | the sweep fails, naming the function | a sweep with no inventory of the capture |
| **[E2]** R58-8 | `joulewise/reduce.py::_derive_anchor_context` and the 19 functions like it | (i) the tree; (ii) a function added to `joulewise/aggregate.py` whose body is `return (p / "raw" / RAW_POWERMETRICS_NAME).read_bytes()`, with `from joulewise.reduce import RAW_POWERMETRICS_NAME` | (i) `joulewise/reduce.py::_derive_anchor_context` is a member; (ii) the sweep fails, naming the function | the refuter's screen, which looks only for a capture constant inside the function: on the tree it misses 20 functions, this one among them (executed, Y14) |
| **[E2]** R58-9 | `BundleReader.events` (`bundle_read.py:531`) | the tree; then the table with `events` moved to `other` | passes; then fails | a table with no kind `journal` |

### Amendment 59 (amends amendment 51 (d) 2, and the callers form of `behind_gate` in 51 (f)). Unchanged by this erratum

59. **A handler that ends in `return` cannot let execution past its `try`; and a `behind_gate` chain may pass through a function that holds no read of its own.**

**(a)** In amendment 51 (d) 2, "unless every handler of that `try` has `raise` (bare, or with an exception) as its last statement" is replaced by "unless every handler of that `try` has `raise` or `return` as its last statement". Reason: after a handler that ends in `return`, no statement of that function runs, so every statement after the `try` was reached through a body that finished. A handler that ends in `continue`, `break`, `pass`, or any other statement still makes the body a branch. Rule (d) 3 is unchanged: a read inside the handler, before its `raise` or `return`, is never gated by a gate call in the body.

This amendment does not touch amendment 52. Whether a handler may convert the gate's exception is that amendment's question. In `reduce_bundle` the handler names `BundleReadError`, which amendment 52 (e) leaves untouched, and a custody failure is not a `BundleReadError`, so it still leaves `reduce_bundle` as an exception.

**(b)** In amendment 51 (f), the callers form's second assertion is replaced by: "and that in each listed function either (i) a gate call comes before and dominates that call, or (ii) the listed function itself has a `behind_gate` row, or (iii) every call of the listed function's own name, in any tracked file under `joulewise/` or `scripts/`, lies in a listed function to which this same assertion is applied. A chain that returns to a function already visited fails." A row's `callers` tuple therefore lists every function of the chain, up to and including the ones that hold the gate call.

**(c)** `joulewise/idle_dependence.py::derive_idle_mean_uncertainty`, operation `raw_artifact_bytes`, carries `behind_gate`, callers form, with `callers = ("joulewise/reduce.py::_reduce", "joulewise/reduce.py::_reduce_v060", "joulewise/reduce.py::reduce_bundle")`. `joulewise/reduce.py` stays byte-identical.

**Test rows for amendment 59.**

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R59-1 (G6) | `reduce.reduce_bundle` (`reduce.py:2651`); `calibration_bracketing.py:2758` | `try:` gate `except ValueError: return None`, then the read after the `try` | not reported | rule (d) 2 as it stood before 59, under which it is reported (the ruling's X4) |
| R59-2 (H7) | any gate inside a loop | inside a `for`: `try:` gate `except ValueError: continue`; the read after the loop | reported | a rule that accepts any handler that leaves the `try` by a jump |
| R59-3 | `idle_dependence.derive_idle_mean_uncertainty` (`idle_dependence.py:198`), called at `reduce.py:3302` and `:3563` | the row of (c), on the tree; then with `_reduce_v060` removed from `callers` | passes; then fails naming `joulewise/reduce.py::_reduce_v060` | the callers form as it stood before 59, under which the full row fails (the ruling's X11; Y2 reproduces both halves) |
| R59-4 (H8) | any handler in a swept function | `try:` gate `except RuntimeError:` the read, then `raise` | reported | a detector that treats a `try` whose handlers all end in `raise` as no branch at all, handlers included (the ruling's X4) |
| R59-5 (H9) | the same | `try:` gate `finally:` the read | reported | the same (Y2: `REPORTED H9`) |

### Amendment 60 ([E2], new; amends amendment 51 (g) 4, 51 (f), 51 (h) and test row R51-14)

60. **A class is held only where its condition is true; and a statement in a reason is either checked or not made.**

**(a) 51 (g) 4 is replaced by:** "`historical` is held by one row at `cbfa9dc3`: `scripts/issue_dg071_dg075_statistics.py::main` (amendment 51 (e)). The seven other rows that held it do not meet its condition: both files can be pointed at any bundle from the command line (executed and read, Y11, Y13). They are re-classed by 60 (b). **Any new `historical` row needs a cold gate.**"

**(b) The seven rows.**

| Row | Class | Reason (exact) |
|---|---|---|
| `joulewise/envelope_gate.py::analyze_envelope_gate`, `raw_summary` | `non_claim` (ii) | "reads whether `suite_metrics` is present; returns the envelope verdict (`envelope_gate.v1`) to `joulewise/cli.py::_cmd_envelope_gate`, which writes it to `--output` or prints it; no tracked code reads that verdict (60 (c) 1); the gate is in the callee `_manifest_record` (R60-3)" |
| `joulewise/envelope_gate.py::_level_window_energy_records`, `raw_summary` | `non_claim` (ii) | "reads `suite_metrics.levels[].energy_gross_j`; returns the records to `analyze_envelope_gate`, which places them in the envelope verdict under `calibration_evidence_only`; no tracked code reads that verdict (60 (c) 1); the gate is in the callee `_manifest_record` (R60-3)" |
| `scripts/make_figures.py::gate_inputs`, `raw_summary` | `non_claim` (i) | "field read: `status`" |
| `scripts/make_figures.py::realized_output_tokens`, `raw_metadata` | `non_claim` (i) if the seat, reading the whole function, finds that no field read is energy-class, with the fields stated (`workload_observed.output_token_count` is one); otherwise `non_claim` (ii), "returns a token count to `extract_rows`, which has no caller (60 (c) 2)" | as stated |
| `scripts/make_figures.py::extract_rows`, `raw_config`, `raw_metadata`, `raw_summary` (three rows) | `non_claim` (ii), third field `callers = ()` | "reads `gross_energy_j` and `energy_request_j`; returns rows to no function under `joulewise/` or `scripts/` (60 (c) 2); `main` writes placeholders that hold no measurement" |

**(c) Two checks that the sweep runs for `non_claim` (ii) rows. Amendment 51 (f), clause (ii), gains:** "A `non_claim` (ii) row may carry a third field, and the sweep checks it:
1. `output_marker`: a string that identifies the record the function writes. The sweep asserts that the string occurs in no tracked file under `joulewise/` or `scripts/` other than the row's own file. For the two envelope rows the marker is `envelope_gate.v1`.
2. `callers = ()`: the sweep asserts that no call of the function's name, by bare name or as an attribute, occurs in any tracked file under `joulewise/` or `scripts/`.

A `non_claim` (ii) row without a third field is checked by the refuter's search, as before."

**(d) 51 (h) gains two items:**
- "**A gate in a callee.** A gate call inside a function that the row's function calls is not seen. `joulewise/envelope_gate.py` is the one place found where a read is safe only for that reason (executed, Y11); row R60-3 pins it by behaviour."
- "**A handler that ends in a call of a function that always raises** (`_refuse(…)` in `joulewise/window_duration_margins.py:944`) is judged by its last statement, which is a call. The sweep treats the `try` body as a branch and reports a read after it although the read is gated in fact. The error is toward reporting. The rule is not widened."

And, from RSW-1: "**A name built while the program runs.** `getattr(reader, "raw_" + "summary")` holds neither the attribute nor the string constant, and is not seen (executed, Y9, A6)."

**(e) R51-14 is amended:** "every class is one of the four" becomes "every class is one of the six: `strict_validation`, `non_claim`, `historical`, `behind_gate`, `gate_body`, `tolerant_definition`".

**Test rows for amendment 60.**

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R60-1 | `envelope_gate.analyze_envelope_gate` (`envelope_gate.py:71`), `cli._cmd_envelope_gate` (`cli.py:2057`) | (i) the tree; (ii) a function added to `joulewise/aggregate.py` that holds the string `envelope_gate.v1` | (i) passes; (ii) the sweep fails, naming the file | a `non_claim` (ii) row whose statement about readers is checked by nobody |
| R60-2 | `make_figures.extract_rows` (`make_figures.py:314`) | (i) the tree; (ii) `scripts/make_figures.py` with `rows = extract_rows(runs_root, manifests, tree)` added to `main` | (i) passes; (ii) the sweep fails, naming `scripts/make_figures.py::main` | a row whose "no caller" is a sentence only. Executed on the tree: the one call is in `tests/` (Y13). The mutation is NOT EXECUTED. |
| R60-3 | `envelope_gate._manifest_record` (`envelope_gate.py:228-233`), the only gate before the reads at `:133` and `:654` | a suite bundle from `EnvelopeGateTests.make_bundle()`; `BundleReader._battery_verdict` patched, for the test only, to return the real verdict with `status` replaced by `battery_float_confounded`; `analyze_envelope_gate([bundle], lambda path: [])` | `verdict == "bundle_refused"`, and the key `calibration_evidence_only` is absent | `_manifest_record` with `reader.metadata()` replaced by `reader.raw_metadata() or {}`: the output holds 5 energy records (**executed RED, Y11**) |
| R60-4 | the same | the same bundle; `_battery_verdict` patched to raise `battery_float.CustodyFailure` | `analyze_envelope_gate` raises, and `isinstance(exc, battery_float.CustodyFailure)`; no verdict is returned | a handler in `analyze_envelope_gate` widened from `BundleReadError` to `Exception`. Executed GREEN on the tree (Y12); the counterfactual is NOT EXECUTED. |
| R60-5 | the allowlist | the allowlist | exactly one row carries `historical`, and its path is `scripts/issue_dg071_dg075_statistics.py` | the allowlist at `cbfa9dc3` (eight rows) |

R60-3 asserts the refusal and not its reason code. The reason code is wrong today (`suite_manifest_missing`) and lane BFGS-ENVELOPE-REASON-01 will change it; the row must stay GREEN across that change.

---

## 7. Kept intact

- **Custody is never a status.** No amendment here adds a status, a handler or a conversion. R57-9 and R60-4 assert that a custody failure leaves as an exception (executed on the tree: the ruling's X7; Y12).
- **Authentication precedes every exclusion decision.** No amendment here changes the order of any production code. Rule 57 (b) 3 (no content leaves a gate body before a verdict exists) and rule 57 (b) 4 (nothing but the gate fills the slot the gate returns) both guard that order. One observation, not ruled: `analyze_envelope_gate` runs strict validation before the gate, and refuses the **whole** input when any bundle fails it. That is a refusal of the run, not the exclusion of a member, and the function is not one of the eight consumers. It is noted for the lead under lane BFGS-ENVELOPE-REASON-01.
- **`joulewise/battery_float.py` and the excluded list are byte-identical.** SHA-256 prefix `4b4d7bb20625`; it, `reduce.py` and `bundle.py` are identical to base `1417c0c4` (Y18). Amendments 57 to 60 parse the frozen files and edit none.
- **The eight consumers do not import `battery_float`** (Y18). They are `scripts/run_campaign.py`, `joulewise/whole_window.py`, `joulewise/analysis_engine/inputs.py`, `joulewise/floor_extraction.py`, `joulewise/aggregate.py`, `joulewise/window_duration_margins.py`, `scripts/mint_floor_artifact.py`, `scripts/extract_detection_floors.py`.
- **Amendments 57 to 60 change test code only.** I rule no production change. The one defect that needs production code (the envelope gate's reason code) is a lane outside S1.
- **Text 8 is not amended.** The reader's behaviour does not change.

---

## 8. The resumed S1 fix round 3: contents for amendment 51

One seat, the same WRITE_SCOPE as fix round 3, working tree from `cbfa9dc3`. Authority: amendment 51 of the earlier erratum **as amended by amendments 57, 58, 59 and 60 as they stand in §6 of this ruling**. §6 replaces §7 of the ruling under review. Order:

1. **The detector.** Implement amendment 51 (a) to (e), with: 59 (a) in rule (d) 2; rule (d) 3 on its own terms (a read inside a handler or a `finally` is tested against the `try` it belongs to, whatever that `try`'s handlers end in); the window form of 51 (c) narrowed as 57 (b) 1 states; the `ref:` read site of 57 (d) 5. Show R51-1 to R51-13, R51-18 to R51-22, R59-1, R59-2, R59-4, R59-5 and R57-10 RED under each counterfactual and GREEN after.
2. **The count.** Report rows, functions and source lines. Executed here: **120 rows, 89 functions, 126 lines, and 0 `ref:` rows** (Y1, Y9). A different count is a finding to return with the differing rows listed, not to explain away.
3. **The two new classes.** Implement 57 (b) and (d), with rule (b) 1 and rule (b) 4 as they stand in §6. Give the three `gate_body` rows and the two `tolerant_definition` rows. Show R57-1 to R57-12, R57-6b included.
4. **The reader pins.** Implement 58 (b) with the kind `journal`, 58 (c), and 58 (e) with the equality reading. Show R58-1 to R58-6b and R58-9.
5. **The raw-capture inventory.** Implement 58 (f). Report the computed set and its size (48 by my prototype). Give every member a kind by reading the function. Return every member of kind `energy` that has no gate. Show R58-7 and R58-8.
6. **The chain.** Implement 59 (b). Give the row of 59 (c). Show R59-3.
7. **The re-classed rows.** Implement 60 (b), (c) and (e). Show R60-1 to R60-5.
8. **The allowlist, all rows,** each with class and reason, in the report. Apply amendment 51 (g) 1 to 3, 5 and 6, amendment 60 (a) in place of (g) 4, 58 (d), and the rulings in the table of §6 of the ruling under review. For every `non_claim` row state clause (i) with the fields read, or clause (ii) with what is written and to whom it is returned.
9. **Returns.** A row, or a raw-capture member, that fits no class after all of the above is returned to the lead with the function, what it returns, and its callers. The seat does not invent a class or a kind and does not edit a frozen file.
10. **Then** V1, V2 and the builder's forward check, as the fix-round-3 brief states them.

The refuter, a model other than this one, checks every allowlist row, the method table of 58 (b), every entry of `RAW_CAPTURE_READERS`, and amendment 60.

---

## 9. What becomes its own lane outside S1

| Lane | What it closes | Why it is not in S1 |
|---|---|---|
| **BFGS-ENVELOPE-REASON-01** | `analyze_envelope_gate` reports a battery refusal under the reason code `suite_manifest_missing` (executed, Y7, Y11). The verdict should name the battery status. | The fix is in `joulewise/envelope_gate.py`: production code, outside S1's WRITE_SCOPE. No energy is released by the defect: the bundle is refused. A reader of the verdict is told the wrong reason. |
| **BFGS-RAWCAPTURE-01** | Every member of `RAW_CAPTURE_READERS` of kind `energy` that the seat returns because it has no gate. | Gating it is a change to production code. The lane is empty until the seat's step 5 reports; if the seat returns nothing, the lane closes unopened. |
| BFGS-MANIFEST-CUSTODY-01 | Carried from amendment 52 (g) of the earlier erratum. | Unchanged by this ruling. |

Not ruled here, as in the ruling under review: the seat's flag F2 (whether a comment fix is authorized in `tests/test_battery_float_consumers.py`).

---

## 10. Not executed

- No unit test of the repository was run. V1 and V2 of the seat's brief: NOT EXECUTED.
- The kinds of the 48 raw-capture functions: I sorted none. The refuter read 6 of its 28.
- `scripts/make_figures.py::realized_output_tokens`: read to line 300, not to its end.
- R60-2's mutation, and the counterfactuals of R57-9, R58-1, R58-3, R58-4, R58-5, R58-6, R58-7, R58-9, R59-2, R60-1, R60-4 and R60-5 were not run as mutations.
- The rules of §6 were run as my prototype (`rules60.py`), not as the repository's sweep. The repository's sweep at `cbfa9dc3` does not implement amendment 51 yet.
- A real charging **suite** bundle through `analyze_envelope_gate`: Y11 replaces the verdict; Y7 uses a stubbed suite manifest.
- Whether any file outside `joulewise/` and `scripts/` reads a bundle or the envelope verdict by code. `git grep` over the whole tracked tree found the verdict's marker only in three prose files under `docs/` and in one test.
- Why the sentinel was absent from the summed curve in Y10's computed-key case.
- The rows of the eight consumer modules, and the 80 swept functions the first judge did not read: not read by me either.
- The earlier erratum ruling outside its amendments 51 and 52.

---

## 11. Probes written in this session (`/tmp/cg_sw_erratum/`; SHA-256 prefix)

| File | Prefix | What it is |
|---|---|---|
| `scan123.py` | `6c799a5708619d3b` | Y8: references, cache occurrences, bindings, over the tree |
| `rules60.py` | `0d348f24bc957cff` | Y9: the prototype of rules 57 (b) 1, 57 (b) 4, 57 (d) 5 |
| `cases60.py`, `cases60b.py` | `f6c0ec12ea76dc62`, `6dc1c6afb1ca9467` | Y9: the mutation cases A1 to A6, R1 to R13, C1 to C11 |
| `behaviour.py` | `50bdfe4a0e43d212` | Y10 |
| `envelope_cf.py` | `01c18cb6aee85ba9` | Y11 |
| `envelope_custody.py` | `09082e4c6a356edb` | Y12 |
| `rawcap.py`, `rawcap2.py` | `f8d1885e66a8f164`, `ca7ae24099559e4f` | Y14; the 48 members are listed in `rawcap_union.json` beside them |
| `refuter/` | as the refuter records | copies of the refuter's probes, unchanged; I ran the originals in `/tmp/oc_sw92/` |

The first judge's probes were run from `/tmp/cg_sweep/`, unchanged. The files under `/tmp` are not durable. The amendment text and the rows are written so the seat can implement without them.

---

## 12. Plain summary for Ed (5 lines)

1. A second model (the "refuter") checked the last ruling on the "sweep", the test that lists every place in the code that reads a measured run's files without first running the battery check (a run whose battery was charging or discharging has untrustworthy energy). It found no place where an energy number reaches a paper result unchecked, and neither did I; its nine findings (RSW-1 to RSW-9) are ways a *future* change could add one while the test stays green.
2. I upheld all nine, and ran each: taking a reader method as a value and calling it under another name, filling the reader's internal store of parsed files by hand, and giving the check's name another meaning each returned the energy of a charging run with nothing reported. Each is now refused by a rule that passes on today's code, so closing them changes no existing code.
3. Two of the refuter's proposed fixes were themselves too weak, which I found by running them: its rule for the reader's internal store still allowed three ways of filling it, and its list of code that opens the power meter's raw output missed 20 of 48 functions, because it did not follow file names held in named constants. I wrote stricter text for both.
4. Seven entries of the sweep's exemption list were filed as "historical" (old runs that cannot be swapped for new ones), which is false for them; they are re-filed under reasons that are true, and each statement in those reasons now has a check of its own. Amendments 57 to 60 are this ruling's four numbered changes; all are in test files, none in measurement code.
5. Two items go outside the current work package (S1, the battery-check wiring): one command reports a battery refusal under the wrong reason label (it still refuses), and any function found reading the meter's raw output for energy with no battery check gets its own fix. I did not sort the 48 functions myself; the implementer does, and a second model checks each.
