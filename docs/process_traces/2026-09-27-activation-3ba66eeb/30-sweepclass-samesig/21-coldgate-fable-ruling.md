# Cold gate SWEEPCLASS-SAMESIG-01: ruling (Fable 5.1, cold judge) on the S1 read-site sweep after two same-signature rounds

Candidate: working tree `/Users/edr/code/JouleWise-wt-samesig-cg-3ba66eeb`, detached @ `315364b2` (S1 head; includes main `97082508`). Parent `cbfa9dc3` (S1 fix round 3, partial).
Charge: `30-sweepclass-samesig/20-coldgate-charge.md`. The file on disk and the blob committed at `6820fed0` both hash to SHA-256 prefix `fc481bc6a9f54024`.
Session: one session, no subagents. No repository file edited: `git status --short` in the working tree printed 0 lines after every probe. Scratch: `/tmp/cg_samesig/`. Session clock: 03:23 to 03:46 local (budget 50 minutes).

---

## 0. Contamination disclosure and protocol deviations

The charge told me not to read `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAUDE*.md`, `AGENTS.md`, the decision log (the D-161 entry excepted), or memory and skill files. I opened none of them. These exposures happened anyway:

1. **Placed in my context by the harness before the charge arrived:** the owner's global `CLAUDE.md` (a pointer to orchestration doctrine, and a writing standard), this working tree's `CLAUDE.md` (notes on the bridge to a second model), the memory index `MEMORY.md` (about 110 one-line summaries), and the names of the installed skills. One index line reads "next = harvest W1, SWEEPCLASS erratum-2 (B-1..B-5), S1 fix-3". I opened no file any line points to and invoked no skill. No line takes a position on B-3, B-4, the stop rule, or the redesign.
2. **The D-161 search** (`grep -n "D-161" docs/decision_log.md`) printed the D-161 table row and four other one-line fragments that mention D-161 (lines 6556, 6721, 10688, 10789). I read the table row. The fragments take no position on this lane.
3. **The rulings under review and I are the same model.** That is a shared-blind-spot risk. Three results below go against earlier text of that model or against the seats' consensus, and each was found by executing: the consensus B-4 edit does not do what it is proposed for (Z8); the consumers-form row that amendment 51 (g) 3 ruled fails its own assertion at this tree (Z9); the marker value that earlier B-3 probes planted in their test bundles is the same in both bundles, so it cannot show which bundle's values came back (Z6).
4. **One fact I used from a ruling outside the listed packet.** To read amendment 51 I opened the earlier erratum ruling (`…/20-bfgs-s1/80-coldgate-r2/30-erratum/21-coldgate-fable-erratum-ruling.md`, lines 222 to 446: amendments 49 to 51). It states that every bundle collected after the base is refused until S1 merges. I used that to weigh how much a merge blocker costs.

The writing standard in the global `CLAUDE.md` asks that every term be defined at first use. The charge asks the same of the summary. I followed it. It changes wording, not rulings.

**Protocol deviations, stated.**
- The protocol says no background tasks. One probe command (Z6's reader tests) ran longer than the harness's 120-second limit, and the harness moved it to the background by itself. I started nothing else in the background, waited for it, and used its output only after it had exited (exit code 0).
- I edited one of my own scratch files in place (`sed -i` on `/tmp/cg_samesig/cons.py`). No repository file.

**What I read.** The cold-gate charge; the consult charge; the three seat reports, in full; the Opus seat's probes `p1.py`, `p2.py`, `p4.py`; the round-2 erratum ruling, in full; the round-2 refuter, lines 100 to 288 (the end of Section A, and Section B in full); amendments 49 to 51 as stated in item 4. **Not read:** the round-1 ruling, charge and refuter (I used the round-2 erratum's restatement); the round-2 charge; the round-2 refuter's lines 1 to 99; the Opus seat's `p3.py` (copied, not opened, not run).

---

## 1. Terms used in this ruling

Each term is defined once and used in that sense only. Terms marked (R) are those of the earlier rulings, repeated so this file stands alone.

- **Bundle** (R). The directory one measured run leaves behind. It holds `metadata.json` (what ran, and two battery readings), `summary_metrics.json` (the reduced numbers, energy included), `power_trace.csv` (the power samples), and other files.
- **Charging bundle** (R). A bundle whose battery readings show current flowing into the battery during the run. Part of the energy the machine drew then did not pass through the meter's accounting, so the bundle's energy numbers cannot be trusted.
- **The gate** (R). The check that a bundle's battery readings pass. It has two forms. **Window form:** the function `authenticate_window_members(members)`, which takes a list of (label, bundle path) and returns all verdicts or raises. **Reader form:** the method `BundleReader.metadata()`, which returns the parsed `metadata.json` only if the bundle passes, and raises `BatteryStatusRefusal` otherwise.
- **The reader** (R). The class `BundleReader` in `joulewise/bundle_read.py`. One reader object reads one bundle, whose directory it keeps in its attribute `_path`.
- **Gated energy accessors** (R). The four reader methods `trace_rows`, `summed_curve`, `source_curve`, `measured_window`. Each calls `self.metadata()` first.
- **Tolerant accessors** (R). The four reader methods `raw_metadata`, `raw_config`, `raw_summary`, `raw_artifact_bytes`. Each returns a file's content **without** the battery check, so that a refused bundle can still be inspected.
- **The sweep** (R). The test `tests/test_bfgs_consumer_sweep.py`. It parses every tracked Python file under `joulewise/` and `scripts/` and lists every **read site**: a place that calls a tolerant accessor, or reads one of the three **watched files** (`summary_metrics.json`, `metadata.json`, `power_trace.csv`), with no gate call before it. Each listed place is a **row**, and must have an entry in the test's **allowlist** with a **class** (a named reason category whose condition the row must meet).
- **The round-2 detector.** The sweep as it stands in the tree at `315364b2`, written in S1 round 2. It treats a whole function as gated if a gate call appears **anywhere** in it. Amendment 51 replaces it; that replacement is not implemented yet.
- **Dominates** (R). Said of a gate call and a later statement: execution cannot reach the statement unless the gate call ran and returned normally.
- **Scope.** A region of a Python file whose statements run together: the body of a function, the body of a class, the body of a `lambda`, or the top level of the file (the **module body**, which runs when the file is imported or run as a script).
- **Call, callee, reference** (R). In `r.raw_summary()` the whole expression is a **call** and `r.raw_summary` is its **callee**. "The callee `_manifest_record`" means the function that a call names. A **reference** is a function's or method's name used where it is *not* being called: `get = r.raw_summary` takes the method without calling it.
- **Energy-class value** (R). An energy, power, current, charge or voltage value, or a value computed from one.
- **Stage journal** (R). The bundle's file `events.jsonl`: one line per stage of the run. One of its events holds a measured idle power. The **journal readers** are the functions that read it and name an energy-class key.
- **Raw capture** (R). The power meter's own output, stored in the bundle as the meter wrote it (`raw/powermetrics*.plist`, `raw/nvidia_smi*.csv`). Every energy number in a bundle is computed from it. The **raw-capture readers** are the functions that name one of those files.
- **Window.** A span of time, scheduled in advance, in which a set of runs is measured on a quiet machine. A window's **members** are the bundles of those runs.
- **Consumer** (R). One of the eight modules that turn bundles into claimed numbers (listed in §10).
- **Claim artifact** (R). A file a paper number is taken from or licensed by.
- **Base.** The commit S1 branched from, `1417c0c4`.
- **Frozen files** (R). Files the ruled texts require to stay byte-identical to base: `joulewise/battery_float.py`, and the files on the excluded list of the ruled text called FT §E (among them `joulewise/reduce.py` and `joulewise/bundle.py`).
- **V1, V2, the builder's forward check.** The three verification runs that the fix-round-3 brief names and defines: two test-suite runs and one check of a generated artifact. I did not read the brief; I carry the names from the round-2 erratum's §8.
- **WRITE_SCOPE.** The closed list of files a seat may edit in one round.
- **Counterfactual** (R). For a test row: the specific wrong implementation under which the row must fail. A row **goes RED** when it fails and is **GREEN** when it passes.
- **Latent form.** A way of writing an ungated energy read that nobody has written in the tree, and that the sweep would not report if somebody did.
- **The seat.** The model session that implements fix round 3. **The refuter.** A model other than this judge that checks the seat's result. **The lead.** The session that commits the seat's work and runs the merge.
- **Same signature.** Two review rounds in a row that fail for the same kind of reason. The project's rule 11 then requires a consult before any further round.

---

## 2. Executed evidence (this session, working tree `315364b2`, Python 3.14.7, `PYTHONDONTWRITEBYTECODE=1`)

"The prototype" is the first judge's detector for amendment 51, `/tmp/cg_sw_erratum/sweep59.py` (SHA-256 prefix `c7ef17cab8b81b3b`, the value the round-2 erratum records), run unchanged unless a row says otherwise. "In memory" means: the module's source is read from the tree, edited as a string, and executed under the module's name for that process only. No file is written.

| Id | Probe | Result (exact) |
|---|---|---|
| Z1 | `python3 -B -m unittest tests.test_bfgs_consumer_sweep` | `Ran 3 tests`, `FAILED (failures=1)`. In the detector's output and not in the allowlist: `('scripts/run_campaign.py', 'evaluate_member', 'direct:read_text')`. In the allowlist and not in the output: `('scripts/run_campaign.py', 'run_axi_spec_campaign', 'direct:read_bytes')`. The seats' report reproduces. |
| Z2 | `inv.py`: the round-2 detector on `scripts/run_campaign.py` at three commits | The same mismatch at `cbfa9dc3` and at `315364b2`; the file is identical at both (`git diff --stat` lists no change). At main `97082508` neither function holds a gate call and both reads are reported. At `315364b2`: `evaluate_member` (lines 2799 to 2913) holds **no** gate call; `run_axi_spec_campaign` (7305 to 8160) holds one, at `:7848`. `git diff 21213be7 cbfa9dc3` shows fix round 3 removed the gate call from `evaluate_member` and added the one at `:7848`. |
| Z3 | `det.py`: the prototype over the tree | `126` sites, `120` distinct rows: the counts the round-2 erratum records for `cbfa9dc3`. For `scripts/run_campaign.py` it reports 10 rows, among them `evaluate_member` three times (`direct:summary_status` and `direct:read_text` on `summary_metrics.json`, `direct:read_text` on `metadata.json`) and `run_axi_spec_campaign`, `direct:read_bytes`, `metadata.json`, line 7686. |
| Z4 | The Opus seat's `p1.py`, re-run: the repository's detector on seven sources | `V7 lambda`, `V8 def under if`, `V8b def under try`, `V9 __main__`, `V9b main open`, `B5 map`: each `SILENT`. `control def`: reported. Tree counts: 209 files, 103 `__main__` blocks, 51 compound statements that hold a nested `def`, 274 lambdas, 9 `map(<named function>, …)`, 1 `partial`. Reproduces. |
| Z5 | The Opus seat's `p4.py`, re-run; and **mine**, `scopes.py`: the prototype with its scope walk replaced by one that visits every scope | `watched call sites: 100 in unvisited scopes: 0`. Prototype: rows `120` as ruled, `120` with every scope, added `[]`, lost `[]`; read sites inside lambdas on the tree: `[]`. The five forms: each `SILENT` as ruled and reported with every scope (`f`, `<module>`, `K.<body>`). |
| Z6 | **Mine.** `b3b.py`: reader `r` over a passing bundle A (its files carry `4242.4242`), gate passed, then re-pointed at a charging bundle B (its files carry `7777.7777`). Then the same with the reader's directory held behind a read-only property, in memory. Then `tests.test_bundle_read` under that edit | **Tree:** `r._path = B` then `trace_rows()`: `RETURNED values of B(CHARGING)`; then `raw_summary()`: the same; `r.__dict__['_path'] = B`: the same. **Read-only property:** `r._path = B`: `raised AttributeError`; `setattr(r, '_path', B)`: the same (`b3.py`); `r.__dict__['_path'] = B`: `RETURNED values of A(passing)` (the write has no effect); `r._BundleReader__root = B`: `RETURNED values of B(CHARGING)`. Reader tests under the edit: `ran 118 failures 0 errors 0`; on the tree: `Ran 118 tests in 167.082s`, `OK`. The test module was bound to the edited class (checked: `patched class: True`). **The earlier probes' sentinel is in both bundles** (the fixture builder writes `4242.4242` whether or not the bundle is charging), so "sentinel present" did not show whose values came back. With two values it does. |
| Z7 | **Mine.** `b4.py`, `b4_same.py`: the envelope gate with a gated helper (amendment 63's edit), in memory, against the tree, on one bundle from `EnvelopeGateTests.make_bundle()`; then `tests.test_envelope_gate` | Same bundle, tree output against edited output: `8237ee4d02d8ab97` and `8237ee4d02d8ab97`, `EQUAL`. Envelope tests: `Ran 27 tests`, `OK` on the tree; `ran 27 failures 0 errors 0` under the edit. With the gate's verdict replaced by `battery_float_confounded`: both give `verdict=bundle_refused … energies_in_output=None`. **CF1**, the callee `_manifest_record` without its gate: tree `energies_in_output=5`; edited `RAISED BatteryStatusRefusal`. **CF2**, the helper without its gate, callee kept: `bundle_refused`, no energy. **CF3**, both removed: `energies_in_output=5`. |
| Z8 | **Mine.** `det.py`: the prototype on three sources of `joulewise/envelope_gate.py` | Tree: `raw_summary` reported at `analyze_envelope_gate:133` and `_level_window_energy_records:654`. **The consensus edit** (`reader.metadata()` written before each `reader.raw_summary()`): **both still reported** (`:133`, `:655`). The gated helper: neither reported. The helper without its gate call: reported at `_gated_summary`. |
| Z9 | **Mine.** `dom.py`, `cons.py`: for the consumers-form row of `evaluate_member`, does a gate call dominate each consuming call? By the prototype's own dominance function, then with rule (d) 6 of amendment 64 | `run_campaign:9033 classify_campaign_members`, gate at `:9032`: `DOMINATED` under both. `run_axi_spec_campaign:8047 _idle_admission_core_evaluation` and `:8115 classify_campaign_members`, gate at `:7848`: **`NOT dominated` as ruled**, `DOMINATED` with (d) 6. The gate is inside `if policy_binding is not None:` at `:7837`; the consuming calls are inside **another** `if policy_binding is not None:` at `:8018`. Counterfactuals, with (d) 6: gate call removed; the name rebound between the two; the gate's test widened by `and`; the gate moved to the `else` of `is None`: each `NOT dominated`. |
| Z10 | **Mine.** AST scan of `run_axi_spec_campaign` | `policy_binding` is a parameter; stores or deletions of the name: `[]`; `global`/`nonlocal`: `[]`; nested definitions: `[]`. Between `:7686` and `:7835` the name `metadata` is used at `:7686` to `:7691` only, and the one field taken is `batch.admitted_request_count`. |
| Z11 | **Mine.** Over the 209 tracked files: uses, other than as the callee of a call, of ten helper names (`evaluate_member`, `evaluate_members`, `extract_rows`, `derive_idle_mean_uncertainty`, `_read_summary`, `realized_output_tokens`, `_level_window_energy_records`, `_manifest_record`, `_idle_admission_core_evaluation`, `classify_campaign_members`) | `non-callee references: []`. Calls of `evaluate_member`: 6, all in `evaluate_members`, `run_campaign`, `run_axi_spec_campaign`. |
| Z12 | **Mine.** The second judge's `rawcap2.py`, run with the ruled pattern and with the refuter's wider pattern (B-6) | Both: `union: 48`, added `[]`, lost `[]`. Named constants that hold a capture file name: 13 under the ruled pattern, 14 under the wider one. |
| Z13 | `shasum joulewise/battery_float.py`; `git diff --quiet` of it against `1417c0c4` and against `97082508`; the same for `reduce.py` and `bundle.py` against `97082508`; an import search over the eight consumers | prefix `4b4d7bb20625`; identical in every comparison; 0 lines that import `battery_float` in each of the eight. |
| Z14 | `grep -n "def summary" joulewise/bundle_read.py`; `grep -rn "\.raw_summary()"` over `joulewise/` and `scripts/` | No `summary` method exists on the reader. 18 lines in 13 Python files call `raw_summary()`. The Opus seat's finding reproduces (it counted 17). |
| Z15 | `grep -n "D-161" docs/decision_log.md` | The entry: an adversary inside the process is out of the threat model; the paper states one trusted operator; refusals whose only defended-against actor is that operator are over-engineering; fail-closed stays where the failure is physics, evidence or pre-registration. |
| Z16 | Read of `tests/test_bundle_read.py:558-589`, the repository's pin of protected paths against base `1417c0c4` | 15 path entries: `reduce.py`, `bundle.py`, `battery_float.py`, `powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, three scripts, four configuration entries, three test files. `joulewise/envelope_gate.py` and `joulewise/bundle_read.py` are not listed. |

**Limits of the probes, stated so they are plain.**
- Z3, Z5, Z8 and Z9 run a prototype, not the repository's sweep. The repository's sweep does not implement amendment 51 yet. The seat implements from the amendment text.
- Z6's and Z7's edits were made in memory. The files the seat will write do not exist yet.
- Z7 replaces the gate's verdict and not the bundle's battery readings: the test builder's bundle is a simulated run. It shows which calls stand between a refused bundle and the output.
- Z9's rule (d) 6 is 25 lines of mine. Its four counterfactuals are the ones I thought of.

---

## 3. Rulings at a glance

| Question | Ruling |
|---|---|
| Q1. Is an exhaustive static guarantee closable? | **No. Consensus ADOPTED.** Same signature. The promise is narrowed (amendment 61 (a)). |
| Q2. Who writes the evasive forms? | **Consensus ADOPTED, with a mechanical boundary** (amendment 61 (b), from the Opus seat's four clauses, one clause narrowed). |
| B-1, unvisited scopes | **CLOSE** (amendment 62 (a)). |
| B-2, the gate's behaviour replaced | **LIMITATION** in 51 (h). No rule. |
| B-3, the reader re-pointed | **LIMITATION** in 51 (h) for S1. No static rule. **A production change is ruled**, in its own lane after S1's merge: a read-only reader directory (lane BFGS-READER-ROOT-01). |
| B-4, the envelope rows | **A production change is ruled, inside S1 fix round 3**: a gated helper in `joulewise/envelope_gate.py` (amendment 63). The consensus edit as written is REJECTED: it does not remove the rows (Z8). The reclassification is REJECTED. |
| B-5, references in caller checks | **CLOSE** (amendment 62 (b)). |
| B-6, the capture pattern | **ADOPT** (amendment 65 (a)). Count stays 48 (Z12). |
| B-7, wording of the cache rule | **ADOPT the first half** (amendment 65 (b)); the second half is covered by 61 (b). |
| B-8, row R57-12 | **ADOPT** (amendment 65 (c)). |
| B-9, the envelope marker | **MOOT**: the rows that used it leave the allowlist. The marker check is withdrawn (amendment 63 (d)). |
| The inventory failure | **Not a key edit.** The round-2 detector is replaced, as already ruled. One new rule makes the ruled row checkable (amendment 64). |
| Stop rule | **One finite predicate, one refuter pass** (amendment 61 (c)). The number of latent forms never blocks S1's merge. |
| Gated `summary()` | **Its own lane**, BFGS-GATED-SUMMARY-01, after S1's merge. It blocks nothing. |

---

## 4. Q1 and Q2: why the promise is narrowed, and where the line is

### 4.1 The forcing problem

The round-2 erratum stated the sweep's standard in its §4: a GREEN sweep is read by everyone as "no ungated energy read exists", so any way a later change could add one silently is a defect. Python does not allow a test that reads source text to meet that standard. Code can reach any object through a name that is computed while the program runs, or through the interpreter's own tables: `getattr` with a built string, `exec`, `importlib`, `sys.modules`, `__dict__`. A rule that matches syntax is complete for a list of forms and for nothing beyond the list.

### 4.2 Worked example: the chain of three rounds

Each round closed a form, and the next refuter found its neighbour:

| Closed in round 1 or 2 | Found by the next refuter | Already visible beyond it |
|---|---|---|
| a method taken as a value (`get = r.raw_summary`) | a helper handed to `map` (B-5) | `functools.partial` |
| the gate's **name** rebound | the gate's **behaviour** replaced (B-2) | `importlib.import_module(…).authenticate_bundle = f` |
| a write into the reader's `_cache` | a write to the reader's `_path` (B-3) | `r.__dict__['_path'] = b` (executed, Z6) |

The count of SHOULD-FIX findings went 5, then 5. It does not shrink because the search space does not.

### 4.3 The line between an accident and an evasion

The science risk is an **accident**: somebody, a person or a model, writes ordinary code to read a number and does not know the gate exists. The most natural such code in this repository is one line at the bottom of a script (Z4: the tree has 103 such blocks, and the detector sees none of them):

```python
if __name__ == "__main__":
    print(BundleReader(sys.argv[1]).raw_summary()["gross_energy_j"])
```

An **evasion** is code that must reach into the gate's own machinery to work. Nobody replaces `battery_float.authenticate_bundle` while trying to read a number. D-161 (Z15) puts that actor outside the threat model.

The Opus seat proposed a four-clause test that sorts a form by its source text. I adopt it with one change: a **file name** built at run time is not evasion. `for name in ("summary_metrics", "metadata"): (b / f"{name}.json").read_text()` is ordinary code. It stays a stated blind spot (51 (h) already lists it), and is not placed in the deliberate class.

### 4.4 The three zones

```
        every way code can reach a bundle's energy values
 +---------------------------------------------------------------+
 | [Z-S]  SUPPORTED FORMS                                        |
 |        the sweep reports each one, in every scope             |
 +---------------------------------------------------------------+
 | [Z-B]  BLIND SPOTS                                            |
 |        ordinary code the sweep cannot see; listed in 51 (h)   |
 +---------------------------------------------------------------+
 | [Z-D]  DELIBERATE CLASS                                       |
 |        code that reaches into the gate's machinery; 61 (b)    |
 +---------------------------------------------------------------+
        [G-rt] the gated accessors refuse at run time in all
               three zones, unless the form replaces the gate
```

- **[Z-S]** is what amendment 61 (a) promises about. After this ruling it includes every scope (B-1) and references to helpers (B-5).
- **[Z-B]** is the list in amendment 51 (h). A form there can be an accident. The sweep says nothing about it, and says so.
- **[Z-D]** is defined by amendment 61 (b). A form there is never a finding against the sweep.
- **[G-rt]** is the run-time gate: `BundleReader.metadata()` inside the four gated energy accessors, and `authenticate_window_members`. It does not depend on the sweep. It is why a missed form in [Z-S] or [Z-B] is a risk only for reads through a tolerant accessor or a file path, which is where the sweep looks.

---

## 5. Amendments 61 to 65 (exact text; the fix-round brief quotes these)

All amend amendment 51 of the BFGS-S1-R2-01 erratum as amended by amendments 57 to 60 of the round-2 erratum (its §6). Text not changed here stands as ruled there. Rows that "call the sweep's check" do so on the tracked source with one replacement made in memory.

### Amendment 61 (new 51 (0); amends 51 (h))

61. **What a GREEN sweep promises, what it does not, and when its review ends.**

**(a) The promise.** Amendment 51 gains, before (a), this item:

> **51 (0). What a GREEN sweep means.**
> **Promised,** at the commit the sweep runs on, for every tracked Python file under `joulewise/` and `scripts/`:
> 1. Every read site written in a supported form (51 (b), as extended by 57 (d) 5), in any scope (51 (b) 0), is either gated in its own scope by a gate call that dominates it (51 (c), (d)), or has an allowlist row.
> 2. Every allowlist row carries a class whose condition holds. The sweep checks the condition where the class table gives it a check. The refuter checks it by reading otherwise.
> 3. Five closed lists equal the tree: the gate bodies (57 (b) 6), the tolerant definitions (57 (d)), the reader's public methods (58 (b)), the journal readers (58 (e)), the raw-capture readers (58 (f)).
>
> **Assumed.** The code was written to do its job. Its author, a person or a model, was not trying to get past the battery check. (D-161: one trusted operator; an adversary inside the process is outside the threat model.)
>
> **Not promised.**
> 1. That no Python program can read energy from a refused bundle.
> 2. Anything about a form in the deliberate class (61 (b)).
> 3. Anything about a blind spot listed in 51 (h).
> 4. Anything about code outside `joulewise/` and `scripts/`: the tests, a notebook, a shell command.
> 5. That a bundle's bytes are the bytes that were measured. That is custody's duty, not the sweep's.
>
> A GREEN sweep is therefore read as: "no ordinary code in the tree reads energy past the gate without a checked reason". It is not read as: "no ungated read can exist".

**(b) The deliberate class.** A latent form is in the deliberate class if its source, between the scope it starts in and the read it reaches, does at least one of:

1. reads or writes an attribute whose name begins with `_`, on an object whose class or module is defined under `joulewise/`, from outside the module that defines it (`r._path = b`; `r._cache.update(…)`);
2. assigns to, or deletes, an attribute of a module, class or function defined under `joulewise/` (`battery_float.authenticate_bundle = f`; `BundleReader.metadata = f`);
3. calls `setattr`, `delattr`, `object.__setattr__`, `vars`, `exec`, `eval`, `compile`, `__import__`, `importlib.import_module`, or `type` with three arguments; or names `__dict__`, `__code__`, `__class__` or `sys.modules`;
4. builds the name of a tolerant accessor or of a gate while the program runs (`getattr(r, "raw_" + "summary")`).

A form in the class is **never a finding against the sweep**. It is added to 51 (h) by name if it is not there. A watched **file** name built at run time is not in the class; it is a blind spot (51 (h), "a read that never names the file").

Rules already ruled that guard forms of the class stay as ruled: 57 (b) 1 (iii) and 57 (b) 4. They are written, GREEN on the tree, and cost the seat one check each. **No new rule is added for the class, by this ruling or by any later review of this lane.**

**(c) The stop rule.** The review of the sweep ends when all five hold at one commit, the **merge candidate**, each shown by execution:

- **A1, the matrix.** Every test row named in §8 is GREEN on the tree, and RED under its counterfactual with the counterfactual applied in memory and run by the seat. The lead re-runs the rows that are new in this ruling: R51-23 to R51-28, R59-3b, R60-2b, R60-6.
- **A2, the inventory.** The reported keys equal the allowlist's keys, and the count is stated. One refuter has checked every allowlist row against its class condition, every entry of `READER_METHODS` and every entry of `RAW_CAPTURE_READERS` against its kind, and found none false.
- **A3, the tree.** The same refuter pass finds no energy-class value that reaches a claim artifact without a gate, on the routes through the eight consumers and through the envelope gate.
- **A4, the suites.** V1 and V2 of the fix-round brief are GREEN, and the builder's forward check passes.
- **A5, the fences.** `joulewise/battery_float.py` hashes to prefix `4b4d7bb20625`; it, `reduce.py` and `bundle.py` are byte-identical to base; none of the eight consumers imports `battery_float`.

**There is one refuter pass.** What its findings do:

| The refuter finds | What happens | Another refuter pass? |
|---|---|---|
| a failure of A1 to A5: a false class, a wrong kind, an ungated read in the tree, a row that does not go RED | the seat fixes it; the lead re-runs the affected rows | no, unless the fix changes production code other than as ruled in §5 |
| a latent form in the deliberate class | it is named in 51 (h) | no. It is not a finding. |
| a latent form in a 51 (h) blind spot | nothing | no. It is not a finding. |
| a latent form in a supported form that the sweep misses | the seat closes it if the closure is GREEN on the tree; the lead re-runs the new row | no |
| three or more of the last kind in the one pass | rule 11 applies: the forms are named in 51 (h), **S1 merges**, and the next spend is lane BFGS-GATED-SUMMARY-01 | no |

**The number of latent forms never blocks S1's merge.** A1 to A5 do.

**(d) 51 (h) gains these items** (the "limitation" wording for B-2 and B-3):

- "**The gate's behaviour replaced while its name stays.** An assignment to `battery_float.authenticate_bundle`, or to `authenticate_window_members` through the module written in full, a `setattr` on either module, or a subclass of `BundleReader` built by a call of `type`, makes a reader admit a refused bundle (executed by the round-2 refuter, its F2). Deliberate class, clauses 2 and 3. Not swept."
- "**A reader pointed at another bundle.** `r._path = other`, after `r.metadata()` passed on the first bundle, makes every accessor return the other bundle's values (executed, SAMESIG Z6). Deliberate class, clause 1. Not swept. Lane BFGS-READER-ROOT-01 makes the assignment raise."
- "**The same through the interpreter's tables:** `importlib.import_module(…)`, `sys.modules[…]`, a module bound to another name first, `__code__`, `vars(…)`, `__dict__` (the Opus seat's P3). Deliberate class, clause 3. Not swept."

And the item of 60 (d) "A gate in a callee" is replaced by: "**A gate in a callee.** A gate call inside a function that the row's function calls is not seen. At the merge candidate no read is known to rely on one: the envelope gate's two reads relied on one until amendment 63."

### Amendment 62 (new 51 (b) 0; amends 51 (f), 59 (b), 60 (c) 2, 57 (d) 5, 58 (f) 3)

62. **Every scope is swept, and a caller check counts references.**

**(a) B-1. Amendment 51 (b) gains, before item 1:**

> **0. Scopes.** The sweep inventories every scope of a tracked file:
> - each `def` and `async def` wherever it is nested. Its qualified name is the enclosing qualified name, then `.`, then its name. A `def` nested under an `if`, `try`, `with`, `for` or `while` is qualified exactly as one in the body;
> - the module body, with the qualified name `<module>`;
> - each class body, with the qualified name `<Class>.<body>`;
> - each `lambda`. Its body is swept as part of the scope that holds it, and a read site inside a `lambda` is **never gated**, because the `lambda` runs at a time the enclosing gate call does not govern.
>
> Parameter defaults and decorators belong to the enclosing scope. No scope inherits a gate from another.

In 57 (d) 5 and 58 (f) 3, "function" reads "scope".

**(b) B-5.** In the callers form of `behind_gate` (51 (f) as amended by 59 (b)), and in 60 (c) 2, "every call of the function's name" is replaced by: "every call of the function's name, and every **reference** to it (a plain name or an attribute of that name, used where it is not the callee of a call, other than its own definition and its imports), by bare name or as an attribute". A reference counts as a call made from the scope that holds it.

**Test rows for amendment 62.** Each source is given to the sweep as file `scripts/zz_new.py`.

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R51-23 | every tolerant accessor call in the tree (100 watched call sites, Z5) | `g = lambda r: r.raw_summary()` | reported in `<module>`, operation `raw_summary` | the round-2 detector, and the prototype as ruled: silent (executed, Z4, Z5) |
| R51-24 | the same | `if os.environ.get("X"):` then, inside it, `def f(r): return r.raw_summary()`; and the same `def` inside the handler of a `try` | each reported in `f` | the same (Z4, Z5) |
| R51-25 | the same | `if __name__ == "__main__": print(BundleReader(sys.argv[1]).raw_summary()["gross_energy_j"])` | reported in `<module>` | the same (Z4, Z5) |
| R51-26 | every path read in the tree | `class K:` with the body `DATA = open("b/summary_metrics.json").read()`; and the same `open` under `if __name__ == "__main__":` | reported in `K.<body>`; reported in `<module>` | the same (Z4, Z5) |
| R51-27 | the tree | the tree | the reported keys equal the allowlist; scope coverage adds **0** rows (executed on the prototype, Z5) | a scope walk that reports a module-level assignment of a path to a name as a read |
| R59-3b | `idle_dependence.derive_idle_mean_uncertainty`, called at `reduce.py:3302` and `:3563` | a file `joulewise/zz_new.py` with `f = derive_idle_mean_uncertainty` in a function the row's `callers` does not list | the sweep fails, naming that function | the callers form as ruled, which counts calls only. NOT EXECUTED as a mutation; the tree holds no such reference (Z11). |
| R60-2b | `make_figures.extract_rows` | `scripts/make_figures.py` with `rows = list(map(extract_rows, [runs_root]))` added to `main` | the sweep fails, naming `scripts/make_figures.py::main` | 60 (c) 2 as ruled. NOT EXECUTED as a mutation; the tree scan is executed (Z11). |

### Amendment 63 (B-4; replaces the first two rows of 60 (b); withdraws 60 (c) 1 and R60-1; restates R60-3). **This amendment changes production code.**

63. **The envelope gate's two summary reads are gated where they are made.**

**(a) The edit, exact.** In `joulewise/envelope_gate.py`, and nowhere else:

1. Immediately above `def _manifest_record`, add:
   ```python
   def _gated_summary(reader: BundleReader) -> dict[str, Any] | None:
       reader.metadata()
       return reader.raw_summary()
   ```
2. In `analyze_envelope_gate`, in the list that builds `summary_missing` (line 133 at `315364b2`), `reader.raw_summary()` becomes `_gated_summary(reader)`.
3. In `_level_window_energy_records`, first statement of the loop (line 654), `reader.raw_summary()` becomes `_gated_summary(reader)`.

**(b) The lane and the order.** The edit is made **inside S1 fix round 3**, as its first step, before the detector's rows are computed. Fix round 3's WRITE_SCOPE gains `joulewise/envelope_gate.py`, **for these three changes only**. The reason code (`suite_manifest_missing` reported for a battery refusal) stays in lane BFGS-ENVELOPE-REASON-01 and is not touched here.

**(c) The rows.** The two rows of 60 (b) for `joulewise/envelope_gate.py` are withdrawn. After the edit the sweep reports neither read (executed on the prototype, Z8): in `_gated_summary` the read's receiver is a parameter annotated `BundleReader`, and the gate call on the same name dominates it, which is the reader form of 51 (c) as ruled. **No rule of the detector changes for this.**

**(d) Withdrawn.** 60 (c) 1 (the `output_marker` check) and row R60-1: no row uses them after (c). B-9 is moot for the same reason.

**(e) Rows.**

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R60-3 (restated) | `envelope_gate._manifest_record` and `envelope_gate._gated_summary`, the two gates before the energy in the envelope verdict | a suite bundle from `EnvelopeGateTests.make_bundle()`; `BundleReader._battery_verdict` patched, for the test only, to return the real verdict with `status` replaced by `battery_float_confounded`; `analyze_envelope_gate([bundle], lambda path: [])` | `verdict == "bundle_refused"`, and the key `calibration_evidence_only` is absent | **both** gates removed (`_manifest_record` with `reader.metadata()` replaced by `reader.raw_metadata() or {}`, and `_gated_summary` without its first statement): the output holds 5 energy records (**executed RED, Z7 CF3**). With the callee's gate alone removed the call raises `BatteryStatusRefusal` and the row is RED by that exception (Z7 CF1). With the helper's gate alone removed the row stays GREEN (Z7 CF2); R60-6 is the row that goes RED then. |
| R60-4 | unchanged | as ruled | as ruled | as ruled |
| R60-6 | `envelope_gate._gated_summary` | (i) the tree; (ii) `_gated_summary` without its `reader.metadata()` statement | (i) the sweep reports no `raw_summary` site in `joulewise/envelope_gate.py`, and the allowlist holds no such row; (ii) the sweep fails, naming `_gated_summary` | a helper that is exempt by its name (**executed on the prototype, Z8**: reported at `_gated_summary`) |
| R60-7 | `envelope_gate.analyze_envelope_gate` | the bundle of R60-3, unpatched; the function's output before the edit (from `git show 315364b2:joulewise/envelope_gate.py`, executed in the test) and after | the two outputs are equal | an edit that changes what the envelope gate returns (executed equal, Z7) |

R60-5 stands. The rows of 60 (b) for `scripts/make_figures.py` stand.

### Amendment 64 (the inventory; amends 51 (d) and restates 51 (g) 3)

64. **The consumers-form row of `evaluate_member` is made checkable, and the read in `run_axi_spec_campaign` is classed by what it reads.**

**(a) 51 (d) gains rule 6:**

> **6. Two `if` statements with the same test on an unchanged parameter are one branch.** For rule 1 only. Take an `if` statement whose test is exactly `<P> is not None`, where `<P>` is a plain name that is a parameter of the function and is bound by nothing else anywhere in the function: no assignment (plain, augmented or annotated), no `:=`, no target of `for`, `with`, `except … as`, a comprehension or `match`, no `del`, no import, no `global` or `nonlocal`, no nested `def` or `class` of that name. Entered through its body, such an `if` counts as the same enclosing branch as every other such `if` on the same `<P>` in that function. Any other test gets no such treatment: `<P> is not None and …`, `<P> is None` with the code in its `else`, a test on an attribute.

Why it is sound: a parameter that nothing rebinds names the same object for the whole call, so the test gives the same answer at both `if`s. If the second body runs, the first body ran.

**(b) 51 (g) 3 is replaced by:** "`scripts/run_campaign.py::evaluate_member` has three rows (`direct:summary_status` on `summary_metrics.json`; `direct:read_text` on `summary_metrics.json`; `direct:read_text` on `metadata.json`). Each carries `behind_gate`, consumers form, with `consumers = (("scripts/run_campaign.py::run_campaign", "classify_campaign_members"), ("scripts/run_campaign.py::run_axi_spec_campaign", "_idle_admission_core_evaluation"), ("scripts/run_campaign.py::run_axi_spec_campaign", "classify_campaign_members"))`."

**(c) The read at `run_axi_spec_campaign`, `metadata.json`, line 7686,** has the row `("scripts/run_campaign.py", "run_axi_spec_campaign", "direct:read_bytes", "metadata.json")`, class `non_claim`, clause (i), reason: "field read: `batch.admitted_request_count`, a count of requests, used for the dispatch receipt". The reason it carries at `315364b2` ("…before gated final analysis") is a statement about a gate in a reason field, which R58-5 forbids, and is removed.

**Test rows for amendment 64.**

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R51-17 (restated) | `run_campaign` (`run_campaign.py:9032-9033`); `run_axi_spec_campaign` (`:7848`, `:8047`, `:8115`) | the rows of (b) on the tree; then with the gate call at `:9032` deleted; then with the gate call at `:7848` deleted | passes; fails naming `run_campaign`; fails naming `run_axi_spec_campaign` | a consumers row that is not checked (executed on my prototype for `:7848`, Z9) |
| R51-28 | `run_axi_spec_campaign`, the two `if policy_binding is not None:` at `:7837` and `:8018` | four sources, each the tree with one change: (a) `policy_binding = policy_binding or _default_binding()` added between the two `if`s; (b) the first test widened to `policy_binding is not None and receipts`; (c) the gate moved to the `else` of `if policy_binding is None:`; (d) the tree unchanged | (a), (b), (c): the rows of 64 (b) fail; (d): they pass | rule (d) 1 as ruled, under which (d) fails (**executed, Z9**); a rule 6 that compares the tests' text and nothing else, under which (a) passes (**executed RED for all three, Z9**) |

### Amendment 65 (the small texts: B-6, B-7, B-8)

65. **(a)** In 58 (f) 2 the capture pattern becomes `^(raw/)?(powermetrics[A-Za-z0-9_]*\.plist|nvidia_smi[^ /]*\.csv)$`. It now matches `powermetrics_idle_post.plist`. At `315364b2` the member count stays 48, and the named constants that hold a capture name go from 13 to 14 (executed, Z12).
**(b)** In 57 (b) 4 (ii), "the assignment of an empty dictionary" becomes "the assignment or annotated assignment of an empty dictionary". The tree uses the annotated form (`bundle_read.py:420`), so the rule as written would fail on the tree.
**(c)** Row R57-12 gains: "If a production change makes this row RED by closing the hole, the row is replaced by its negation under a cold gate. The change is not reverted."

---

## 6. B-1 to B-9: dispositions

| Finding | Zone (§4.4) | Disposition | Text |
|---|---|---|---|
| B-1, scopes never visited | supported form | **CLOSE.** The plainest accident there is (Z4). Costs 0 rows (Z5). | 62 (a); R51-23 to R51-27 |
| B-2, the gate's behaviour replaced | deliberate, clauses 2 and 3 | **LIMITATION.** The refuter's replacement text for 57 (b) 1 (ii) and (iii) and its rows R57-11b and R57-12b are **not adopted**. | 61 (d), first item |
| B-3, the reader re-pointed | deliberate, clause 1 | **LIMITATION for S1.** The refuter's 57 (b) 4 (v) and row R57-6c are **not adopted**. Closed at run time in its own lane (§7.1). | 61 (d), second item |
| B-4, the envelope rows | not a latent form: a false class on today's tree | **PRODUCTION EDIT in fix round 3** (§7.2). | 63 |
| B-5, caller checks count calls only | supported form | **CLOSE.** `map(helper, …)` is ordinary Python; 9 such calls exist in the tree on other names (Z4), none on a guarded helper (Z11). | 62 (b); R59-3b, R60-2b |
| B-6, capture pattern | supported form, a screen by name | **ADOPT.** | 65 (a) |
| B-7, wording | | **ADOPT** the annotated-assignment wording. The proposed 51 (h) item ("`_cache` or `_path` named by a string built at run time") is covered by 61 (b) clause 1 and is not added separately. | 65 (b) |
| B-8, R57-12 pins a hole | | **ADOPT.** | 65 (c) |
| B-9, the marker is one string | | **MOOT.** | 63 (d) |

---

## 7. B-3 and B-4: the choices, with reasons

### 7.1 B-3. Limitation now; a read-only reader directory in its own lane, after S1 merges

**The forcing problem.** A reader remembers that its gate passed, in its cache. It does not remember **for which directory**. If the directory is changed afterwards, the reader answers for the new one under the old pass.

**Worked example (executed, Z6).** Bundle A passes and its files carry the value `4242.4242`. Bundle B is charging and its files carry `7777.7777`.

```python
r = BundleReader(A); r.metadata()     # the gate passes on A
r._path = Path(B)                     # the reader now points at B
r.trace_rows()                        # returns rows holding 7777.7777
```

**The three seats.** Sol: a static rule that forbids the assignment. Astra: make the directory read-only in the reader. Opus: a limitation, with an optional binding of the gate to the path.

**Ruling, and why.**
1. **No static rule.** A rule on the text `r._path = …` is the shape that produced this consult. Its neighbour is already known and executed: `r.__dict__['_path'] = B` returns B's values on the tree (Z6) and no rule on assignments sees it. By 61 (b) clause 1 the form is in the deliberate class: it writes a private attribute of a reader from outside the reader's module. The tree holds no such write (the round-2 refuter's F3).
2. **The run-time fix is ruled, in Astra's form, as lane BFGS-READER-ROOT-01.** In `joulewise/bundle_read.py`, `BundleReader.__init__` stores the directory in a name-mangled attribute (`self.__root = Path(path)`), and `_path` becomes a property with no setter that returns it. Executed in memory (Z6): the assignment and `setattr` raise `AttributeError`; the `__dict__` write has no effect and the reader still answers for A; all 118 reader tests pass. Every other line of the reader is unchanged, because each already reads `self._path`. **This is a production change.** It touches no frozen file and adds no import to any consumer.
3. **Order: after S1's merge. It does not block S1.** The tree has no instance, so no number is at risk today. S1's merge is what lets bundles collected since the base be consumed at all. A change to the reader deserves its own short review and should not ride inside a round that is already large.
4. **Not ruled:** the Opus seat's binding of the gate to the path and a token inside `metadata()`. It edits a gate body, which rules 57 (b) 3 and rows R57-2 to R57-6 pin. The property does the same job for B-3 without touching one.

What the property does not stop: a write to the mangled name (`r._BundleReader__root = B` returns B's values, Z6). That form names the class's private storage in full and is in the deliberate class.

### 7.2 B-4. A gated helper in `envelope_gate.py`, inside fix round 3

**The forcing problem.** The envelope gate is a command that checks a set of calibration bundles and writes a verdict. AP-5 is one of the project's registered analysis plans (`docs/contracts/analysis_plans.md`); as the round-2 refuter quotes it, it requires that verdict to pass before any scored campaign (a campaign whose answers are graded). So the verdict **licenses** numbers and is a claim artifact. It carries energy per level. The round-2 erratum filed the two reads that fetch that energy as `non_claim` (ii), whose condition is "nothing the function writes is consumed by a claim artifact". That condition is false. The energy is gated in fact, but only by a call inside another function, `_manifest_record`, which the sweep cannot see.

**The three seats.** Sol and Opus (and the round-2 refuter): write `reader.metadata()` before each `reader.raw_summary()`. Astra: leave the code, and file the rows under a new "gate in a callee" form of `behind_gate`, pinned by a behaviour test.

**What I executed, and what it changes.**
1. **The consensus edit does not remove the rows (Z8).** At both sites `reader` is a loop variable. Amendment 51 (c) accepts a reader-form gate only on a name bound from a call of `BundleReader`, on a parameter annotated `BundleReader`, or on `self`. With the two calls added, the prototype still reports both reads. The edit would need a new detector rule for loop variables as well: a wider rule about what counts as gated, in the direction that hides reads.
2. **A helper with an annotated parameter removes them with no detector change (Z8),** and gives byte-equal output on the same bundle and 27 of 27 envelope tests (Z7).

**Ruling, and why.** Amendment 63's helper.
- **Against the reclassification.** It needs a new class form and a new check in the sweep for "the callee holds a gate". That grows the recogniser, which this ruling freezes. And it leaves the energy read separated from its gate by a function boundary, so a later edit of `_manifest_record` can remove the gate without touching the read. Executed: on the tree, removing the callee's gate puts 5 energy records of a refused bundle into the verdict (Z7 CF1, tree).
- **For the helper.** The read and its gate become two adjacent lines. Executed: with the helper in place, removing the callee's gate releases **nothing**; the call raises `BatteryStatusRefusal` (Z7 CF1, edited). Astra's objection, that production calls should not be added only to satisfy a detector, is answered by that result: the edit changes what happens under a real future mistake.
- **On Astra's caveat** that behaviour identity depends on today's call graph: correct, and that is all that is claimed. On today's call graph every reader that reaches either site has passed `metadata()` in `_manifest_record`, which caches on success, so the helper's call returns the cached value.

**Kept intact by the edit.** A custody failure cannot newly arise at the helper on today's paths (the value is cached). If one ever did, it would leave `analyze_envelope_gate` as an exception: neither site is inside a handler that names it. Custody stays an exception.

---

## 8. The inventory failure, and fix round 3 restated

### 8.1 What the failure is

**The mechanism (executed, Z1, Z2).** The round-2 detector treats a function as wholly gated if a gate call appears anywhere in it. Fix round 3 made two ruled changes to `scripts/run_campaign.py` and did not touch the sweep, because amendment 51 was blocked:

1. It **removed** the gate call from `evaluate_member` (the gate moved to the functions that work out a window's membership, amendments 49 and 53). The function's reads of `summary_metrics.json` and `metadata.json` became visible: the **unlisted** key.
2. It **added** a gate call to `run_axi_spec_campaign` at `:7848`. The round-2 detector then called the whole function gated, and the read of `metadata.json` at `:7686`, which comes 162 lines **before** that gate call, vanished from its output: the **stale** key.

**Why the keys must not be edited to match.** Deleting the stale key would record that the read at `:7686` is gated. It is not: it runs before the gate, in a loop that collects bundles. Under amendment 51's detector it is reported (Z3). Adding the unlisted key under the old three-field form would give `evaluate_member` a class with no check behind it. Both keys are symptoms of the detector that amendment 51 already replaces.

**What the consumers form says, and what I found (Z9).** `evaluate_member` runs during collection, before any gate, and returns a record that holds the bundle's summary and metadata, energy included. Its reads are safe only if every function that later **uses** those records for a verdict is gated first. Amendment 51 (g) 3 ruled exactly that, as a checked row. At this tree the check **fails** for `run_axi_spec_campaign`: the gate call and the consuming call sit inside two separate `if policy_binding is not None:` statements, and rule (d) 1 requires one enclosing branch. The gate does dominate in fact: `policy_binding` is a parameter that nothing rebinds (Z10). Amendment 64 (a) states that fact as a rule, with four counterfactuals executed (Z9). Without it the seat would return the row for a ruling, and the lane would stall again.

### 8.2 Fix round 3, in order

One seat. Working tree from `315364b2`. WRITE_SCOPE: that of fix round 3, plus `joulewise/envelope_gate.py` for amendment 63 (a) only. Authority: amendment 51 (earlier erratum, §10), as amended by 57 to 60 (round-2 erratum, §6), as amended by 61 to 65 (§5 above). Where two texts differ, the later one holds.

| Step | What | Rows to show RED under the counterfactual, then GREEN |
|---|---|---|
| 1 | **The envelope edit**, amendment 63 (a), three changes. | R60-3 (restated), R60-4, R60-7; `tests.test_envelope_gate` 27 of 27 |
| 2 | **The detector.** Replace the round-2 detector by amendment 51 (a) to (e), with: scopes (62 (a)); 59 (a) in rule (d) 2; rule (d) 6 (64 (a)); the window form of 51 (c) narrowed (57 (b) 1); the `ref:` read site (57 (d) 5). The allowlist key becomes (path, qualified scope, operation, watched file). | R51-1 to R51-13, R51-18 to R51-22, R51-23 to R51-26, R59-1, R59-2, R59-4, R59-5, R57-10 |
| 3 | **The count.** Report rows, scopes and source lines. By the prototype: 126 sites and 120 rows at `315364b2` (Z3); **118 rows after step 1** (the two envelope rows leave, Z8); 0 rows added by scope coverage (Z5); 0 `ref:` rows. A different count is returned with the differing rows listed. | R51-27 |
| 4 | **The two closed classes.** 57 (b) and (d) as they stand, with 65 (b). Three `gate_body` rows, two `tolerant_definition` rows. | R57-1 to R57-12, R57-6b included; R57-12 with 65 (c) |
| 5 | **The reader pins.** 58 (b) with the kind `journal`; 58 (c); 58 (e). | R58-1 to R58-6b, R58-9 |
| 6 | **The raw-capture inventory.** 58 (f) with the pattern of 65 (a). 48 members by the prototype (Z12). Every member gets a kind by reading the function. A member of kind `energy` with no gate is returned to the lead and is a tree finding (it fails A3). | R58-7, R58-8 |
| 7 | **The chains and the caller checks.** 59 (b) and (c); 62 (b). | R59-3, R59-3b, R51-16, R60-2, R60-2b |
| 8 | **`scripts/run_campaign.py`.** The three `evaluate_member` rows of 64 (b). The `run_axi_spec_campaign` row of 64 (c). The file's other rows by step 9. | R51-17 (restated), R51-28 |
| 9 | **The allowlist, all rows,** each with class and reason, in the report. Apply 51 (g) 1, 2, 5 and 6; 64 (b) in place of (g) 3; 60 (a) in place of (g) 4; 58 (d); the `make_figures.py` rows of 60 (b); 60 (c) 2; 60 (e). No row for `raw_summary` in `joulewise/envelope_gate.py`. For every `non_claim` row: clause (i) with the fields read, or clause (ii) with what is written and to whom it is returned. | R51-14, R51-15, R58-5, R60-5, R60-6 |
| 10 | **51 (0) and 51 (h).** The promise of 61 (a) and the deliberate class of 61 (b) go into the sweep's module docstring, word for word. The items of 61 (d) go into the list the test holds for 51 (h). | none: text |
| 11 | **Returns.** A row or a raw-capture member that fits no class is returned to the lead with the scope, what it returns, and its callers. The seat invents no class and no kind, and edits no frozen file. | |
| 12 | **The suites and the fences.** V1, V2 and the builder's forward check as the fix-round-3 brief states them; the three fences of A5. | |

**Does not block S1's merge:** B-2, B-3 and every other form in the deliberate class; lane BFGS-READER-ROOT-01; lane BFGS-GATED-SUMMARY-01; the envelope reason code; lane BFGS-MANIFEST-CUSTODY-01.
**Does block S1's merge:** the red sweep (Z1) until steps 1 to 9 are GREEN; a false class; a raw-capture member of kind `energy` with no gate; any failure of A1 to A5.

**Then:** one refuter pass on the merge candidate, under the stop rule of 61 (c).

---

## 9. The gated `summary()` redesign

**Ruling: its own lane, BFGS-GATED-SUMMARY-01. It opens after S1 merges. It blocks nothing.**

**The root cause is real (Z14).** The reader has four gated accessors for the power trace and none for `summary_metrics.json`, the file that holds `gross_energy_j`. A correct claim read and an ungated read are therefore the same text, `reader.raw_summary()`, and whether one is safe depends on what was called earlier and elsewhere. That is why the sweep needs dominance rules, a reader-binding rule, caller chains and a consumers form, and why each round finds another way to separate a read from its gate. Amendment 63's helper is the same idea in one module.

**The lane's content, for whoever briefs it.**
1. Add `BundleReader.summary()`: its first statement is `self.metadata()`, then it returns what `raw_summary()` returns. Its kind in `READER_METHODS` is `gated_energy`; the public-method count goes from 30 to 31.
2. Move the claim consumers' reads onto it (18 lines in 13 files call `raw_summary()` today, Z14; the lane sorts which are claim reads).
3. Replace `envelope_gate._gated_summary` by it.
4. The allowlist for `raw_summary` then holds only callers that are not claim reads, and the dominance machinery for tolerant reads has nothing left to decide.

It adds a method to the reader, which the earlier rulings' text 8 ("the reader's behaviour does not change") did not foresee, so the lane needs its own cold gate. It touches no frozen file.

**When it moves up.** On the rule-11 event of 61 (c) (three or more missed supported forms in the one refuter pass), or when the first new claim consumer is written after S1, whichever comes first. Until then it ranks below anything on the path to measurement windows.

---

## 10. Kept intact

- **Custody is never a status.** No amendment here adds a status, a handler or a conversion. Amendment 63's helper sits inside no handler that names a custody failure. R57-9 and R60-4 stand.
- **Authentication precedes every exclusion decision.** No amendment here reorders production code. Amendment 63 adds a gate call that returns a cached value. Amendment 64 changes the test's rule (d) and a row's class, and no line of `scripts/run_campaign.py`.
- **`joulewise/battery_float.py` and FT §E's excluded list are byte-identical.** SHA-256 prefix `4b4d7bb20625`; identical to base `1417c0c4` and to main `97082508`; `reduce.py` and `bundle.py` identical to main (Z13). Amendments 61 to 65 edit none of them. Neither file that this ruling changes is protected: the repository's own pin test (`tests/test_bundle_read.py:558-589`, `test_historical_set_bytes_and_protected_base_paths_are_pinned`, which compares a list of protected paths against base `1417c0c4`) lists 15 path entries, and `joulewise/envelope_gate.py` and `joulewise/bundle_read.py` are not among them (read, Z16; the test passed in Z6's run). I did not open the text FT §E itself. If the lead finds either file on that text's list, the change to it is returned to a cold gate and is not made.
- **The eight consumers do not import `battery_float`** (Z13): `scripts/run_campaign.py`, `joulewise/whole_window.py`, `joulewise/analysis_engine/inputs.py`, `joulewise/floor_extraction.py`, `joulewise/aggregate.py`, `joulewise/window_duration_margins.py`, `scripts/mint_floor_artifact.py`, `scripts/extract_detection_floors.py`. `envelope_gate.py` is not one of the eight and gains no import.

**Production changes ruled here, all of them:** (1) amendment 63 (a), three changes in `joulewise/envelope_gate.py`, inside S1 fix round 3; (2) the read-only reader directory in `joulewise/bundle_read.py`, lane BFGS-READER-ROOT-01, after S1's merge. Nothing else.

---

## 11. Lanes outside S1

| Lane | What it does | Order | Blocks S1? |
|---|---|---|---|
| **BFGS-READER-ROOT-01** (new) | the reader's directory becomes read-only (§7.1) | after S1's merge | no |
| **BFGS-GATED-SUMMARY-01** (new) | a gated `summary()` accessor; claim consumers moved onto it (§9) | after S1's merge; moves up on the rule-11 event | no |
| BFGS-ENVELOPE-REASON-01 | the envelope gate names the battery status in its refusal | unchanged. It no longer carries the B-4 edit. | no |
| BFGS-RAWCAPTURE-01 | gates any raw-capture reader of kind `energy` that step 6 returns | opens only if step 6 returns one | the returned member does |
| BFGS-MANIFEST-CUSTODY-01 | carried | unchanged | no |

---

## 12. Not executed

- V1, V2 and the builder's forward check. Of the repository's tests I ran three modules: `tests.test_bfgs_consumer_sweep` (3 tests, 1 failure), `tests.test_envelope_gate` (27, OK), `tests.test_bundle_read` (118, OK). `tests.test_bfgs_window_consumers` and the full suite: NOT EXECUTED.
- Rows R59-3b and R60-2b as mutations. The counterfactuals of the rows carried unchanged from the round-2 erratum that it marks NOT EXECUTED remain so.
- Amendment 63's edit and the read-only property as files. Both were run in memory only.
- A real charging **suite** bundle through the envelope gate. Z7 replaces the verdict.
- Whether a record built by `evaluate_member` reaches the two other callers of `_idle_admission_core_evaluation` (`idle_admission_core_verdict` at `:5330`, `_run_whole_window_verdict_locked` at `:6360`). I established only that `evaluate_member` is called in three functions (Z11). The refuter traces this under A3.
- The classes of the other rows of `scripts/run_campaign.py` that the prototype reports (`_basis_member_occurrences`, `_run_record_supersession_locked`, `existing_state`, and four more). Step 9 is the seat's.
- The kinds of the 48 raw-capture readers. I sorted none.
- AP-5's text. I took "the envelope verdict licenses scored campaigns" from the round-2 refuter and two seats, who quote `docs/contracts/analysis_plans.md:270` and `:277`. I did not open the file.
- The Opus seat's `p2.py` (its run-time prototype) and `p3.py` (six further forms). I ran my own B-3 probe instead of `p2.py`; the six forms of `p3.py` are taken from its report as read, not re-run.
- The round-1 ruling, charge and refuter: not read.

---

## 13. Probes written in this session (`/tmp/cg_samesig/`; SHA-256 prefix)

| File | Prefix | What it is |
|---|---|---|
| `inv.py` | `d49376a37f4df269` | Z2: the round-2 detector on `run_campaign.py` at three commits |
| `dom.py` | `09202da1b6f79c37` | Z9: the enclosing branches of each gate call and consuming call |
| `cons.py` | `866aa785ca453012` | Z9: dominance as ruled and with rule (d) 6; four counterfactuals |
| `det.py` | `c97abb7dff3c4d85` | Z3, Z8: the prototype on the tree and on three envelope sources |
| `scopes.py` | `de71a3df0030110d` | Z5, Z8: the prototype with every scope; the helper without its gate |
| `patchlib.py` | `9ea12afcd2b37055` | the in-memory edits: amendment 63 (a), and the read-only property |
| `b3.py`, `b3b.py` | `844e3e537e3bdce9`, `3b105b2324e99230` | Z6 |
| `b4.py`, `b4_same.py` | `46fa75b56d84a08b`, `77f304c4928c2037` | Z7 |
| `run_tests_patched.py` | `2f978419207171ce` | Z6, Z7: a test module run against an in-memory edit |
| `rawcap_widened.py` | `0e4510d45b1d83ee` | Z12: the second judge's `rawcap2.py` with the pattern of 65 (a) |
| `p1.py`, `p4.py` | `41d207a0c458de03`, `ae8e23ce25c96bee` | the Opus seat's probes, copied unchanged and re-run (Z4, Z5) |

Z10, Z11 and Z13 to Z16 were run as commands typed into the shell and are given in full in §2. The earlier judges' prototypes were run from `/tmp/cg_sw_erratum/` and `/tmp/cg_sweep/`, unchanged. Files under `/tmp` are not durable. The amendment texts and the rows are written so the seat can implement without them.

---

## 14. Plain summary for Ed (5 lines)

1. The "sweep" is a test that reads the source code and lists every place that reads a measured run's energy files without first running the battery check (a run whose battery was charging has untrustworthy energy). Two review rounds in a row each found five new ways future code could slip past it, none in use today. I ruled, with all three consulted models, that a test of source text can never close every such way in Python, so the sweep's promise is narrowed in writing: it guards against ordinary code written by mistake, not against code that reaches into the check's own machinery.
2. I close the two gaps that are plausible mistakes: the sweep did not look at code outside function bodies, such as the block at the bottom of a script (the tree has 103 of them and the test saw none), and it counted calls of a helper but not a helper passed to `map`. Both closures add no entries on today's code. Replacing the check's function, or re-pointing a reader object at another run's directory, is recorded as a stated limit; the second gets a four-line run-time fix as its own small task after the current work package (S1, the battery-check wiring) merges.
3. The sweep is failing today, and the cause is not what it looks like: an earlier fix moved a battery check between two functions, and the old version of the test, which treats a function as fully checked if a check appears anywhere in it, then hid a read that happens 162 lines before the check. The fix is the already-ruled replacement of that detector, not an edit of the exemption list. I also found that one exemption ruled earlier fails its own check on the current code, and wrote the one narrow rule that makes it checkable, with four failure cases executed.
4. Two reads in the command that validates calibration runs were filed under a reason that is false. The edit two models proposed does not remove them from the list: I ran it. A three-line helper that performs the battery check next to the read does, gives byte-identical output, passes all 27 of that command's tests, and with it a future mistake that today would release five energy values of a refused run raises an error instead. That is the one production change inside S1.
5. The lane now ends on a fixed list: five conditions (A1 to A5) checked at one commit, and one review pass by a second model. Newly imagined bypasses never block the merge; a wrong exemption or a real unchecked read does. The deeper fix, giving the reader a checked `summary()` method so that a safe read and an unsafe read stop looking identical, is its own later task and blocks nothing.
