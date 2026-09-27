# Cold gate SWEEPCLASS-SAMESIG-01, erratum: ruling (Fable 5.1, cold judge) on the paired refuter's F1 to F6

Candidate: working tree `/Users/edr/code/JouleWise-wt-samesig-cg-3ba66eeb`, detached @ `315364b2` (the S1 head). Main: `97082508`. Base (the commit S1 branched from): `1417c0c4`.
Under review: `21-coldgate-fable-ruling.md` (SHA-256 prefix `71b1c570e5226b1e`, checked) and `22-opus-paired-refuter.md` (prefix `103ac850986ca5df`), both in this directory.
Session: one session, no subagents, no background task, every probe in the foreground. No repository file edited: `git status --short` printed 0 lines after every probe. Scratch: `/tmp/cg_samesig_err/`. Session clock: 03:54 to 04:09 local (budget 35 minutes).

---

## 0. Contamination disclosure (written first)

The charge told me not to read `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAUDE*.md`, `AGENTS.md`, the decision log, or memory or skill files. I opened none of them. These exposures happened anyway:

1. **Placed in my context by the harness before the charge arrived:** the owner's global `CLAUDE.md` (a pointer to orchestration doctrine, and a writing standard), this working tree's `CLAUDE.md` (notes on the bridge to a second model), the memory index `MEMORY.md` (about 110 one-line summaries), and the names of installed skills. One index line reads "W1 ARMED … next = harvest W1, SWEEPCLASS erratum-2 (B-1..B-5), S1 fix-3". I opened no file that any line points to and invoked no skill. I did **not** use the index to decide anything. In particular, the order I rule for lane BFGS-COOLDOWN-ANCHOR-01 is stated against "the next scored campaign" in general, and does not rest on any belief about what is armed or running.
2. **File names seen, files not opened.** One search for the text of amendment 58 (`grep -rl` over `docs/process_traces`) printed the names of two activation records and one older ruling. I opened none of the three.
3. **Earlier rulings I opened, to quote amendment text exactly:** the round-1 erratum (`…/2026-09-26-activation-92472459/20-bfgs-s1/80-coldgate-r2/30-erratum/21-coldgate-fable-erratum-ruling.md`, lines 385 to 412: amendment 51 (f), (g), (h)), and the round-2 erratum (`…/2026-09-26-activation-22784e38/20-coldgate-sweep-erratum/21-coldgate-fable-erratum-ruling.md`, lines 376 to 409 and 435 to 461: amendments 58 (f) and 60).
4. **The ruling under review and I are the same model.** That is a shared-blind-spot risk. Against it: F1 is decided by an executed probe and not by reading, and two of my rulings below go against the text of the ruling under review (its consumers-form wording is false on the tree, §4.3; its clause 1 of the deliberate class is too wide, §8).

The writing standard in the global `CLAUDE.md` asks that every term be defined at first use. The charge asks the same of the summary. I followed it. It changes wording, not rulings.

**What I read.** The charge; the ruling under review, in full; the refuter's report, in full; its probe `q2_docs_scope.py`; the amendment texts of item 3. **Not read:** the consult charge and the three seat reports (the ruling under review restates them); the refuter's `q1_dominance.py`; the fix-round-3 brief.

---

## 1. Terms used in this ruling

Each term is defined once. Terms marked (R) are those of the ruling under review, repeated so this file stands alone.

- **Bundle** (R). The directory one measured run leaves behind. It holds `metadata.json` (what ran, and two battery readings), `summary_metrics.json` (the reduced numbers, energy and idle power included), `power_trace.csv` (the power samples), and other files.
- **Charging bundle** (R). A bundle whose battery readings show current flowing into the battery during the run. Its energy and power numbers cannot be trusted.
- **The gate** (R). The check that a bundle's battery readings pass. **Window form:** the function `authenticate_window_members(members)`, which takes a list of (label, bundle path) and returns all verdicts or raises `WindowBatteryRefusal`. **Reader form:** the method `BundleReader.metadata()`.
- **Custody failure** (R). The exception `CustodyFailure`: a file's bytes are not the bytes that were recorded. It is a different thing from a battery refusal, and the ruled texts require that it always stays an exception.
- **The sweep** (R). The test `tests/test_bfgs_consumer_sweep.py`. It parses tracked Python files and lists every **read site**: a place that reads one of the three **watched files** (`summary_metrics.json`, `metadata.json`, `power_trace.csv`) or calls a **tolerant accessor** (one of four reader methods that return a file's content without the battery check), with no gate call before it. Each listed place is a **row** and must have an entry in the test's **allowlist**, with a **class** (a named reason category whose condition the row must meet).
- **Energy-class value** (R). An energy, power, current, charge or voltage value, or a value computed from one.
- **Campaign.** One run of `scripts/run_campaign.py`: it measures a list of configurations one after another and leaves one bundle per run. The bundles are the campaign's **members**. A **scored campaign** is one whose answers are graded and whose numbers are meant for the paper.
- **Campaign provenance.** The file `runs/campaign_manifests/<session>.json` that a campaign writes about itself while it runs. Each write is recorded in the campaign log, so a later reader can tell that the file's bytes are the ones the campaign wrote.
- **Idle baseline.** The key `idle_baseline` of a bundle's `summary_metrics.json`: the mean power the machine drew while idle just before the run, in watts. It is an energy-class value.
- **Cooldown.** The wait between two runs of a campaign. The campaign measures idle power repeatedly and releases the next run when that power has fallen to a **reference** value times 1.1 (the policy's tolerance is 0.1). If that does not happen within the cap (300 s in the production policy), the result is `cap_hit`.
- **Cooldown anchor.** A record that a campaign stores in its provenance, once: the idle baseline of its first member that passes the eligibility check, with that bundle's id. It serves as the cooldown reference whenever the run just before is not itself eligible. "Freezing" the anchor is storing it.
- **Admission reason.** A string that the campaign attaches to a member to say why the member cannot be used for a claim, such as `cooldown_cap_hit`. A member with a reason is excluded.
- **Member verdict row.** The record of one member inside the campaign's verdict. The ruled texts list "a whole-window verdict row" as a **claim artifact** (a file a paper number is taken from or licensed by).
- **Consumers form** (R). One of two forms of the allowlist class `behind_gate`. It is for a function that reads bundle files during collection, before any gate can run, and hands the content on. Its row names the **consumers**: the calls that later turn that content into a verdict. The sweep checks that a gate call comes before each of them.
- **Dominates** (R). Said of a gate call and a later statement: execution cannot reach the statement unless the gate call ran and returned normally.
- **Scope** (R). The body of a function, of a class, of a `lambda`, or the top level of a file.
- **Reference** (R). A function's name used where it is not being called (`f = evaluate_member`).
- **Deliberate class** (R). Code that must reach into the gate's own machinery to read energy. The ruling under review places it outside what the sweep promises.
- **The seat, the refuter, the lead** (R). The model session that implements fix round 3; the model that checks the result; the session that commits and merges.
- **Counterfactual** (R). For a test row: the specific wrong implementation under which the row must fail. A row **goes RED** when it fails and is **GREEN** when it passes.
- **Stop rule, A1 to A5** (R). The five conditions of amendment 61 (c) that end the review of the sweep. A3 is "no energy-class value reaches a claim artifact without a gate".
- **Swept roots.** New in this ruling (amendment 68): the directories whose tracked Python files the sweep reads.

---

## 2. Executed evidence (this session, Python 3.14, `PYTHONDONTWRITEBYTECODE=1`)

| Id | Probe | Result (exact) |
|---|---|---|
| E1 | `f1_probe.py` (prefix `186e2a466569e861`), steps 1 to 3, on the tree `315364b2`. A bundle `C` is built as `tests/test_battery_float.py::BundleAuthenticationTests.bundle` builds one, with the repository's fixture `charging-synthetic-from-real.ioreg` as its first battery reading, an idle baseline of **9.99 W** in its summary, and the environment and policy fields that the anchor's eligibility check reads | `battery_float.authenticate_bundle(C)`: `battery_float_confounded ('pre IsCharging is not No',)`. `authenticate_window_members([C])`: `RAISED WindowBatteryRefusal`. `evaluate_member(C)`: **returned**, idle power `9.99`. `cooldown_reference_eligibility`: `eligible: True, reasons: []`. `_first_eligible_cooldown_anchor([evaluation], …)`: an anchor with `bundle_id 'C'`, `baseline.power_w_mean = 9.99` |
| E2 | The same probe, step 4. The anchor is written to a campaign's provenance with the production writer (`new_campaign_provenance`, then `write_campaign_provenance`, under the production campaign lock), then read back with `prior_campaign_cooldown_anchor(runs, "probe-manifest-1", policy digest, log)` | Provenance schema `joulewise.campaign_provenance.v2`. `prior_campaign_cooldown_anchor -> ('C', 9.99)` |
| E3 | The same probe, steps 5 and 6. `campaign_cooldown_before_member` is called as `tests/test_run_campaign.py:2306` calls it: the run just before is not eligible, and a fake meter reads **5.0 W**. Then `_member_readiness_reasons` on the following member. Three anchors | **(a) the anchor from C:** `result=recovered reference_selection=frozen_clean_anchor reference_power_w=9.99 effective_upper_w=10.989 waited_s=30.0`; the member's row carries `anchor bundle_id=C baseline power=9.99`; cooldown reasons `[]`. **(b) the same anchor with 0.2 W in place of 9.99:** `result=cap_hit … reference_power_w=0.2 … waited_s=300.0`; reasons `['cooldown_cap_hit']`. **(c) no anchor:** `result=unknown`; reasons `['campaign_cooldown_evidence_missing']` |
| E4 | The same probe, unchanged, on an export of main (`git archive 97082508` into scratch) | Every line of E1 to E3 identical, except one: `authenticate_window_members` does not exist in main's `joulewise/bundle_read.py` (`AttributeError`) |
| E5 | `git show <commit>:scripts/run_campaign.py` searched for the route's functions and for gate calls, at main and at base; `git diff 97082508 315364b2 -- scripts/run_campaign.py` searched for changed lines that hold `anchor`, `idle_baseline` or `cooldown`; `git diff --stat` over the four files on the route | The four functions and both call pairs exist at main and at base. Main's `run_campaign.py` holds **0** calls of `authenticate_window_members`. Changed lines on the route between main and S1: **0** (S1 changes 146 lines of the file, all elsewhere). `joulewise/cooldown_anchor.py` and `joulewise/campaign_provenance.py`: unchanged. |
| E6 | `grep -n WindowBatteryRefusal scripts/run_campaign.py` | 0 lines. No code in the campaign script takes a stored anchor back when the gate later refuses the window. |
| E7 | `f2_scan.py` (prefix `83745a240201abce`): an AST scan of the 209 tracked files under `joulewise/` and `scripts/` | Calls of `evaluate_member`: 6 (`:2924` in `evaluate_members`; `:7517`, `:7759`, `:7789`, `:8034` in `run_axi_spec_campaign`; `:8709` in `run_campaign`). Calls of `evaluate_members`: 2 (`:8587`, `:8880`, both in `run_campaign`). References to either name: `[]`. |
| E8 | The same scan: private names | `private-name imports from joulewise modules: 89 in 32 files` (the refuter's count reproduces). Uses of `._cache` or `._path` on anything other than `self`: `[]`. Writes or deletions of a `_`-prefixed attribute on anything other than `self`: 5, in three files. `BundleReader(bundle)._strict_json("metadata.json")` exists at `scripts/build_battery_float_historical_bundles.py:245`, and the first judge's prototype reports it (`sweep59.tree.out:93`: `witness direct:_strict_json metadata.json 245`). |
| E9 | The first judge's prototype `sweep59.py` (prefix `c7ef17cab8b81b3b`), run over tracked Python outside `joulewise/` and `scripts/` | Tree: 120 rows (as recorded). `docs/paper`: 6 files, **2 rows**, both in `docs/paper/figures/reproduce_worked_examples.py` (`historical`, `direct:read_bytes`, `power_trace.csv`, line 113; `synthetic`, `direct:read_bytes`, `power_trace.csv`, line 47). `configs`: 21 files, **0 rows**. `docs/legacy`: 1 file, 1 row (`analysis_appup_r01r02.py::analyze`, `metadata.json`, line 39). The refuter's B1 reproduces. |
| E10 | `git ls-files '*.py'` grouped by directory; `grep` for capture file names and for the guarded helpers' names under `docs/paper` and `configs` | Tracked Python outside `joulewise/`, `scripts/`, `tests/`: `docs/process_traces` 129, `configs/campaigns` 21, `docs/paper` 6, `docs/legacy` 1; none at the top level. One function outside the two ruled roots names a raw capture: `reproduce_worked_examples.py::historical`, line 79 (`raw/powermetrics.plist`). Calls of a guarded helper under `docs/paper` or `configs`: 0. |
| E11 | An AST scan of `run_campaign` and `run_axi_spec_campaign`: calls that come before the function's gate line and take a member's evaluation as an argument | `run_campaign` (gate `:9032`): `campaign_cooldown_before_member` `:8798`; `_first_eligible_cooldown_anchor` `:8900`; `record_campaign_member_provenance` `:8670`, `:8743`, `:8979`; `evaluation_failure_detail` `:8596`, `:8951`. `run_axi_spec_campaign` (gate `:7848`): `campaign_cooldown_before_member` `:7612`; `_first_eligible_cooldown_anchor` `:7817`; `record_campaign_member_provenance` `:7796`; `dataclasses.replace` `:7529`, `:7766`, `:7795`. |
| E12 | `anchor_precheck.py` (prefix `e97ba58dae31876c`, text in §4.6) on the probe's runs directory | `anchor C: WindowBatteryRefusal: … battery_float_confounded …: REFUSE`; `manifests: 1 anchors refused: 1`; exit code 1 |

**Limits of the probes, stated so they are plain.**
- E1 to E4 call the production functions one after another, in the order the campaign script calls them. They do **not** run `run_campaign()` from its command line through two whole campaigns. That run is NOT EXECUTED. What stands between the two is read, not run: the call order at `:8880` to `:8911`, and E6.
- The meter in E3 is a fake that always reads 5.0 W. It shows that the anchor's value decides the result. It does not show what a real machine would read.
- Bundle `C` is minimal, so `evaluate_member` reports it as not strictly valid (`strict_valid=False`). The anchor's eligibility check does not read that field (`run_campaign.py:3933-3980`), which is why `C` is eligible all the same.
- E7, E8 and E11 match by name. E11 does not see a method called on an evaluation (`evaluation.to_log()` at `:8975`).
- E9 runs a prototype, not the repository's sweep.

---

## 3. Rulings at a glance

| Finding | Ruling |
|---|---|
| **F1** | **TRUE, by execution** (E1 to E3). **Pre-existing:** the same on main, and S1 changes no line of the route (E4, E5). **It does not block S1's merge.** It is its own lane, **BFGS-COOLDOWN-ANCHOR-01**, which must merge **before the next scored campaign starts**; until then a named pre-check runs before every scored campaign (§4.6). The route under 61 (c) is amendment 66. The consumers form's wording was false on the tree and is corrected (66 (c)). |
| **F2** | **UPHELD, text changed.** The refuter's "transitively, any function that returns its result" cannot be checked by a test that reads source. It becomes a named field, `producers` (amendment 67). |
| **F3** | **UPHELD in part.** The read-site sweep and the caller checks widen to `docs/paper/` and `configs/`, and the file scope becomes closed (amendment 68). The two rows are granted `non_claim` (i): **no `historical` grant is needed.** The raw-capture and journal inventories are **not** widened in S1, and the promise says so. |
| **F4** | **UPHELD.** Rows R51-23b and R51-23c (amendment 69). |
| **F5** | **UPHELD.** Clause 1 of the deliberate class is narrowed (amendment 70). |
| **F6** | **UPHELD, all three.** Rule (d) 6 wording with one row; R60-7 skip clause; the 61 (c) route is amendment 66 (amendment 71). |

---

## 4. F1: the cooldown anchor carries an unchecked idle power into a later campaign

### 4.1 The forcing problem

A campaign must decide, between two runs, whether the machine has cooled down. It compares the idle power it measures now with a reference idle power. The reference comes from a bundle. The campaign reads that bundle with `evaluate_member`, which runs during collection and holds no gate, because the gate for a window can only run once the window's members are all known. Inside one campaign that is safe: the gate at the end (`:9032`) covers every member, and refuses the whole window if one fails. The anchor breaks that reasoning, because the campaign **stores** it in a file that the **next** campaign reads, and the next campaign's gate covers only its own members.

### 4.2 The route, with every element named

```
 CAMPAIGN N-1                                              CAMPAIGN N
 ------------                                              ----------
 [B]  bundle C (charging)                                  [6] prior_campaign_cooldown_anchor
      summary_metrics.json: idle_baseline 9.99 W                (:4048; called :8350, :7408)
        |                                                        reads [P]; checks the anchor's
 [1]  evaluate_member(C)            (:2799, no gate)             own fields; NO gate on C
        |                                                         |
 [2]  cooldown_reference_eligibility (:3933)               [7] campaign_cooldown_before_member
        reads idle window, environment, policy;                 (:4105; called :8798, :7612)
        reads NO battery status                                 reference = anchor baseline 9.99 W
        |                                                         |
 [3]  _first_eligible_cooldown_anchor (:4012;              [8] cooldown note: result, and
        called :8900, :7817)                                    anchor_provenance (9.99 W inside)
        |                                                         |
 [4]  write_campaign_provenance     (:8908-8911)           [9] evaluate_member(member of N,
        |                                                        cooldown_evidence = note)
 [P]  runs/campaign_manifests/<session N-1>.json                  |
        holds cooldown_anchor {bundle_id C, 9.99 W} ----->  [10] _member_readiness_reasons (:6649)
        |                                                        result cap_hit -> reason
 [5]  GATE of N-1 (:9032) raises on C.                           cooldown_cap_hit; recovered -> none
      N-1's window is refused.                                    |
      [P] stays on disk unchanged (E6).                     [G]  GATE of N (:9032): N's members only.
                                                                 C is not one of them.
                                                            [V]  member verdict row of N: carries
                                                                 the note, 9.99 W inside (:522)
```

- **[B]** is the source bundle. **[P]** is campaign N-1's provenance file. **[5]** and **[G]** are the two campaigns' gate calls. **[V]** is the claim artifact the value arrives in.
- **[1]** to **[4]** run inside campaign N-1, before **[5]**. **[6]** to **[10]** run inside campaign N.
- The arrow from **[P]** to **[6]** is the only link between the two campaigns. It is a file on disk.
- A campaign reuses an anchor when the stored `analysis_manifest_id` equals its own and the anchor's policy digest equals its own (`:4058-4070`). If the campaign has no analysis manifest id, the first test is skipped, and any stored anchor with the same policy digest is taken (`:4060-4064`, read).

### 4.3 Worked example (executed, E1 to E3)

Bundle `C` is charging and its summary says the machine idled at 9.99 W. During the cooldown in campaign N the meter reads 5.0 W.

| Anchor that campaign N holds | Release threshold (reference × 1.1) | Result | Waited | Admission reason on the next member |
|---|---|---|---|---|
| from `C`, 9.99 W (the tree's behaviour) | 10.989 W | `recovered` | 30 s | none |
| the same anchor holding 0.2 W | 0.22 W | `cap_hit` | 300 s | `cooldown_cap_hit` |
| none | none | `unknown` | none | `campaign_cooldown_evidence_missing` |

The value from the unchecked bundle decides whether the next member is excluded. With the value from `C`, a machine that reads 5.0 W is declared cooled down and the member is admitted with no reason attached. The member's verdict row holds `anchor_provenance.baseline.power_w_mean = 9.99` and `bundle_id = C`.

**So the refuter's F1 is true**, in each link it names. Its reading of the collection-time use is also right: the consumers form was defined "for a function that runs during collection and whose result is used **only later**", and on the tree the result is used during collection at seven call names (E11).

### 4.4 Pre-existing, or introduced by S1?

**Pre-existing.** Three executed facts:
1. The probe gives the same output on main (E4).
2. S1 changes no line of the route (E5).
3. The route exists at base, which holds no gate at all (E5).

S1 neither opened the route nor widened it. S1's fix round 3 did remove a gate call from `evaluate_member` (the ruling under review, Z2), but that call was S1's own earlier addition: main never had it (E5: 0 gate calls in main's campaign script).

### 4.5 Does it block S1's merge?

**No.** The reasons, in the order they weigh:

1. **The merge does not create the hazard, and refusing the merge does not remove it.** Main carries the same route today with fewer gates around it. Holding S1 back leaves the repository in the less protected of the two states.
2. **The hazard arises when a campaign runs, not when a branch merges.** The constraint therefore belongs on campaigns. It is stated in §4.6 and it is binding.
3. **The fix is production code in the campaign script's cooldown path and, probably, in the anchor's record format** (§4.7). That deserves its own review. The ruling under review made the same call for its reader change, for the same reason.

As written, A3 of the stop rule would count F1 as a failure that blocks the merge. A3 is amended so that it says what is meant (66 (b)).

**What keeps this from becoming a way to wave findings through:** the pre-existing branch of the route needs three executed things (66 (a), row 1c), and it always comes with a lane that has an order. A finding on a route that S1 changed gets no such treatment.

### 4.6 The order, and the pre-check until the lane merges

1. **S1 merges first**, when A1 to A5 hold. Lane BFGS-COOLDOWN-ANCHOR-01 opens at once. It does not wait for S1's merge to be briefed.
2. **The lane merges before the next scored campaign starts.**
3. **If a scored campaign must start before the lane has merged,** the lead first runs the pre-check below on that campaign's runs directory and records its output in the campaign's trace. The campaign starts only if the exit code is 0. This holds for **every** scored campaign until the lane merges, because each campaign can store a new anchor that the next one reads.
4. A campaign that is not scored needs no pre-check.

The pre-check, exact (executed on the probe's data, E12: it refuses the anchor from `C`):

```python
"""Run the battery gate on the source bundle of every stored cooldown anchor.
Read-only. Exit 0 only if every anchor's source bundle is found once and passes.
Usage: python3 -B anchor_precheck.py <repo_root> <runs_dir>"""
import json, sys
from pathlib import Path
repo, runs = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(repo))
from joulewise.bundle_read import authenticate_window_members
bad = 0
manifests = sorted((runs / "campaign_manifests").glob("*.json"))
for manifest in manifests:
    anchor = json.loads(manifest.read_text()).get("cooldown_anchor")
    if not isinstance(anchor, dict):
        print(f"{manifest.name}: no anchor"); continue
    bundle_id = anchor.get("bundle_id")
    found = [p for p in runs.rglob(str(bundle_id)) if (p / "metadata.json").is_file()]
    if len(found) != 1:
        print(f"{manifest.name}: anchor {bundle_id}: source bundle found {len(found)} times: REFUSE"); bad += 1; continue
    try:
        authenticate_window_members(((str(bundle_id), found[0]),))
    except Exception as exc:
        print(f"{manifest.name}: anchor {bundle_id}: {type(exc).__name__}: {exc}: REFUSE"); bad += 1; continue
    summary = json.loads((found[0] / "summary_metrics.json").read_text())
    same = summary.get("idle_baseline") == anchor.get("baseline")
    print(f"{manifest.name}: anchor {bundle_id}: gate passed; baseline equals the bundle's: {same}")
    bad += 0 if same else 1
print("manifests:", len(manifests), "anchors refused:", bad)
sys.exit(1 if bad else 0)
```

It is a command the lead runs. It is not repository code and it is not the fix. It needs the gate, so it runs on a tree that holds S1. Its limits: it has been run on the probe's data only, NOT on a real runs directory; it checks every stored anchor and not only those the campaign would select, which errs toward refusing.

### 4.7 Lane BFGS-COOLDOWN-ANCHOR-01: what it must achieve

The lane gets its own cold gate, because it changes production code that no ruling covers. I rule what must hold when it is done, and the rows that show it. I do not rule the code.

**Requirements.**

1. **At freezing.** No anchor is stored from a member unless the gate has run on that member's bundle and returned. The gate call comes **before** the eligibility check, because choosing the anchor is a decision to exclude the members not chosen.
2. **At reuse.** No anchor read from an earlier campaign's provenance is used as a cooldown reference, handed to a child run, or copied into the new campaign's provenance, unless in this process (i) the gate has run on the anchor's source bundle and returned, and (ii) the anchor's `baseline` equals the `idle_baseline` in that bundle's `summary_metrics.json`. Requirement 2 is the one that closes the route for anchors already on disk.
3. **When the source bundle cannot be found, or the gate refuses it,** the anchor is not used. The campaign then behaves as it does today with no stored anchor: it stores its own from its first member that passes. The refusal is written to the campaign's provenance with its status and reasons.
4. **A custody failure stays an exception.** It is never turned into "anchor not usable".
5. `scripts/run_campaign.py` already imports `authenticate_window_members` from `joulewise/bundle_read.py` (`:68`). The lane adds no import of `battery_float` to any of the eight consumers and edits no frozen file.
6. **The lane's inventory.** Before it writes code, the lane lists every reader of a stored anchor and of a stored cooldown note, and shows for each that it is gated or that no energy-class value passes through it. Three candidates I read and did not trace (NOT EXECUTED):
   - `prior_campaign_cooldown_evidence` (`:3725`, called at `:8345`): it reads earlier campaigns' cooldown notes. A note holds the reference power that was used, which may come from a bundle that is not a member of the new campaign.
   - `command_for` (`:1543`, called at `:8569`): it hands the anchor to the child run on the command line when a configuration has more than one repetition.
   - the skipped manifest-id test of §4.2.

**Left to the lane's cold gate:** whether a battery refusal at freezing ends collection at once (the window will be refused at the end in any case); where the anchor records its bundle's location; whether the anchor's format version changes.

**Rows the lane must show** (RED on `315364b2`, GREEN after the lane):

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| RCA-1 | `_first_eligible_cooldown_anchor`, called at `run_campaign.py:8900` and `:7817` | the evaluation of charging bundle `C` of E1 (idle baseline 9.99 W, eligibility fields present) | no anchor is stored from `C` | the tree at `315364b2`: an anchor with `bundle_id C` and 9.99 W (**executed RED, E1**) |
| RCA-2 | `prior_campaign_cooldown_anchor`, called at `:8350` and `:7408` | a runs directory whose provenance holds the anchor of `C`, written by the production writer under the campaign lock (E2) | the anchor of `C` is not returned | the tree: returns `('C', 9.99)` (**executed RED, E2**) |
| RCA-3 | `campaign_cooldown_before_member` (`:8798`, `:7612`), then `_member_readiness_reasons` (`:6649`) | the inputs of E3 (a): the run before is not eligible, the meter reads 5.0 W, the stored anchor is that of `C` | the result is not `recovered`; the member's row holds no value from `C` | the tree: `recovered`, reasons `[]`, the row holds 9.99 W (**executed RED, E3**) |
| RCA-4 | the same two functions as RCA-2 and RCA-3 | the same, with a passing bundle `P` (both battery readings from `float.ioreg`) in place of `C` | the anchor of `P` is returned and used; the result follows `P`'s baseline | a fix that refuses every stored anchor |
| RCA-5 | `prior_campaign_cooldown_anchor` | the anchor of `P`, after one byte of `P`'s `raw/battery_float.pre.ioreg` is changed | `CustodyFailure` leaves the function as an exception | a handler that turns it into "anchor not usable" |
| RCA-6 | `prior_campaign_cooldown_anchor` | the anchor of `P`, after `P`'s `summary_metrics.json` is rewritten with another `idle_baseline` | the anchor is not used | a fix that runs the gate and does not compare the value |

RCA-4 to RCA-6 are NOT EXECUTED by me: they test code that does not exist yet.

### Amendment 66 (amends 61 (c), A3, 51 (f), 64 (b); names the lane)

66. **A tree finding whose fix is production code that no ruling covers has a route; the consumers form says what is true.**

**(a) In 61 (c), the first row of the table "What its findings do" is replaced by these three rows:**

| The refuter or the seat finds | What happens | Another refuter pass? |
|---|---|---|
| **1a.** a failure of A1, A2, A4 or A5; or a failure of A3 whose fix is a change ruled in §5 of the SAMESIG ruling or in this erratum | the seat fixes it; the lead re-runs the affected rows | no |
| **1b.** a failure of A3 whose fix is production code that no ruling covers, on a route that **S1 introduced or changed** | the seat does not fix it. It returns it under step 11. A cold gate rules the fix as an amendment inside S1. **It blocks S1's merge.** | yes: one pass, on the fix only |
| **1c.** the same, on a **pre-existing route** | the seat does not fix it. It returns it under step 11. The lead opens a lane with its own cold gate, and names the lane and its order in the description of S1's merge. **It does not block S1's merge.** | not for S1 |

A route is **pre-existing** only if the return shows all three, each executed: (i) a probe that drives the route and prints the value arriving at the claim artifact; (ii) the same probe, unchanged, giving the same output on main; (iii) `git diff <main> <merge candidate>` holding no changed line in any function on the route. If one is missing, row 1b applies.

Every lane opened under 1c states **an order against the artifact at risk**: the event before which it must merge, and the check that stands in until then.

**(b) A3 is replaced by:** "**A3, the tree.** The same refuter pass finds no energy-class value that reaches a claim artifact without a gate, on the routes through the eight consumers and through the envelope gate, other than by a pre-existing route returned under row 1c of 61 (c)."

**(c) In 51 (f), the consumers form is replaced by:**

> **Consumers form**, for a function that runs during collection, before the window's members are all known, and hands on content it read from a bundle. Its result is used in two ways, and the row names both.
> - **For a verdict.** Third field `consumers`: a tuple of (`path::qualified function`, name of the consuming call). The sweep asserts that in each named function a gate call comes before and dominates **every** call of the named consuming function.
> - **During collection, before the gate.** Fourth field `collection_uses`: a tuple of (`path::qualified function`, name of the call that receives the result). The sweep asserts that the field is present and is not empty. The refuter checks by reading that the list is complete, and that each use writes only to the campaign's own log, provenance and cooldown notes.
> - Fifth field `producers`: see amendment 67.
>
> A collection use that stores an energy-class value where **another campaign, or a verdict, reads it** is a tree finding under A3.

**(d) The three rows of 64 (b) gain the fourth field.** By my scan (E11, by name; the seat recomputes and returns any difference):

```python
collection_uses = (
    ("scripts/run_campaign.py::run_campaign", "campaign_cooldown_before_member"),
    ("scripts/run_campaign.py::run_campaign", "_first_eligible_cooldown_anchor"),
    ("scripts/run_campaign.py::run_campaign", "record_campaign_member_provenance"),
    ("scripts/run_campaign.py::run_campaign", "evaluation_failure_detail"),
    ("scripts/run_campaign.py::run_campaign", "to_log"),
    ("scripts/run_campaign.py::run_axi_spec_campaign", "campaign_cooldown_before_member"),
    ("scripts/run_campaign.py::run_axi_spec_campaign", "_first_eligible_cooldown_anchor"),
    ("scripts/run_campaign.py::run_axi_spec_campaign", "record_campaign_member_provenance"),
)
```

`_first_eligible_cooldown_anchor` is the one that fails the last sentence of (c). It is F1, routed under row 1c, lane BFGS-COOLDOWN-ANCHOR-01. The rows stay `behind_gate`: their condition, as corrected, is about the verdict uses, and those are gated (the ruling under review, Z9).

**(e) 51 (h) gains the item:** "**A value that a campaign stores for the next one.** The cooldown anchor in a campaign's provenance holds the idle power of a bundle that the later campaign's gate never sees (executed, SAMESIG erratum E1 to E3). The sweep reads source text and does not follow a value through a file. Lane BFGS-COOLDOWN-ANCHOR-01."

**Test row for amendment 66.**

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R51-17e | the three allowlist rows of `scripts/run_campaign.py::evaluate_member` | (i) the allowlist; (ii) the allowlist with `collection_uses` removed from one of the three rows | (i) passes; (ii) fails, naming the row | a consumers form with no fourth field, which is the form as first ruled: it states "used only later" and nothing checks it |

---

## 5. F2: the consumers form has no closure over its callers. UPHELD, text changed

**The forcing problem.** The row for `evaluate_member` is safe because each function that uses its result for a verdict runs a gate first. The sweep checks the uses that the row names. If someone writes a new function that calls `evaluate_member` and uses `.summary`, nothing names it, so nothing checks it, and the sweep stays GREEN. That is an ordinary refactor, not an evasion.

**Why the refuter's text is changed.** It asks the sweep to follow "any function … that returns its result". A test that reads source text cannot decide what a function returns. The relation becomes a list that a person writes and the refuter checks. The sweep then checks names, which it can do.

### Amendment 67 (adds to 51 (f), consumers form; adds to 64 (b))

67. **Every call of a consumers-form function lies in a listed function.**

**(a) The consumers form gains:** "Fifth field `producers`: a tuple of function names. It holds the row's own function, and every function under the swept roots that returns the row's function's result or a collection of such results. The sweep asserts that every call of a name in `producers`, and every reference to one (62 (b)), in any tracked file under the swept roots, lies either in a function named in `producers`, or in a function that is the first element of an entry of `consumers`. The refuter checks by reading that `producers` is complete."

**(b) The three rows of 64 (b) gain:** `producers = ("evaluate_member", "evaluate_members")`.

**Test rows for amendment 67.** Each new source is given to the sweep as file `scripts/zz_new.py`.

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R51-17b | the 6 calls of `evaluate_member` (`run_campaign.py:2924`, `:7517`, `:7759`, `:7789`, `:8034`, `:8709`) | `def f(p, i): return evaluate_member(p, info=i, waivers={}).summary` | the sweep fails, naming `scripts/zz_new.py::f` | 64 (b) as ruled, which checks the named consuming calls and nothing else. NOT EXECUTED as a mutation. |
| R51-17c | the 2 calls of `evaluate_members` (`:8587`, `:8880`) | `def g(): h = evaluate_members; return h` | the sweep fails, naming `scripts/zz_new.py::g` | a check that counts calls and not references; a `producers` field that holds the row's own function only |
| R51-17d | all 8 calls | the tree | passes: each call lies in `evaluate_members`, `run_campaign` or `run_axi_spec_campaign`; references `[]` (**executed, E7**) | a check that does not count `evaluate_members` as a listed function, under which the call at `:2924` fails on the tree |

---

## 6. F3: the file scope. UPHELD in part

**The forcing problem.** The promise covers `joulewise/` and `scripts/`. The scripts that make the paper's figures and worked examples live in `docs/paper/`. A future figure script that reads new bundles is the most natural place for an accidental ungated read, and a figure is a claim artifact.

**What widening costs (executed, E9, E10).** Two rows, both in one file. The 21 files under `configs/` add none.

**The two rows need no `historical` grant.** `historical` is the class for a function that reads energy values of old bundles. I read the two sites:
- **Line 113, function `historical`.** The file's bytes are hashed and compared (`:114`) with a digest held in the committed file `docs/process_traces/2026-08-09-prefill-phase-proof/results.json`. From the rows, two columns are taken: `interval_start_s` and `interval_end_s` (`:116`). They are times. No power column is read.
- **Line 47, function `synthetic`.** The loop hashes four files of a fixture bundle under `tests/fixtures/` into a dictionary of fingerprints. No field is parsed.

Both meet `non_claim`, clause (i): no field read from the file at the site is an energy-class value. Clause (i) is read here per row, as it already is for `make_figures.py::gate_inputs` ("field read: `status`", amendment 60 (b)).

**What is not widened, and why.** The function `historical` also reads a raw capture at line 79 (`raw/powermetrics.plist`), from a directory of an instrument-validation capture, which is not a bundle. If the raw-capture inventory (amendment 58 (f)) widened, that function would become a member of kind `energy` with no gate, and by the ruling under review a merge blocker. Neither form of the gate applies to a directory that is not a bundle, and the table of kinds has no kind for it. That question is not before me and must not reach S1's merge by a side door. So the inventories keep their scope, and the promise names this function.

### Amendment 68 (amends 51 (0), 51 (b) 2, 51 (f), 60 (c) 2, 62 (b); grants two rows)

68. **The swept roots, closed; two rows under `docs/paper/`.**

**(a) In 51 (0), "Promised",** the words "for every tracked Python file under `joulewise/` and `scripts/`" become: "for every tracked Python file under the **swept roots**: `joulewise/`, `scripts/`, `docs/paper/`, `configs/`. Item 3, the five closed lists, holds under `joulewise/` and `scripts/` only."

**(b) In 51 (0), "Not promised", item 4 is replaced by:**

> 4. Anything about code outside the swept roots: tracked Python under `tests/`, `docs/process_traces/` and `docs/legacy/`; a notebook; a shell command. And, under `docs/paper/` and `configs/`, anything about the stage journal or the raw capture. One function there reads a raw capture at the commit of this text: `docs/paper/figures/reproduce_worked_examples.py::historical`, which reads `raw/powermetrics.plist` of a capture directory that is not a bundle.

**(c) The scope is closed.** The sweep asserts that every tracked file whose name ends in `.py` lies under a swept root or under one of the three directories named in item 4. A file elsewhere makes the sweep fail, naming the file.

**(d)** In 51 (b) 2, in both forms of `behind_gate` (51 (f)), in 60 (c) 2, in 62 (b) and in 67 (a), "any tracked file under `joulewise/` or `scripts/`" becomes "any tracked file under the swept roots".

**(e) Two rows, granted by this gate.**

| Key | Class | Reason (exact) |
|---|---|---|
| `("docs/paper/figures/reproduce_worked_examples.py", "historical", "direct:read_bytes", "power_trace.csv")` | `non_claim` (i) | "fields read: `interval_start_s`, `interval_end_s`; the bytes are hashed and compared with the digest in `docs/process_traces/2026-08-09-prefill-phase-proof/results.json`" |
| `("docs/paper/figures/reproduce_worked_examples.py", "synthetic", "direct:read_bytes", "power_trace.csv")` | `non_claim` (i) | "fields read: none; the bytes are hashed into `fixture_fingerprints`" |

The loop at `:46` names four files, three of them watched. The prototype reports one row for it. If the seat's detector reports a row for `metadata.json` or for `summary_metrics.json` at the same site, each takes the class and the reason of the second row. Any other row under `docs/paper/` or `configs/` is returned to the lead.

**(f) The count.** Step 3 of §8.2 expects 118 rows. After this amendment it expects **120** by the prototype (118 and these 2), or up to 122 under (e).

**Test rows for amendment 68.**

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R61-1 | the sweep's list of files | (i) the tree; (ii) the tree's file list with `tools/zz_new.py` added | (i) passes (**executed by count, E10**: every tracked `.py` lies under a root or a named directory); (ii) fails, naming `tools/zz_new.py` | a sweep that reads a fixed list of roots and does not look at what is left over |
| R61-2 | `docs/paper/figures/reproduce_worked_examples.py:47`, `:113` | a file `docs/paper/figures/zz_new.py` holding `def fig(b): return json.loads((b / "summary_metrics.json").read_text())["gross_energy_j"]` | the sweep fails, naming `docs/paper/figures/zz_new.py::fig` | the scope as ruled in 61 (a), under which the file is not read (**executed on the prototype for the two existing rows, E9**) |

---

## 7. F4: no row pins "a read inside a lambda is never gated". UPHELD

The ruling under review says (62 (a)) that a read inside a `lambda` is never gated and that no scope inherits a gate from another. Its rows R51-23 to R51-26 use sources that hold no gate at all. A detector that lets a `lambda`, or a nested function, inherit the gate of the function around it passes all of them. The rule has no row that fails when it is broken.

### Amendment 69 (adds two rows to amendment 62)

69. Each source is given to the sweep as file `scripts/zz_new.py`.

| Row | Production site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R51-23b | every tolerant accessor call in the tree (100 watched call sites, the ruling under review, Z5) | `def f(r: BundleReader):` with the body `r.metadata()`, then `g = lambda: r.raw_summary()`, then `return g()` | reported in `f`, operation `raw_summary` | a detector in which the body of a `lambda` inherits the gate of the scope that holds it. NOT EXECUTED as a mutation. |
| R51-23c | the same | `def f(r: BundleReader):` with the body `r.metadata()`, then `if os.environ.get("X"):` holding `def inner(): return r.raw_summary()`, then `return inner` | reported in `f.inner` | a detector in which a nested `def` inherits the gate of the function around it. NOT EXECUTED as a mutation. |

Both are GREEN on the tree in this sense: the ruling under review found no read site inside a `lambda` and no row added by visiting every scope (its Z5).

---

## 8. F5: clause 1 of the deliberate class counts plain reads. UPHELD

Clause 1 of 61 (b) puts any code that **reads** a `_`-prefixed attribute of a `joulewise` object, from outside its module, into the deliberate class, which is never a finding. Such reads are routine in this tree: 89 imports of private names in 32 files (E8). One of them is a read of a bundle file: `BundleReader(bundle)._strict_json("metadata.json")` at `scripts/build_battery_float_historical_bundles.py:245`. Under clause 1 as ruled, a copy of that line that reads `summary_metrics.json` would count as deliberate, though it is ordinary code copied from the tree. The class is defined as code that reaches into the gate's machinery. Reading through a private helper does not do that. Writing the reader's storage does.

### Amendment 70 (replaces clause 1 of 61 (b))

70. **Clause 1 of 61 (b) is replaced by:**

> 1. writes or deletes an attribute whose name begins with `_`, or reads `_cache`, `_path` or a name-mangled attribute (`_<Class>__<name>`), on an object whose class or module is defined under `joulewise/`, from outside the module that defines it (`r._path = b`; `r._cache.update(…)`; `r._BundleReader__root`). A **call** of a private function or method is not in the class. Where it reads a watched file it is a supported form and the sweep reports it (51 (b) 2).

No row moves: the tree holds no use of `._cache` or `._path` outside `self` (E8), and the prototype already reports the call at `:245` (E8). No new rule is added for the class.

---

## 9. F6: three wordings. UPHELD

### Amendment 71 (amends 64 (a), row R51-28, row R60-7)

71. **(a) In rule (d) 6 (amendment 64 (a)),** "is bound by nothing else anywhere in the function" becomes "is bound by nothing else anywhere in the function, **nested scopes included**: a `nonlocal` or `global` statement for `<P>` in a nested `def`, followed by any binding of `<P>` there, counts". Reason: a nested function that declares the name `nonlocal` and assigns it changes what the second `if` tests.

**(b) Row R51-28 gains input (e):** "the tree with a nested function added to `run_axi_spec_campaign` between the two `if`s, `def _reset():` holding `nonlocal policy_binding` and `policy_binding = None`, and a call of it". Expected: the rows of 64 (b) fail. Counterfactual: a rule 6 that looks for bindings in the function's own body only. On the tree the function holds no nested definition (the ruling under review, Z10), so input (d) stays GREEN.

**(c) Row R60-7 gains:** "If the commit `315364b2` is absent from the repository the test runs in (`git cat-file -e 315364b2^{commit}` fails), the row calls `skipTest` with the message `R60-7: commit 315364b2 absent`. The seat's report and the lead's re-run show the row **executed and passing**, not skipped, at the merge candidate." Reason: the row proves that the edit of amendment 63 changed no output. That proof is made once, where the history is present. A skipped row in a shallow clone loses nothing. A row that errors there breaks the suite for a reason that has nothing to do with the code.

**(d) The route for 61 (c)** is amendment 66 (a).

---

## 10. The complete delta to §8.2

The seat finishes steps 1 to 12 as written, then applies steps 13 to 19. **No production file is edited in this delta.** WRITE_SCOPE for the delta: the test files that fix round 3's WRITE_SCOPE already holds (the sweep, and the file that holds row R60-7). If applying a step seems to need any other file, the seat returns it.

| Step | What | Rows to show RED under the counterfactual, then GREEN |
|---|---|---|
| 13 | **The swept roots** (68 (a) to (d)): the read-site sweep and every caller check read `joulewise/`, `scripts/`, `docs/paper/`, `configs/`. The five closed lists keep `joulewise/` and `scripts/`. The closure check of 68 (c). | R61-1, R61-2 |
| 14 | **The two rows under `docs/paper/`** (68 (e)), classes and reasons as written. **The count** becomes 120 (68 (f)); a different count is returned with the differing rows listed. | R51-27 re-run with the new count |
| 15 | **The consumers form** (66 (c), 66 (d), 67): the three `evaluate_member` rows gain `collection_uses` and `producers`. The seat recomputes `collection_uses` and returns any difference from 66 (d). | R51-17b, R51-17c, R51-17d, R51-17e; R51-17 (restated) re-run |
| 16 | **Lambda and nested scopes under a gate** (69). | R51-23b, R51-23c |
| 17 | **Rule (d) 6 wording** (71 (a), (b)); **R60-7's skip clause** (71 (c)). | R51-28 with input (e); R60-7 executed, not skipped |
| 18 | **Texts.** In the sweep's module docstring: 51 (0) with 68 (a) and (b); 61 (b) with clause 1 as replaced by 70; 61 (c) with the three rows of 66 (a) and A3 as replaced by 66 (b). In the list the test holds for 51 (h): the item of 66 (e). | none: text |
| 19 | **Returns, and the suites again.** Under step 11 the seat returns F1's route with its executed evidence (it was already told to). V1, V2, the builder's forward check and the three fences of A5 are run again after step 18. | |

**Not applied by the seat:** lane BFGS-COOLDOWN-ANCHOR-01 (§4.7); the pre-check of §4.6, which the lead runs.

**Lanes, added to §11 of the ruling under review:**

| Lane | What it does | Order | Blocks S1? |
|---|---|---|---|
| **BFGS-COOLDOWN-ANCHOR-01** (new) | the gate runs on a cooldown anchor's source bundle when the anchor is stored and when it is reused (§4.7) | opens now; merges **before the next scored campaign starts**; until then the pre-check of §4.6 before every scored campaign | no |
| BFGS-RAWCAPTURE-01 (carried) | gains one item: whether the raw-capture inventory widens to `docs/paper/`, and what kind `reproduce_worked_examples.py::historical` takes | unchanged | no |

**Blocks S1's merge, restated with this erratum:** everything the ruling under review lists, and any failure of rows added here. **Does not block it:** F1, under row 1c.

---

## 11. Kept intact

- **Custody is never a status.** No amendment here adds a status, a handler or a conversion. Requirement 4 of §4.7 and row RCA-5 carry the rule into the new lane. The pre-check of §4.6 treats a custody failure as a reason not to start. It converts nothing, and it is not repository code.
- **Authentication precedes every exclusion decision.** F1 is a place on main and on S1 where this does **not** hold today: the anchor's eligibility check, and through the anchor an admission reason, are decided on a bundle no gate has seen (executed, E1 to E3). No amendment here reorders production code. Requirement 1 of §4.7 puts the gate before the eligibility check. Until the lane merges, §4.6 stands in.
- **`joulewise/battery_float.py` and FT §E's excluded list stay byte-identical.** This erratum changes no production file. The lane's likely files (`scripts/run_campaign.py`, `joulewise/cooldown_anchor.py`) are not among the 15 protected paths of the repository's pin test as the ruling under review lists them (its Z16). I did not open the pin test or FT §E. If the lead finds either file on that text's list, the lane's change is returned to a cold gate before it is made.
- **The eight consumers do not import `battery_float`.** Nothing here adds an import. The lane uses `authenticate_window_members`, which `scripts/run_campaign.py` imports from `joulewise/bundle_read.py` at `:68`.

---

## 12. Not executed

- `run_campaign()` from its command line through two whole campaigns. E1 to E4 call its functions in its order.
- A real meter in the cooldown. E3 uses a fake that reads 5.0 W.
- The pre-check of §4.6 on a real runs directory.
- Rows RCA-4, RCA-5, RCA-6; R51-17b and R51-17c as mutations; R51-23b and R51-23c; R51-28 input (e); R61-1 input (ii) and R61-2 on the repository's sweep. The repository's sweep does not implement amendment 51 yet.
- The three candidates of §4.7, requirement 6.
- Whether `docs/paper/figures/reproduce_worked_examples.py` still runs to the end on a tree that holds S1. Its line 48 calls a gated accessor on fixture bundles. I did not run the script.
- The five writes to `_`-prefixed attributes of E8: I did not read the five sites. They hold no `_cache` or `_path`.
- The repository's test suites, V1, V2 and the builder's forward check. I ran no test module.
- The refuter's `q1_dominance.py`. I did not re-run it. The ruling under review executed the same fact (its Z9).

---

## 13. Probes written in this session (`/tmp/cg_samesig_err/`; SHA-256 prefix)

| File | Prefix | What it is |
|---|---|---|
| `f1_probe.py` | `186e2a466569e861` | E1 to E4: the route of §4.2, step by step, on a tree given as its first argument |
| `f2_scan.py` | `83745a240201abce` | E7, E8: calls and references of the two producers; private names |
| `anchor_precheck.py` | `e97ba58dae31876c` | E12: the pre-check of §4.6 |
| `main_tree/` | | `git archive 97082508`, the tree E4 ran on |

E5, E6, E9, E10 and E11 were run as commands typed into the shell. E9 uses the first judge's `/tmp/cg_sw_erratum/sweep59.py`, unchanged. Files under `/tmp` are not durable. The pre-check is given in full in §4.6, and the probe of E1 to E3 is described by its inputs and its calls so that it can be rebuilt.

---

## 14. Plain summary for Ed (5 lines)

1. The reviewer's main finding (F1) is real. I ran it: a measured run whose battery was charging, and which the battery check refuses, still had its idle power (9.99 W in my test) stored by the campaign script as the "cooldown anchor", the reference a campaign uses to decide that the machine has cooled down between runs. The next campaign read that stored value from disk and never checked the run it came from.
2. The value decides exclusions. With a meter reading 5.0 W, the anchor from the charging run gave "recovered" after 30 s and no objection to the next run. The same anchor holding 0.2 W gave "cap hit" after 300 s and the exclusion reason `cooldown_cap_hit`. The untrusted number is also copied into the next campaign's verdict record.
3. This is an old path, not one the current work package (S1, the battery-check wiring) opened: the same test gives the same output on the main branch, and S1 changes none of the lines involved. So it does not block S1's merge. It becomes its own task (BFGS-COOLDOWN-ANCHOR-01), which must merge before the next scored campaign starts. Until then a short read-only check, given in full in the ruling and run on my test data, must pass before every scored campaign.
4. The smaller findings are all upheld. The source-reading test (the "sweep") now also reads the paper's figure scripts, which adds two entries, both harmless (one reads only time columns, one only hashes files). It fails if Python appears in a directory it does not know. It fails if new code calls the campaign's bundle-reading function from an unlisted place. It gets two entries that catch a read hidden in a lambda or nested function.
5. Nothing in this ruling edits production code. The seat applies seven small steps (13 to 19) to test files after its current work. Not run by me: two whole campaigns end to end (I called the campaign script's functions in its order), a real meter, and the pre-check on real data.
