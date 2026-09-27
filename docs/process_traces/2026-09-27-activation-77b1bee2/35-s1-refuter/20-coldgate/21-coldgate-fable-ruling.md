RULING: S1 MERGE NOT BLOCKED

# Cold gate S1-A3-ROUTE-01: ruling (Fable 5.1, cold judge) on the S1 refuter's two A3 findings

Candidate: working tree `/Users/edr/code/JouleWise-wt-s1-refuter-77b1bee2`, detached @ `4aefdd12` (S1 head `204424e6` merged with main `b69c39eb`). Merge base of the two: `97082508`. Base (the commit S1 branched from): `1417c0c4`.
Under review: `35-s1-refuter/11-refuter-report.md`, ending `S1 REFUTER: A3 FAILS`.
Session: one session, no subagents, no background task, every probe in the foreground. No repository file edited: `git status --short` printed 0 lines after every probe. Scratch: `/tmp/cg-s1a3-77b1bee2/`. Session clock: 13:07:05 to 13:18:31 local for the probes; this file written after that (budget 35 minutes).

---

## 0. Contamination disclosure and protocol deviations (written first)

The charge told me not to read `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAUDE*.md`, `AGENTS.md`, memory or skill files. I opened none of them. These exposures happened anyway:

1. **Placed in my context by the harness before the charge arrived:** the owner's global `CLAUDE.md` (a pointer to orchestration doctrine, and a writing standard), this working tree's `CLAUDE.md` (notes on the bridge to a second model), the memory index `MEMORY.md` (about 110 one-line summaries), the names of installed skills, and the last five commit subjects. Three index lines bear on this charge: one says a second measurement window is admitted and "S1 refuter running"; one says review gates exist "only to keep science defensible"; one says "model agreement is not progress; drop ceremony that catches nothing". The last two lean toward not blocking. I opened no file any line points to and invoked no skill. I did **not** use the index to decide anything: each ruling below rests on a probe I ran or a line I quote, and on reasons the three listed rulings already state.
2. **File names seen, files not opened.** `ls` of my export of main printed `AGENTS.md`, `AGENT_PLAN.md`, `CLAIMS_STATUS.md`, `CLAUDE.md`, `LICENSE`. `ls` of the refuter's scratch directory printed `report.md`, `report.log` and three more report files. I opened none.
3. **The refuter's probes.** I read `attached_probe.py` in full and the first 40 lines of `cooldown_probe.py`. The second is byte-identical to the earlier judge's `f1_probe.py` (both hash to SHA-256 prefix `186e2a466569e861`).
4. **The rulings I apply and I are the same model.** That is a shared-blind-spot risk, and it is sharper here than before: the refuter, a different model, read a rule strictly, and I rule that the strict reading is not the ruled meaning. Against the risk: §3 says plainly that the refuter's reading of the **words** is correct; every fact about which lines S1 changed is executed and listed line by line (X4, X5); and the rule is rewritten so that the next reader needs no judge to apply it (amendment 77).

The writing standard in the global `CLAUDE.md` asks that every term be defined at first use. I followed it. It changes wording, not rulings.

**Protocol deviations, stated.**
- Twice the harness asked for a status line while I worked. I wrote one sentence each time and continued.
- One probe of mine (`lines_probe.py`) was wrong twice before it was right: first a stand-in object lacked a field, then I built the planted exception with the wrong argument, so the first two runs tested nothing. I edited my scratch file in place and re-ran. Only the third run is used (X7).

**What I read.** The charge; the three listed rulings, in full; the refuter's report, in full; in the tree, the lines named in §2. **Not read:** the refuter's brief (`01-refuter-brief.txt`); the round-1 and round-2 rulings; FT §E's text; the decision log (the D-161 entry is used as the SAMESIG ruling quotes it, its Z15).

---

## 1. Terms used in this ruling

Each term is defined once. Terms marked (R) are those of the three rulings I apply, repeated so this file stands alone.

- **Bundle** (R). The directory one measured run leaves behind. It holds `metadata.json` (what ran, and two battery readings), `summary_metrics.json` (the reduced numbers, energy and idle power included), and other files.
- **Charging bundle** (R). A bundle whose battery readings show current flowing into the battery during the run. Its energy and power numbers cannot be trusted.
- **Battery pair.** The two battery readings of one recording, one taken before and one after (`raw/battery_float.pre.ioreg`, `raw/battery_float.post.ioreg`).
- **The gate** (R). The check that a battery pair passes. **Window form:** `authenticate_window_members(members)` in `joulewise/bundle_read.py`; it takes (label, bundle path) pairs and returns verdicts or raises `WindowBatteryRefusal`. **Reader form:** `BundleReader.metadata()`. **Capture form:** `battery_float.authenticate_capture(directory)`; its verdict's `status` is `pass` when the pair passes.
- **Custody failure** (R). The exception `CustodyFailure`: a file's bytes are not the bytes that were recorded. The ruled texts require that it always stays an exception.
- **Gate exceptions.** The tuple `GATE_EXCEPTIONS = (WindowBatteryRefusal, battery_float.CustodyFailure)`, defined by S1 at `joulewise/bundle_read.py:279`.
- **Energy-class value** (R). An energy, power, current, charge or voltage value, or a value computed from one.
- **Claim artifact** (R). A file a paper number is taken from or licensed by.
- **Campaign** (R). One run of `scripts/run_campaign.py`: it measures a list of configurations one after another and leaves one bundle per run. The bundles are its **members**. A **scored campaign** is one whose numbers are meant for the paper.
- **Idle baseline** (R). The key `idle_baseline` of a bundle's summary: the mean power the machine drew while idle just before the run, in watts.
- **Cooldown** (R). The wait between two runs of a campaign. The next run is released when measured idle power has fallen to a reference value times 1.1. If that does not happen within 300 s the result is `cap_hit`, and the next member is excluded.
- **Cooldown anchor** (R). A record that a campaign stores in its own provenance file: the idle baseline of its first eligible member. A later campaign reads it from disk and uses it as the cooldown reference.
- **Calibration capture** (R). A run in which the machine draws power in timed pulses, so that the meter's clock can be lined up with the machine's clock. Its result is the **fiducial bound**: a number of seconds that bounds how far the two clocks can disagree. It is computed by fitting pulse edges in power samples, so it is an energy-class value (ruled, RETURNS §5.2). A capture has a battery pair of its own.
- **Capture copy.** The copy of a calibration capture that a bundle carries in its subdirectory `instrument_calibration/`. It is put there when the run starts (**attachment**), by `controller._load_instrument_calibration_attachment`.
- **Reduction.** Computing a bundle's summary from its raw files (`joulewise/reduce.py`). The **calibration verifier** is `reduce._verify_instrument_calibration` (`:1171`): it re-derives the fiducial bound from the capture copy and returns it.
- **Whole-window preparation.** The method `AuthenticatedConsumptionSession._prepare` in `joulewise/whole_window.py` (`:641-951`). It prepares a window's bundles for a verdict and calls the calibration verifier at `:788`.
- **Frozen files** (R). Files the ruled texts require to stay byte-identical to base, among them `joulewise/reduce.py`.
- **The eight consumers** (R). The eight modules that turn bundles into claimed numbers, `scripts/run_campaign.py` and `joulewise/whole_window.py` among them. None may import `battery_float`.
- **Stop rule, A1 to A5** (R). The five conditions of amendment 61 (c) that end the review. A3, as replaced by 66 (b): no energy-class value reaches a claim artifact without a gate, on the routes through the eight consumers and the envelope gate, *other than by a pre-existing route returned under row 1c*.
- **Row 1b, row 1c** (R). Two rows of amendment 66 (a). Both concern an A3 failure whose fix is production code that no ruling covers. **1b:** the route is one that S1 introduced or changed; it blocks S1's merge. **1c:** the route is pre-existing; it goes to a lane with an order and does not block.
- **Route.** The path of one value from the file it is read from to the claim artifact it arrives in.
- **Lane** (R). A separate work package with its own branch and its own cold gate.
- **The seat, the refuter, the lead** (R). The model session that implements; the model that checks; the session that commits and merges.
- **Member source / non-member source.** New here. A member source is a bundle that is a member of the window being judged. A non-member source is any other object from which the window's verdict takes an energy-class value.

---

## 2. Executed evidence (this session, Python 3.14, `PYTHONDONTWRITEBYTECODE=1`)

"Main" below is `b69c39eb`, exported by `git archive` into scratch.

| Id | Probe | Result (exact) |
|---|---|---|
| X1 | `git rev-parse HEAD`; `git merge-base 204424e6 b69c39eb` | `4aefdd1213aa…`; `97082508…` |
| X2 | For nine production files: `git diff b69c39eb 4aefdd12 -- <file>` against `git diff 97082508 204424e6 -- <file>`, compared by hash | Equal for all nine, so main added nothing to them since S1 branched off it. Changed lines between main and candidate: `run_campaign.py` 141, `whole_window.py` 216, `controller.py` 72. **Zero** in `reduce.py`, `cooldown_anchor.py`, `campaign_provenance.py`, `battery_float.py`, `bundle.py`, `powermetrics_fiducial.py`. |
| X3 | `git diff --quiet <commit> 4aefdd12 -- <file>` for `315364b2`, `8953c7a5`, `204424e6` and six route files | All 18 comparisons `identical`. The two earlier judges ruled on the same bytes of `run_campaign.py` and `whole_window.py` that the refuter read. |
| X4 | `funcmap.py`: every changed line between main and candidate, mapped by syntax tree to the function that holds it | `run_campaign.py`: 17 scopes, 145 lines added, 1 removed. `evaluate_member` +2 (`:2812-2813`). `campaign_cooldown_before_member` +2 (`:4221-4222`). `run_campaign` +22. `run_axi_spec_campaign` +18. `append_verdict` +3. **No changed line** in `cooldown_reference_eligibility`, `_first_eligible_cooldown_anchor`, `prior_campaign_cooldown_anchor`, `_member_readiness_reasons`, `evaluate_members`. `whole_window.py`: `_prepare` +7 (`:680-686`), `__init__` +1 (`:535`). `controller.py`: `_load_instrument_calibration_attachment` +8, −5. |
| X5 | The changed lines themselves, read | Quoted in §4.2 and §5.2. |
| X6 | The earlier judge's `f1_probe.py` (prefix `186e2a466569e861`), unchanged, on the candidate and on main | Candidate: the gate refuses bundle `C` (`battery_float_confounded`); `evaluate_member(C)` returns idle power `9.99`; the anchor is stored and read back as `('C', 9.99)`; with a fake meter at 5.0 W: `result=recovered … reference_power_w=9.99 effective_upper_w=10.989 waited_s=30.0`, reasons `[]`; with 0.2 W in the anchor: `cap_hit`, `waited_s=300.0`, `['cooldown_cap_hit']`. **Main:** `diff` of the two outputs shows two lines: main has no `authenticate_window_members`, and the provenance file's name holds a timestamp. |
| X7 | `lines_probe.py`: `validate_bundle` replaced, for the call only, by a function that raises `CustodyFailure`; then `evaluate_member(C)` | **Candidate:** `RAISED CustodyFailure`. **Main:** `RETURNED; idle_baseline.power_w_mean= 9.99`, with the failure turned into a problem string. |
| X8 | `f2_build.py`, `f2_check.py`: a bundle built by the repository's test helper `_run_p2038_with_battery`; a copy of it with the capture copy's battery pair removed and the three digests that name the changed files recomputed (the refuter's edit); each checked on candidate and on main | See §5.3. All four runs return the bound `0.02142716616057592` and the same energy envelope. |
| X9 | `capture_precheck.py` (text in §5.6) on the two bundles of X8; the earlier judge's `anchor_precheck.py` (prefix `e97ba58dae31876c`) on the data of X6 | Control alone: exit 0. Control and edited: `mutated: capture verdict battery_float_evidence_missing: REFUSE`, exit 1. Anchor pre-check: refuses the anchor from `C`, exit 1. |
| X10 | The fences of A5 | `battery_float.py` hashes to prefix `4b4d7bb20625`; it, `reduce.py` and `bundle.py` are identical to base; each of the eight consumers holds 0 lines that import `battery_float`. |
| X11 | `grep` over main's `joulewise/*.py` and `scripts/run_campaign.py` for the two gate names | One line: the definition of `authenticate_capture` (`battery_float.py:1069`). Main calls no battery gate anywhere on either route. |

**Limits of the probes, stated so they are plain.**
- X6 calls the campaign script's functions in the script's order with a fake meter. Two whole campaigns from the command line: NOT EXECUTED.
- X8 drives the route as far as the value that `reduce_bundle` returns. It does **not** run whole-window preparation. The leg from `:788` onward is read (§5.2), NOT EXECUTED.
- X8's edited bundle is made by editing a finished bundle. The capture it came from had a passing pair, so the bound is a true one. The probe shows that nothing re-checks the pair. It does not show a wrong number.
- X7 plants the exception. I did not find a real bundle on which `validate_bundle` raises a custody failure.
- X4 maps lines to functions by syntax tree. It does not say what a line does; §4.2 and §5.2 do, by reading.

---

## 3. The question under both findings: what does "no changed line in any function on the route" mean?

**The forcing problem.** Row 1c exists so that an old defect, found while reviewing new work, goes to its own lane and does not hold the new work hostage. Row 1b exists so that a defect the new work caused is fixed in the new work. Something must tell the two apart. Amendment 66 (a) gives three tests, and the third reads: "`git diff <main> <merge candidate>` holding no changed line in any function on the route".

**The refuter's reading.** S1 added lines inside `evaluate_member` and inside `campaign_cooldown_before_member`. Both functions are on F1's route. So the third test fails and row 1b applies. The same for F2 and whole-window preparation.

**As words, that reading is correct, and the refuter was right to return it.** A refuter does not interpret a rule in the direction that lets a finding through.

**As the ruled meaning, it cannot stand**, for a reason that is executed and not argued:

1. The judge who wrote the sentence applied it, in the same document, to F1 at commit `315364b2`, and found it met (its E5: "Changed lines on the route between main and S1: **0**. S1 changes 146 lines of the file, all elsewhere"). The test it ran counted changed lines that hold `anchor`, `idle_baseline` or `cooldown`.
2. `scripts/run_campaign.py` at `315364b2` is byte-identical to the file at the candidate (X3). The four lines the refuter names were already there.
3. So were 22 changed lines in `run_campaign` and 18 in `run_axi_spec_campaign` (X4), which are the two functions that hold every call on the route. Under the literal words, F1 could never have been row 1c, and the document's own ruling of F1 would be void in the document that made it.
4. The second judge applied the same test to the same bytes and reached the same result (RETURNS, R10, §6.2).

A rule whose words contradict its own first application has a drafting error. The error is in the words: they name the **function**, and the test that was run looked at the **lines that carry the value**.

**Why the literal words are also the wrong rule, on the science.** S1's task is to put a gate into every function that turns bundles into numbers. A rule that says "S1 changed this function, so S1 owns every defect on any route through it" makes S1 own every old defect in exactly the places where it did its job. Row 1c would be empty.

**What the rule must still prevent.** A seat must not be able to change the path of a value and call the result pre-existing. So the corrected rule does not ask a judge for an opinion. It asks for a list: every changed line in every function on the route, quoted, and each one either carries the value (then row 1b) or is one of two closed forms that can only stop execution.

### Amendment 77 (replaces test (iii) of amendment 66 (a); adds a rule on findings already routed)

77. **Test (iii) speaks of lines on the route, and the return lists every changed line.**

**(a) In 66 (a), test (iii) is replaced by:**

> (iii) a list of **every** line that `git diff <main> <merge candidate>` adds, removes or changes inside a function on the route, each quoted with its line number, and none of them **on the route**. The functions on the route are those that read the value from its source, those it passes through as an argument, a return value, an attribute or a stored record, and those that hold the calls between them.
>
> A changed line is **on the route** unless it has one of two forms:
> 1. **a gate statement:** a call of `authenticate_window_members`, of `BundleReader.metadata` or of `battery_float.authenticate_capture`; the statements that build that call's argument from paths and labels; and the statements that store or pass on the statuses of the verdicts it returns;
> 2. **a gate-exception handler:** `except GATE_EXCEPTIONS:` whose body is the single statement `raise`.
>
> Any other changed line in a function on the route is on the route, and row 1b applies. The two forms are a closed list. A third form needs a cold gate.

Why the two forms are safe: each can end an execution and neither can start one. A gate statement returns verdicts or raises. The handler re-raises. Neither binds, passes, returns or stores the value, so neither can carry it to a place it did not reach on main.

**(b) 66 (a) gains:** "A finding that a cold gate has routed under row 1c is not returned again by a later pass unless the return shows a new fact: a changed line in a function on the route since the commit of that ruling, or a probe output that differs from the one the ruling records. Without a new fact the later pass names the lane and moves on."

**Test rows for amendment 77.** They are rows for a reader of a return, not for the sweep.

| Row | Production site | Input | Expected | Must fail under this counterfactual |
|---|---|---|---|---|
| R77-1 | `evaluate_member`, `run_campaign.py:2811-2813` | the candidate's diff against main | two changed lines, both form 2 (**executed by reading, X5**); row 1c stays open | the diff with `summary = parsed` moved or changed inside the same function: a line that binds the value, so row 1b |
| R77-2 | `_prepare`, `whole_window.py:680-686` | the candidate's diff against main | seven changed lines, all form 1 (X5) | the diff with a changed argument in the call at `:788`, so row 1b |

---

## 4. F1: the cooldown anchor

### 4.1 Verified by execution

The refuter's F1 is **true**, and it is the finding the two earlier gates ruled. X6 reproduces every link on the candidate: a charging bundle that the gate refuses has its idle baseline of 9.99 W stored as the anchor; the next campaign reads it from disk; with the meter at 5.0 W the machine is declared cooled down after 30 s, where an anchor of 0.2 W gives `cap_hit` after 300 s and excludes the next member. The route, with every element named, is the diagram in §4.2 of the SAMESIG erratum. I do not redraw it: no element has changed (X3).

### 4.2 Which S1-added lines lie in the two functions, and where

Four lines, two in each function (X4). They are the same two lines twice.

**`evaluate_member`, `:2810-2815`** (added lines marked `+`):

```python
        try:
            problems = validate_bundle(bundle_dir, strict=True)
+       except GATE_EXCEPTIONS:
+           raise
        except Exception as exc:
            problems = [f"strict validation raised {type(exc).__name__}: {exc}"]
```

**`campaign_cooldown_before_member`, `:4220-4224`:**

```python
            note.update({"result": "unknown", "reason": "cooldown trace was empty"})
+   except GATE_EXCEPTIONS:
+       raise
    except Exception as exc:  # noqa: BLE001 - evidence failure must stay fail-closed.
        note.update({"result": "unknown", "reason": f"{type(exc).__name__}: {exc}"})
```

**Do they lie on the anchor route itself? No.** The value enters `evaluate_member` lower in the function, where it parses `summary_metrics.json` and keeps the result (`:2822-2826`), and those lines are unchanged. The added handler sits on the strict-validation call, which returns a list of problem strings and never touches the idle baseline. In the cooldown function the value enters as the reference power, far above the handler; the handler wraps the whole body and acts only if a gate exception arrives.

**What the lines do, executed (X7).** One input reaches them: a gate exception raised inside the wrapped call. I planted a custody failure there.

| Tree | `evaluate_member(C)` with a custody failure raised by strict validation |
|---|---|
| main | returns; the failure becomes a problem string; idle power **9.99 W travels on** |
| candidate | raises `CustodyFailure`; **nothing travels on** |

So on the one input where S1's lines act, they close the route. On every other input they do nothing, which is why the probe's output is the same on both trees (X6).

**The other changed lines in functions on the route** (the list that amendment 77 (a) requires):

| Function | Changed lines | Form |
|---|---|---|
| `evaluate_member` | `:2812-2813` | 2, handler |
| `campaign_cooldown_before_member` | `:4221-4222` | 2, handler |
| `run_campaign` | `:8374-8375`, `:8386-8387`, `:8446-8447` | 2, handler |
| `run_campaign` | `:9020-9032`: the list `battery_members` built from bundle ids and paths, then `battery_verdicts = authenticate_window_members(battery_members)` | 1, gate statement |
| `run_campaign` | `:9083-9085`: `battery_float_members={label: verdict.status …}` handed to `append_verdict` | 1, stores statuses |
| `run_axi_spec_campaign` | `:7393-7394`, `:7425-7426` | 2, handler |
| `run_axi_spec_campaign` | `:7837-7850`: paths and labels collected, then `authenticate_window_members(…)` | 1, gate statement |
| `append_verdict` | the parameter `battery_float_members` and the row key of that name | 1, stores statuses |

No line binds, passes, returns or stores an idle baseline, an anchor or a cooldown note. `cooldown_anchor.py` and `campaign_provenance.py` are unchanged (X2).

### 4.3 Ruling on F1

- **Under 66 (a) as written:** read word for word, test (iii) is not met, and the words give row 1b. Read as it was ruled and applied, twice, on these bytes, it is met. The words are corrected by amendment 77.
- **Row 1c applies.** Its three tests, each executed: (i) X6; (ii) X6 on main; (iii) the table above.
- **F1 is not an S1 merge blocker.** It is lane **BFGS-COOLDOWN-ANCHOR-01**, as ruled by amendment 66, with the order ruled there: it merges before the next scored campaign starts, and until then the anchor pre-check of the SAMESIG erratum's §4.6 runs before every scored campaign. I re-ran that pre-check on this session's data: it refuses the anchor from `C` (X9).
- Under amendment 77 (b), F1 is not returned a fourth time without a new fact.

---

## 5. F2: the capture copy whose battery pair is missing

### 5.1 The forcing problem

A bundle carries two recordings: the run itself, and the calibration capture that was attached to it. Each has its own battery pair, because each was recorded at a different time. The window gate checks the run's pair. The capture's pair is checked once, at attachment (`controller.py:448`). After that the capture copy is only re-read for its power samples. If the copy's pair is absent when the bundle is later reduced, nothing notices.

### 5.2 The route, with every element named

```
 AT COLLECTION (the run starts)                  AT CONSUMPTION (a verdict is prepared)
 ------------------------------                  --------------------------------------
 [K]  calibration capture directory              [W]  _prepare  (whole_window.py:641)
        its own battery pair                            |
        |                                        [G]  window gate (:680-682)  ADDED BY S1
 [A]  _load_instrument_calibration_attachment           checks the RUN's pair of each bundle
        (controller.py:370)                             |
 [GA] capture gate (:448-450)  ADDED BY S1       [V]  _verify_instrument_calibration
        refuses unless the pair passes                  (reduce.py:1171, called at :788)
        |                                               reads [C]'s power samples, returns
 [C]  capture copy inside the bundle:                   the bound; reads NO battery pair
        <bundle>/instrument_calibration/                |
        --------------------------------------->  [B]  the bound, 0.0214 s in the probe
                                                        |
                                                 [E]  energy envelope of the bundle:
                                                        point, lower, upper, in joules
```

- **[K]** is the source. **[C]** is the copy the bundle carries. **[A]** makes the copy. **[GA]** and **[G]** are the two gates S1 added. **[V]** is the calibration verifier, in a frozen file. **[B]** is the value. **[E]** is where it arrives: the bound widens the interval around the bundle's energy.
- The arrow from **[C]** to **[V]** is the only link between the two halves. It is a directory on disk.
- **The gap:** no element on the right-hand side runs the capture form of the gate on **[C]**.

**The leg after `:788`, read, not run.** `_prepare` refuses the member if the verifier returns a detail or no finite bound (`:798-809`), and refuses it if the bound differs from the number stored in `metadata.json` by more than 1e-9 (`:810-824`). Otherwise the member is appended to the list that the verdict is computed from (`:825`). None of those tests reads the capture copy's battery pair.

### 5.3 Worked example (executed, X8)

One bundle from the repository's test helper. "Edited" is a copy in which the capture copy's two battery readings are deleted, its `battery_float` record is removed, and the three digests that name the changed files are recomputed.

| Bundle | Tree | Run's pair | Capture copy's pair | Bound returned by [V] | Strict validation | Re-reduction |
|---|---|---|---|---|---|---|
| control | candidate | `pass` | `pass` | 0.0214272 s | no problems | succeeded; 88.5432 J, interval 88.4800 to 88.6064 J |
| control | main | `pass` | `pass` | 0.0214272 s | no problems | the same |
| **edited** | candidate | `pass` | **`battery_float_evidence_missing`** | **0.0214272 s** | no problems | **succeeded; the same interval** |
| **edited** | main | `pass` | **`battery_float_evidence_missing`** | **0.0214272 s** | no problems | **succeeded; the same interval** |

**So the refuter's F2 is true as far as the reducer's result.** A capture copy that the capture gate would refuse still yields its bound, and the bundle still reduces to an energy interval.

### 5.4 Is the missing recheck pre-existing on main? Yes

1. `joulewise/reduce.py` is byte-identical to main and to base (X2, X10). It is a frozen file. S1 could not have added the recheck there, and did not remove one.
2. The same probe gives the same output on main (§5.3).
3. Main is the less protected of the two trees, and by more than the recheck. Main calls no battery gate on this route at all (X11). Main's attach function goes further: it **refuses** any capture that carries a battery record (`controller.py`, the lines S1 removed: `"battery_float" in evidence` raises "revision_five evidence cannot be attached"). On main, a capture copy with no pair is the only kind a bundle can carry.

### 5.5 Did S1's change to whole-window preparation touch the route? No

S1 added seven lines to `_prepare` and they are one statement and its record (X5):

```python
+        battery_verdicts = authenticate_window_members(
+            (bundle_id, path) for bundle_id, path in sorted(bundle_paths.items())
+        )
+        self.battery_float_members = {
+            label: verdict.status for label, verdict in battery_verdicts.items()
+        }
+
```

That is element **[G]**. It stands 108 lines above the call at `:788`. The call, its five arguments, and every test on its result are unchanged. The list that amendment 77 (a) requires:

| Function | Changed lines | Form |
|---|---|---|
| `AuthenticatedConsumptionSession._prepare` | `:680-686` | 1, gate statement and its statuses |
| `AuthenticatedConsumptionSession.__init__` | `:535`, `self.battery_float_members: dict[str, str] = {}` | 1, stores statuses |
| `reduce._verify_instrument_calibration`, `reduce._derive_anchor_context` | none | |
| `powermetrics_fiducial.py`, all of it | none | |

**The effect of [G] on this route** is to narrow it. A bundle recorded by main's controller holds no battery pair for the run (main's `controller.py` names `battery_float` on one line, the refusal quoted above, against 22 lines on the candidate). Such a bundle is refused at **[G]** and never reaches `:788`. That is read from the two files, not run.

**Two things I could not fit into the two closed forms, stated so they are not hidden.**
- `controller._load_instrument_calibration_attachment` is changed by S1 (+8, −5). It is element **[A]**, upstream of the refuter's route. Three of its added lines are the capture gate. Three more copy the two battery readings into the capture copy (`files[relative] = (root / relative).read_bytes()`). Those copy battery readings, which are what the gate reads; they carry no bound and no power sample. Five removed lines are the refusal quoted in §5.4. **This function was ruled** as gated in the RETURNS ruling (amendment 74 (d), `capture_in_function`, row R74-1), on these bytes (X3). I do not re-open it.
- The verifier calls two methods of the bundle reader that S1 changed: `events` (+12, −5: stricter parsing of the bundle's journal) and `measured_window` (+1: `self.metadata()`, the reader form of the gate, itself changed by +6). They read the **bundle's** files. The capture copy is read by the verifier's own code in `reduce.py`, which is unchanged. I read the verifier's list of calls (by syntax tree) and the changed methods. I did not trace each call's use: NOT EXECUTED.

### 5.6 Ruling on F2

- **Row 1c applies**, on the same reading of 66 (a) as for F1. Its three tests: (i) X8, as far as the reducer's result, with the leg into the whole-window verdict read and not run; (ii) X8 on main; (iii) the table of §5.5.
- **F2 is not an S1 merge blocker.** It is item 5 of lane **BFGS-RAWCAPTURE-01**, which the RETURNS ruling opened with exactly this question (its §5.4 and §5.5). The refuter has now answered the question by execution, and that is the pass doing its job.
- **Item 5 needs an order of its own.** The RETURNS ruling gave the lane "no constraint against the next scored campaign", and reasoned it for five script functions that are on no campaign's path. Item 5 is on a consumer's path, so that reasoning does not cover it. Amendment 66 (a) requires every lane under 1c to state an order against the artifact at risk. It is ruled here (amendment 78).

**How the edited state can arise.** This decides how urgent the item is, so I state what I know and what I do not.

| Where the bundle comes from | Can it reach `:788` with a capture copy that fails the capture gate? |
|---|---|
| recorded by S1's controller | No, by attachment: **[GA]** refuses the capture first. (Read, and ruled in R74-1.) |
| recorded by main's controller | No: the run has no pair, so **[G]** refuses the bundle. (Read.) |
| a bundle on the pinned list of old bundles, which the gate admits with the status `unobserved_historical` (`bundle_read.py:453`, `:484-486`) | **Probably yes.** Neither the run's pair nor the capture's was ever recorded. That is a ruled exemption with a closed list. NOT EXECUTED: I ran no old bundle. |
| a finished bundle whose files are edited and whose digests are recomputed | Yes (X8). It takes three consistent edits. The SAMESIG ruling quotes the project's threat model as one trusted operator (its Z15). |

So after S1 merges, new bundles are protected at attachment, and what is missing is the second check at consumption. That is a real gap, and a smaller one than on main.

### Amendment 78 (adds to §5.5 of the RETURNS ruling: the order of item 5, and a pre-check)

78. **Item 5 of lane BFGS-RAWCAPTURE-01 is on a consumer's route and has its own order.**

**(a) Order.** A whole-window verdict can be computed again from stored bundles at any time, so no collection is at risk. The artifact at risk is a verdict that is **used**. Item 5 merges before any whole-window verdict computed after S1's merge is used for a number in the paper.

**(b) Until it has merged,** before such a verdict is used, the lead runs the pre-check below on every member bundle of the window and records its output in the window's trace. The verdict is used only if the exit code is 0. For a member whose bundle verdict is `unobserved_historical`, a capture verdict of `battery_float_evidence_missing` is recorded and is not a refusal; the paper states that the battery state of that run and of its capture was not recorded.

```python
"""Run the capture form of the battery gate on the calibration copy each bundle carries.
Read-only. Exit 0 only if every bundle given carries a copy whose verdict is pass.
Usage: python3 -B capture_precheck.py <repo_root> <bundle_dir> [<bundle_dir> ...]"""
import sys
from pathlib import Path
repo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(repo))
from joulewise import battery_float
bad = 0
for text in sys.argv[2:]:
    bundle = Path(text).resolve()
    capture = bundle / "instrument_calibration"
    if not capture.is_dir():
        print(f"{bundle.name}: no calibration copy: REFUSE"); bad += 1; continue
    try:
        verdict = battery_float.authenticate_capture(capture)
    except Exception as exc:
        print(f"{bundle.name}: {type(exc).__name__}: {exc}: REFUSE"); bad += 1; continue
    ok = verdict.status == "pass"
    print(f"{bundle.name}: capture verdict {verdict.status}: {'pass' if ok else 'REFUSE'}")
    bad += 0 if ok else 1
print("bundles:", len(sys.argv) - 2, "refused:", bad)
sys.exit(1 if bad else 0)
```

It is a command the lead runs. It is not repository code and it is not the fix. Executed on the probe's two bundles (X9). NOT run on a real window. It treats a custody failure as a reason not to use the verdict and converts nothing.

**(c) What item 5 must achieve.** I rule what must hold, not the code.
1. Before the verifier's bound is accepted at `whole_window.py:788`, the capture form of the gate has run on that bundle's capture copy, in the same process, and returned `pass`.
2. The same at the verifier's other two call sites: `reduce.py:1820` (in a frozen file, so the check goes to the callers of reduction) and `whole_window.py:4585`.
3. The eight consumers still import no `battery_float`. The check is reached through `joulewise/bundle_read.py`, as the window gate is.
4. A custody failure stays an exception.
5. The lane rules what a member with the bundle verdict `unobserved_historical` does.

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| RCC-1 | `_prepare`, the call at `whole_window.py:788` | the edited bundle of X8 | the member is refused with a reason that names the capture's status; no bound is accepted | the tree: the verifier returns `(0.02142716616057592, None)` (**executed RED at the verifier, X8**; at `_prepare`: NOT EXECUTED) |
| RCC-2 | the same | the control bundle of X8 | the bound is accepted | a fix that refuses every capture copy |
| RCC-3 | the same | the control bundle after one byte of the capture copy's `raw/battery_float.pre.ioreg` is changed | `CustodyFailure` leaves as an exception | a handler that turns it into a refusal reason |

RCC-2 and RCC-3 are NOT EXECUTED: they test code that does not exist yet.

---

## 6. Question 3: if either blocked, what would close it?

Neither blocks. The charge asks the question, and a later reader may disagree with §3, so I answer it in full.

1. **The closure must be production code.** F1 closes in `scripts/run_campaign.py`, where the anchor is stored and read back. F2 closes in `joulewise/whole_window.py` and `joulewise/bundle_read.py`, because `reduce.py` is frozen and a consumer may not import `battery_float`. No test closes either: a test can show the gap, and only a gate call removes it.
2. **Inside S1 it would need its own ruling and one more refuter pass.** The RETURNS ruling says no production code is ruled inside S1. Row 1b says a cold gate rules the fix as an amendment inside S1. The table of 61 (c) grants no further pass "unless the fix changes production code other than as ruled"; row 1b grants one pass, on the fix only. So the cost inside S1 is: two code rulings, one seat round, one refuter pass, and the suites again.
3. **"Land the lane first, then merge S1 on top" is not available.** Both fixes call gates that only S1 provides. Main has no `authenticate_window_members`, and no call of `authenticate_capture` (X6, X11). A lane branched from main would have to bring S1's gate with it, which is S1.
4. **So blocking would be circular:** S1 would wait for lanes that need S1. That is the practical form of the reason the SAMESIG erratum gave in its §4.5: the merge does not create the hazard, and refusing it does not remove it.

**The ordered plan, as ruled.**

| Order | Who | What |
|---|---|---|
| 1 | lead | A4 on the merge candidate `4aefdd12`: V1, V2 and the builder's forward check. They were reported green on the S1 head, and the merge changed no production file on either route (X2). I ran none of them. |
| 2 | lead | S1 merges. The merge description names: lane BFGS-COOLDOWN-ANCHOR-01 and its order; item 5 of lane BFGS-RAWCAPTURE-01 and its order (78 (a)); the two pre-checks; amendment 77. |
| 3 | lead | From the merge on: the anchor pre-check before every scored campaign; the capture pre-check before any whole-window verdict is used. |
| 4 | lead | The consult of §7, convened at once. It does not wait for the lanes, and the lanes do not write code before it returns. |
| 5 | lane | BFGS-COOLDOWN-ANCHOR-01 merges **before the next scored campaign starts**. Own cold gate. Rows RCA-1 to RCA-6 of the SAMESIG erratum. |
| 6 | lane | Item 5 of BFGS-RAWCAPTURE-01 merges **before a whole-window verdict computed after S1's merge is used for a paper number**. Own cold gate. Rows RCC-1 to RCC-3. |
| 7 | lane | The other four items of BFGS-RAWCAPTURE-01: order unchanged (before the paper's timing numbers are frozen). |

**The stop rule after this ruling.** A1, A2 and A5 hold by the refuter's pass, and I re-ran A5's fences (X10). A3 holds in the words of 66 (b): the only two routes found are pre-existing routes returned under row 1c. A4 is order 1. There is no second refuter pass on S1.

---

## 7. Question 4: is this the same defect class as the SWEEPCLASS rounds?

**Not the same class of finding.** The SWEEPCLASS rounds each found **latent forms**: ways of writing an unchecked read that nobody had written, which a test of source text would not report. The refuter found none this time, and says so (`rule_11: false`, no missed supported form). F1 and F2 are the opposite kind: real routes in today's tree, driven by execution. The three-form route of 61 (c) does not fire.

**But there are two repeats, and both deserve a name.**

**Repeat 1, in the process.** F1 has now been to three cold gates with no new fact: the same probe, the same output, the same bytes (X3, X6). What changed each time was the reading of a rule. Two rounds that fail for the same kind of reason is what the project's rule 11 calls a same signature. Amendment 77 is the cure: test (iii) becomes a list that a reader can check, and a routed finding is re-opened only by a new fact.

**Repeat 2, in the design.** F1, F2, and the salvage license that the RETURNS ruling names in its §4.4 have one shape:

```
   the window's verdict
        ^            ^
        |            |
   [M] members   [N] non-member sources
   checked by        checked where they were STORED or ATTACHED,
   the window        by another process, at another time,
   gate, now         or not at all
```

- **[M]** is the set of bundles the window gate sees. **[N]** is everything else that hands the verdict an energy-class value.
- Known members of **[N]**: the cooldown anchor's source bundle (F1, checked nowhere); the capture copy (F2, checked at attachment only); the aborted attempt behind a salvage license (no energy-class value leaves it: executed in the RETURNS ruling).

The SAMESIG ruling found the root of the sweep's trouble in its §9: whether a read is safe depends on what was called earlier and elsewhere. This is the same root, stretched across files and across time. The window gate answers "are this window's members sound?" and the verdict also depends on things that are not this window's members.

**What the structural consult should decide.** One consult, for the two lanes, before either writes code. It does not touch S1.

1. **The principle.** Is every object whose energy-class value reaches a verdict checked **in the process that consumes it**, and not only where it was stored or attached? I recommend yes: a check made at another time protects only as long as the bytes and the rules stay as they were.
2. **The closed list of non-member sources.** At least: the anchor's source bundle; an earlier campaign's cooldown notes (`prior_campaign_cooldown_evidence`, named and not traced in the SAMESIG erratum); the capture copy; the salvage attempt; the pinned list of old bundles. The consult names the list, and the sweep then holds it as a closed list, as it holds its five others.
3. **One home for the check.** Both lanes need "run a gate on something that is not a member", reached through `joulewise/bundle_read.py`. If each lane writes its own, the next refuter compares two idioms. The consult decides whether the window gate takes non-member sources as a second argument, or whether a sibling function does.
4. **Old bundles.** What status a capture copy takes when its bundle is admitted as `unobserved_historical`.
5. **The words of A3.** Whether A3 says "members" or "members and non-member sources". Today it says neither, and that silence is why the salvage license, the anchor and the capture copy each arrived as a surprise.

**What the consult must not do:** widen S1, add a rule to the sweep's detector, or re-open the stop rule. The number of non-member sources is finite and they can be listed, which the space of latent forms could not.

---

## 8. Kept intact

- **Custody is never a status.** No amendment here adds a status, a handler or a conversion. S1's handler lines do the opposite of a conversion: on main a custody failure inside strict validation became a problem string, and on the candidate it stays an exception (X7). Requirement 4 of 78 (c) and row RCC-3 carry the rule into item 5.
- **Authentication precedes every exclusion decision.** F1 and F2 are two places where it does not yet hold for a non-member source. No amendment here reorders production code. The two pre-checks stand in.
- **`joulewise/battery_float.py` and the frozen files are byte-identical** (X10). This ruling edits no file in any repository.
- **The eight consumers do not import `battery_float`** (X10). Requirement 3 of 78 (c) keeps it so.

---

## 9. Not executed

- V1, V2, the builder's forward check. I ran no test module of the repository.
- Whole-window preparation on the edited bundle: the leg from `whole_window.py:788` into a verdict row is read.
- Two whole campaigns from the command line; a real meter.
- A bundle from the pinned list of old bundles through either probe.
- Whether `validate_bundle` raises a gate exception on any real bundle. X7 plants one.
- The use the verifier makes of the three reader methods that S1 changed (§5.5).
- Whether `reduce_bundle` writes the envelope to `summary_metrics.json`. I printed the value it returns.
- Both pre-checks on a real runs directory or a real window.
- Rows RCC-1 (at `_prepare`), RCC-2, RCC-3; the counterfactuals of R77-1 and R77-2.
- The refuter's A1 and A2 runs. I did not re-run them; they took 13 minutes in its report.
- How far a charging battery moves a fitted pulse edge (carried from the RETURNS ruling).

---

## 10. Probes written in this session (`/tmp/cg-s1a3-77b1bee2/`; SHA-256 prefix)

| File | Prefix | What it is |
|---|---|---|
| `funcmap.py` | `b8139693ff7ee6ad` | X4: every changed line between two commits, mapped to its function |
| `f1_probe.py` | `186e2a466569e861` | X6: the earlier judge's probe, copied unchanged |
| `lines_probe.py` | `eb65056ab5e42a06` | X7: the one input that reaches S1's handler lines |
| `f2_build.py` | `6222764457a94daf` | X8: builds the control bundle and the edited bundle |
| `f2_check.py` | `ae14eb88e582cbcd` | X8: the two gates, the verifier, strict validation and re-reduction on one bundle, on a tree given as argument |
| `capture_precheck.py` | `994e8af853050ed9` | X9: the pre-check of 78 (b) |
| `main/` | | `git archive b69c39eb`, the tree the main-side runs used |

X1 to X3, X5, X10 and X11 were run as commands typed into the shell. Files under `/tmp` are not durable. The pre-check is given in full in 78 (b), and each probe is described by its inputs and its calls so that it can be rebuilt.

---

## 11. Plain summary (3 lines)

1. Both findings are real and I reproduced them, but both are old: the same tests give the same output on the main branch, and the only lines the battery-check work (S1) added in the functions involved are the battery check itself and handlers that re-raise its errors, which can stop a bad value and cannot pass one on. S1's merge is not blocked.
2. Each goes to its own follow-up task with a deadline and a read-only check that stands in until then: the stored idle-power reference (9.99 W from a charging run decided "cooled down" after 30 s) before the next scored campaign; the calibration recording whose own battery readings are missing (it still produced its 0.0214 s timing bound) before any window verdict is used for a paper number. Neither fix can land before S1, because both call checks that only S1 provides.
3. The rule the reviewer applied said "no changed line in any function", which was stricter than the test its author actually ran; I rewrote it as a checkable list and ruled that a finding already routed is re-opened only by a new fact. Not run by me: the full test suites (owed by the lead before merging), and the last step from the timing bound into a whole-window verdict, which I read but did not execute.
