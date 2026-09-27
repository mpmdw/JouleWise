# Cold gate BFGS-S1-R2-01, erratum: ruling (Fable 5.1, cold judge) on the paired refuter's RB-1, RS-1 to RS-5 and RN-1 to RN-4

Candidate: working tree detached @ `49d77c74` (S1 round 2 plus fix round 2). Base `1417c0c4`.
Charge: `80-coldgate-r2/30-erratum/00-charge.md`, committed at `a24c2f7d`. Session: one foreground session, no subagents, no background tasks. No repository file edited; `git status --short` in the working tree was empty after the last probe (X10). Scratch: `/tmp/cg_r2e/`.

---

## 0. Contamination disclosure

The charge told me not to read `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAUDE*.md`, `AGENTS.md`, the decision log, or memory and skill files. I opened none of them. **The harness that started this session placed three of them in my context before the charge arrived:** the owner's global `CLAUDE.md` (a writing standard, and a pointer to orchestration doctrine), the project `CLAUDE.md` (notes on the bridge to a second model), and the index file `MEMORY.md` (about 110 one-line summaries of earlier sessions; several name this lane, pull-request numbers and standing directives of the owner). The harness also listed the names and one-line descriptions of the installed skills. I opened no file that any of those lines points to, and invoked no skill.

What this exposure could bias, and what I did about it:

- The index says that gates should be sensible on science grounds, that documentation work gets light gates, and that one model has the final say. I used none of these as authority. Every ruling below rests on the ruled texts in the packet, the code at `49d77c74`, and probes I ran.
- The index names the state of other lanes. None bears on the ten findings and none is cited.
- The global writing standard asks that every term be defined at first use. The charge asks the same of the summary for Ed. I followed it; it changes wording, not rulings.

I read, from the packet: the erratum charge, the original charge, the ruling under review in full, the refuter's report in full, and the `WRITE_SCOPE` and authority lines of the round-2 seat brief (to settle RS-2). I read the refuter's probes `/tmp/oc2/sweep_holes.py`, `/tmp/oc2/gate_try.py` and ran `/tmp/oc2/q2.py`. The first judge and I are the same model; that is a shared-blind-spot risk which the paired refuter, a different model, exists to offset, and on which I side with the refuter in every finding but one clause.

---

## 1. Terms used in this ruling

Each term is defined once and used in that sense only. Terms 1 to 8 are the first ruling's, repeated so this file stands alone.

- **Bundle.** The directory one measured run leaves behind. It holds `config.json` (what was asked), `metadata.json` (what ran), `summary_metrics.json` (the reduced numbers, energy included), `power_trace.csv` (the power samples) and `events.jsonl` (the stage log).
- **Battery pair.** Two readings of the laptop battery, one before the measured span and one after. If either shows current flowing into or out of the battery, the run's energy cannot be trusted.
- **Verdict.** The object the battery checker returns for one bundle. Its `status` is `pass`, `battery_float_confounded` (a reading shows charging or discharging), `battery_float_evidence_missing` (a reading is absent or unusable), `not_applicable` (a simulated run) or `unobserved_historical` (one of 69 listed runs measured before the check existed).
- **Custody failure.** The exception `CustodyFailure` and its subclass `CustodyUnreadable`: a file the evidence depends on is missing, unreadable, or does not hash to the digest that was recorded for it. It is never a status. It stops the whole computation.
- **The gate.** The function `bundle_read.authenticate_window_members(members)`. It takes a list of (label, bundle path), classifies every one, and either returns all verdicts or raises: `WindowBatteryRefusal` naming every member whose status refuses, or a custody failure labelled with the member it was found in.
- **Window.** One collection session: all the runs a campaign made under one runs directory and one campaign policy.
- **Consumer.** One of the eight modules that turn bundles into claimed numbers: `scripts/run_campaign.py`, `joulewise/whole_window.py`, `joulewise/analysis_engine/inputs.py`, `joulewise/floor_extraction.py`, `joulewise/aggregate.py`, `joulewise/window_duration_margins.py`, `scripts/mint_floor_artifact.py`, `scripts/extract_detection_floors.py`.
- **Supersession record.** A row of type `campaign_occurrence_supersession` in a window's campaign log (`campaign_log.jsonl`). The command `run_campaign --record-supersession` writes it when one bundle id was collected twice. It names the selected run, the superseded ones, and `quarantine.path`, the directory the superseded run's bundle was moved to, together with the SHA-256 of three of that bundle's files (`config.json`, `metadata.json`, `summary_metrics.json`). The **quarantined bundle** is the bundle at that path.
- **Resolver.** Code that works out which bundle stands for each bundle id of a window. For one id it returns `selected` (one bundle stands for it), `terminal_absent` (no directory for it exists), `unresolved` (collected twice, no record says which stands) or `ambiguous` (two copies present, or a record that fails validation).
- **Whole-window verdict row.** The row the command `run_campaign --whole-window-verdict` appends to the campaign log. Its `status` is `passed`, `flagged`, `failed` or `invalid`; its `idle_admission_core.conditions` is a list of strings, each naming one thing that stopped the window from passing. Later analysis refuses a window that has no `passed` row.
- **Production path.** The route real operation takes: the command functions (`run_record_supersession`, `run_whole_window_verdict`, `load_analysis_inputs`) called as the command line calls them, reading what earlier commands wrote. Its opposite here is a **hand-built resolution**: a test that constructs the resolver's output object itself and hands it to a helper.
- **Field-valid.** Said of a supersession record: everything that can be checked from the record's own fields and from the runs directory holds. Nothing about the quarantined bundle's bytes is consulted. Defined exactly in amendment 55 (a).
- **Finalization record.** A record that holds a SHA-256 of a bundle's own files. Such a digest can only have been computed from a bundle that existed, so the record proves the bundle was written. Defined exactly in amendment 56 (a).
- **The sweep.** The test `tests/test_bfgs_consumer_sweep.py`. It parses every tracked Python file under `joulewise/` and `scripts/` and lists every place that reads a bundle's files without the gate before it. Each listed place must have a named row in the test's **allowlist**.
- **Dominates.** Said of a gate call and a later read: execution cannot reach the read unless the gate call ran and returned normally.
- **Counterfactual.** For a test row: the specific wrong implementation under which the row must fail.

---

## 2. Executed evidence (this session, foreground, working tree `49d77c74`)

| Id | Probe | Result (exact) |
|---|---|---|
| X1 | `/tmp/cg_r2e/rb1_prod.py`. **Production path, no hand-built resolution.** The repository's own fixture (`IdleAdmissionCoreVerdictTests._retry_occurrence_fixture`) writes three bundles and the two campaign manifests; the real `run_record_supersession` writes the record; the real `run_whole_window_verdict` runs. Scenarios: S1 quarantine intact and passing; S2 quarantine intact with a charging pair; S3 quarantine directory deleted after the record was written; S4 one byte appended to the quarantined `summary_metrics.json`; S5 quarantine charging, then deleted. | S1, S2: `supersession_entry_validation_results -> 1 record(s), valid = [True]`; `quarantine path in gate list: False`; one row appended, `supersessions reported 1`, no condition about membership. **S3, S4, S5:** `valid = [False]`; `whole-window-verdict: returned exit code 1` (**nothing raised**); `quarantine path in gate list: False`; `rows appended by the verdict command: 1`; `status failed`; conditions include **`whole_window_campaign_membership_ambiguous`**; `supersessions reported 0`. |
| X2 | `rb1_prod.py norecord` (S6): the first run moved aside with a charging pair, **no** supersession record written, then the real verdict command | `0 record(s)`; one row appended, `status failed`, conditions include `whole_window_campaign_membership_unresolved` |
| X3 | `/tmp/cg_r2e/rs3_inputs.py upgrade`. **Production path**: the repository's integration corpus (30 real controller runs, real analysis manifest, real whole-window install), then the real `load_analysis_inputs`, first intact, then with one registered member's directory deleted | intact: `first gate call size: 30`; one deleted: `first gate call size: 29`. (Both then raise `WindowBatteryRefusal`, because the corpus is simulated runs.) |
| X4 | `rs3_inputs.py spy-pass`: the same, with the gate's refusal of simulated runs set aside so the function runs to its end | one deleted: `returned LoadedAnalysisInputs; nothing raised`; `any gate call containing the deleted member: False`; `deleted member -> excluded ('bundle_missing', 'whole_window_verdict_provenance_invalid') ('bundle directory is missing',)` |
| X5 | `/tmp/oc2/sweep_holes.py` (the refuter's), against the first judge's prototype detector `/tmp/cg_r2/sweep49.py`, whose SHA-256 prefix I checked is `8e0d3bcdde3214e2`, the value the first ruling records | `silent H1 gate swallowed by try/except Exception, read after` / `silent H2 gate under contextlib.suppress` / `silent H3 gate on a different member list than the read` / `silent H4 gate in try body, read in except handler` / `REPORTED H5 …` / `silent H6 BundleReader(a).metadata() then raw read of another bundle` |
| X6 | `/tmp/oc2/gate_try.py` in my tree; `git diff --stat 1417c0c4 HEAD -- joulewise/analysis_manifest_v3.py`; `git show 1417c0c4:joulewise/whole_window.py \| grep authenticate_window_members`; the class ancestry printed | `joulewise/analysis_manifest_v3.py:3712 handler ['KeyError', 'OSError', 'RuntimeError', 'TypeError', 'ValueError'] bare_reraise=False gate_line=3704 (_prepare)`; the file is identical to base; the gate does not occur in `whole_window.py` at base; `CustodyFailure ['RuntimeError', …]`, `WindowBatteryRefusal ['RuntimeError', …]` |
| X7 | `/tmp/cg_r2e/try_size.py`: every `try` in tracked `joulewise/` and `scripts/` whose body holds a gate call by name | 7 such `try` statements; 3 have a handler that does not end in `raise` (`calibration_bracketing.py`, `reduce.py`, `window_duration_margins.py:942`); 0 `with suppress(...)` bodies hold a gate call |
| X8 | `/tmp/oc2/q2.py` (the refuter's), fixture `_terminal_night(width=2, kind="ceiling_violation")` | `marker entries: Counter({('voided', 'cut_off'): 2, ('voided', 'completed'): 2, ('terminal', 'completed'): 2})`: **six** |
| X9 | `grep -rn claim_readiness joulewise/ scripts/`; `run_campaign.py:223-225` | the string occurs in `scripts/run_campaign.py` and in no other tracked file; `CLAIM_READINESS_NOTE = "This verdict checks analysis inputs only; P2-037 decides claim outcomes."` |
| X10 | `shasum joulewise/battery_float.py`; `git diff --quiet 1417c0c4 HEAD -- joulewise/battery_float.py`; an import grep over the eight consumers; `git ls-files \| grep -c historical_captures.json`; `build_battery_float_historical_bundles.py --check`; `git status --short` | prefix `4b4d7bb20625`, identical; no `battery_float` import line; `0`; `forward check: byte-identical entries=69`; empty status |
| X12 | an inline probe of path resolution on this machine: a runs directory under the default temporary directory; the path `<runs>/../runs/inside`; a quarantine path whose directory does not exist | `root /private/var/…/runs`; `abspath form /var/…/runs/inside` (**not** under the root); `resolve(False) /private/var/…/runs/inside \| inside runs: True`; `absent quarantine resolves without error … \| inside runs: False`; `strict=True on absent quarantine -> FileNotFoundError`. This probe corrected a first draft of amendment 55 (a) 3, which had named `os.path.abspath`. |
| X11 | `python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_recorded_supersession_resolves_present_retry_and_is_reported` | `ERROR`, `WindowBatteryRefusal … prospective bundle` for all three fixture bundles: the repository's one end-to-end supersession test cannot reach the verdict at `49d77c74`. This is the older-fixture debt that round F repairs. |

**What the probes changed, stated so their limits are plain.**

- X1, X2. The fixture's bundles carry no battery pair, so the gate refuses them before anything else can be seen (X11). The probe gives each fixture bundle, and the quarantined copy, a real battery pair built from the repository's fixture readings, and sets `metadata.config_sha256`; with that the **real** gate returns `pass` for each (printed per scenario). The gate is wrapped only to record its arguments; the wrapper calls the real gate. `validate_bundle` and the calibration bracket are patched exactly as the repository's own test patches them. The membership resolution, the record, the validation and the verdict row are untouched production code.
- X1's baseline verdict is `failed` in every scenario, S1 included, because the fixture bundles are not valid under strict validation (`bundle_strict_invalid`). So X1 does **not** show a window going from `passed` to `failed`. It shows what RB-1 claims: with the quarantined bytes gone or changed, nothing is raised, a row is written, and the only trace is one more condition string.
- X4 sets aside two things so that `load_analysis_inputs` can finish: the refusal `not_applicable`, and custody failures that name fixture stubs which are not registered members (the fixture's floor cells and reference runs have no `metadata.json`). A custody failure naming a registered member would still raise; none did. Every member ends `excluded` in both runs, because the fixture's whole-window verdict does not validate under these conditions. So whether the 29 remaining members would yield a number is **NOT EXECUTED**.

Read, not run (each is marked where used): `whole_window.py:2773-2843`, `:2978-3030`; `run_campaign.py:5435-5509`, `:5848-5958`, `:6197-6250`, `:6647-6660`, `:6786-6860`, `:7114-7135`, `:7666-7675`, `:8495-8515`, `:8926-8990`, `:2794-2815`, `:5961-5985`; `inputs.py:3120-3140`, `:2769-2787`, `:2380-2432`; `analysis_manifest_v3.py:3696-3716`, `:4478-4506`; `battery_float.py:55-85`; `bundle_read.py:278-327`.

---

## 3. Rulings at a glance

| Finding | Tier as reported | Ruling | Where the text changes |
|---|---|---|---|
| RB-1 | BLOCKER | **UPHELD**, as a blocker. Executed on the production path (X1). | amendment 49 (b) 4, (c), (d); new amendment 55; rows R49-3b, -3c, -3d, -7b, -8b |
| RS-1 | SHOULD-FIX | **UPHELD**, with one word of the proposed text rejected (`else`). | amendment 51 (d); rows R51-18 to R51-22 |
| RS-2 | SHOULD-FIX | **UPHELD.** It becomes its own lane; the file is not added to S1. | amendment 52 (g); row R52-6; §11 of the first ruling corrected |
| RS-3 | SHOULD-FIX | **UPHELD**, raised to a required item of fix round 3. Executed on the production path for `load_analysis_inputs` (X3, X4); not executed for `run_campaign`. | new amendment 56; amendments 49 (b) 3, 49 (e), 53 (b); rows R53-4, R56-1 to R56-5 |
| RS-4 | SHOULD-FIX | **UPHELD in part.** The premise sentence is wrong and is replaced. The proposed rule is **REJECTED** as unnecessary: the final analysis licenses nothing (X9), and a window with a re-done run and no record cannot pass (X2). Both facts get test rows. | amendment 49 (b), last paragraph; rows R49-10, R49-11 |
| RS-5 | SHOULD-FIX | **UPHELD.** | amendment 51 (c), (h); row R51-21 |
| RN-1 | NIT | **UPHELD.** Six, not five (X8). | amendment 50, row R50-8 |
| RN-2 | NIT | **UPHELD.** | amendment 49 (f) |
| RN-3 | NIT | **UPHELD.** | amendment 51 (f) |
| RN-4 | NIT | **UPHELD.** | amendment 53 (e); round F note |

Amendments 50 (apart from one count) and 54 stand as first ruled.

---

## 4. RB-1: custody of the quarantined bundle

### 4.1 The forcing problem

A supersession record says two things: "this run was superseded" and "its bundle is at this path and hashes to these three digests". The first ruling made the quarantined bundle a window member and said that its absence is a custody failure. But it admitted only records that pass `validate_occurrence_supersession_entry`, and that function (`whole_window.py:2817-2843`, read) returns `False` when the quarantine path does not exist or when any of the three digests fails to match. So the record stops being "valid" at exactly the moment the quarantined bytes go missing, and the member silently leaves the list.

### 4.2 Evidence

X1, scenario S3, step by step, all on production code:

1. The record command writes the record; validation reports `[True]`.
2. The quarantine directory is deleted.
3. Validation reports `[False]`.
4. The verdict command returns exit code 1. Nothing is raised.
5. The gate was never handed the quarantine path.
6. One verdict row is appended: `status failed`, with the condition `whole_window_campaign_membership_ambiguous`, and the supersession is no longer reported in the row.

S4 (one byte appended) and S5 (a charging first run, then deleted) give the same six facts. S5 is the case that matters physically: the evidence that the battery was charging during the window has been destroyed, and the system's answer is a condition string that says membership was "ambiguous".

No number is released: the row is `failed`. But the bytes that a record digest-binds are missing or changed, which is the definition of a custody failure, and the outcome is a status. "Custody is never a status" is broken on this path. The refuter's reading of the code was right in every step.

For `load_analysis_inputs` the refuter's reading is that the same invalid record gives the member the payload `{"result": "unknown", "verified": False, …}` (`inputs.py:2383-2432`, read). I confirm the reading. I did **not** execute it: it needs an analysis corpus whose campaign log holds a supersession, which no fixture I found builds. NOT EXECUTED.

### 4.3 Ruling

**UPHELD.** The remedy separates the two things the record says.

- Whether the record is a well-formed record of this window is decided from its own fields (**field-valid**, amendment 55 (a)). A record that fails this is a record problem, and the resolver's `ambiguous` stays the right answer for it.
- Whether the quarantined bytes are as recorded is custody. It is decided by the gate, which raises.

Two design choices, with reasons:

- **The existing validation functions are not changed.** `validate_occurrence_supersession_entry` and `supersession_entry_validation_results` are called by `scripts/check_window_provenance.py:955`, which is outside S1's WRITE_SCOPE, and by the record command. A new function is added beside them.
- **The digest comparison goes inside the gate**, not in the consumer. The refuter's text has "the resolver raises `CustodyFailure`". A consumer cannot construct that exception without importing `battery_float`, which the consumers must not do. `bundle_read.py` already imports it and already raises both custody classes.

R49-3 stays as a helper-level row. It is not the witness for this property; R49-3b is.

---

## 5. RS-1 and RS-5: what the sweep counts as gated

### 5.1 Evidence

X5: the first judge's own prototype is silent on H1 (the gate's exception caught and discarded, the read after it), H2 (the gate under `contextlib.suppress`), H4 (the read inside the handler, which runs exactly when the gate raised) and H6 (one reader authenticated, another reader read). X7: at `49d77c74` three `try` statements hold a gate call and have a handler that lets execution continue.

### 5.2 Ruling on RS-1

**UPHELD.** The first ruling said the body of a `try` and the body of a `with` "do not count as branches". That is true only when nothing can swallow the gate's exception.

I change the refuter's replacement text in two ways.

- **The test is on control flow, not on exception types.** The refuter's text asks whether a handler's caught types include an ancestor of the gate's exceptions. The sweep reads syntax and cannot resolve ancestry in general; and the second form of the gate, `BundleReader.metadata()`, raises `BundleReadError`, which that list would miss. The question the sweep must answer is simpler: *can execution reach the read without the gate having returned?* A handler whose last statement is `raise` cannot let execution continue past the `try`. Any other handler can. So the rule is: the body of a `try` counts as a branch unless every handler ends in `raise`. Whether a handler may *convert* the exception to another type is amendment 52's question, not the sweep's.
- **`else` is rejected from the refuter's list.** The `else` of a `try` runs only when the body finished without an exception, so a gate call in the body does dominate a read in the `else`. A read in a handler or in `finally` is never gated by a gate call in the body.

### 5.3 Ruling on RS-5

**UPHELD**, with the refuter's text, plus one clause: the reader's name must not be bound again between the gate and the read. The two bindings the sweep still cannot check (the gate's member list against the path that is read, H3; a reader's gate against a path read that does not go through the reader) are stated in amendment 51 (h).

---

## 6. RS-2: the ninth module

### 6.1 Evidence

X6. `joulewise/analysis_manifest_v3.py::_authenticate_finalization_inputs` calls `session._prepare(...)` at `:3704`. `_prepare` holds a gate call (`whole_window.py:679`), which S1 added: the gate does not occur in `whole_window.py` at base. The handler at `:3712` names `RuntimeError`, the parent class of both gate exceptions, and re-raises as `AnalysisManifestFinalizationError("analysis_finalization_attachment_invalid", …)`. `validate_finalized_analysis_manifest_v3` (`:4455`) reaches the same function (`:4379`) inside `try … except Exception` (`:4499`, read) and returns a `ManifestRefusal`. The file is byte-identical to base and is not in S1's WRITE_SCOPE (round-2 brief, line 3).

Both sites refuse. No number escapes. But a custody failure raised by the gate becomes a refusal code, and the first ruling's §11 sentence "Amendment 52 removes the one place found where a custody failure became a reason string" is not accurate.

### 6.2 Ruling

**UPHELD.** The charge offers two remedies: add the file to S1 by name, or register a lane. **I rule the lane.** Reasons:

1. Three handlers on the path need the change, not one (`:3712`, the handlers between `:4379` and the return of the unchecked validator, and `:4499`), and the public validator's contract is to **return** refusals. Letting custody raise through it changes what its callers receive. I have not read those callers. A ruling that changes a function's contract without reading its callers would be ruling blind.
2. S1's WRITE_SCOPE is the ruled list of Final texts v1.1 §E "exactly". Widening it at an erratum, for a module whose own tests are outside S1's verification set, is a larger act than the defect warrants while the defect fails closed.
3. The residual is named, tested for (row R52-6), and blocks first use.

Proposed lane name, for the lead to register: **BFGS-MANIFEST-CUSTODY-01**. Its contents are in §15.

---

## 7. RS-3: member lists that come from the disk

### 7.1 Evidence

X3 and X4, on the real `load_analysis_inputs`: with one registered member's directory deleted, the gate receives 29 members, not 30; no gate call anywhere in the function contains the deleted member; the function returns; the member is `excluded` with the reason `bundle_missing`. The first ruling's own probe E4 showed that the gate, had it been handed the path, raises `CustodyUnreadable`.

For `run_campaign`'s final analysis the filter is `if evaluation.bundle_path.is_dir()` (`:8931`, read). I could not execute it: a campaign of simulated runs aborts at the first member at `49d77c74`, and a campaign of real runs needs the battery probe. NOT EXECUTED.

### 7.2 Ruling

**UPHELD**, and raised from SHOULD-FIX to a required item of fix round 3, because it is the same defect as RB-1 seen from the other side: a bundle that was recorded, then deleted, leaves the evidence without a custody failure. A charging run deleted after the fact would be an exclusion.

`bundle_missing` is also the honest state of a run that was planned and never made. So the rule cannot be "pass every registered path to the gate": that would make every unfinished campaign a custody failure. The rule keys on the **finalization record**: a record holding a digest of the bundle's own bytes proves the bundle existed. Amendment 56.

What I verified and what I did not: I read two kinds of finalization record (the supersession record's three digests; the `member_occurrences` rows of a verdict row's evaluation basis, written by `_basis_member_occurrences`, `run_campaign.py:5961-5985`) and the attempt-ledger row, whose `run_id` is non-null only when the attempt finalized (`run_campaign.py:7668-7670`). I did **not** read how an attempt-ledger row maps to its bundle's path, nor the salvage-closure rules. Amendment 56 says where the seat must stop and return.

---

## 8. RS-4: the rerun's own final analysis

### 8.1 Evidence

The operator's workflow is printed by the code itself (`run_campaign.py:8509-8511`, read): quarantine the failed run, rerun, record the supersession. The rerun is a `run_campaign` invocation, and its final analysis gates the runs that invocation evaluated. The first run is by then outside the runs directory and no record exists yet. The refuter is right that the first ruling's sentence, "a supersession is recorded only after collection, by a separate command", does not dispose of this.

What the final analysis writes is a campaign verdict row holding a field `claim_readiness`. X9: that field is read by no tracked file other than `run_campaign.py` itself, and the note the row carries says "This verdict checks analysis inputs only; P2-037 decides claim outcomes" (P2-037 is the analysis engine, whose entry is `load_analysis_inputs`). The analysis engine refuses a window that has no passing whole-window verdict row. X2: with the first run moved aside and no record written, the whole-window verdict command writes `failed` with `whole_window_campaign_membership_unresolved`. With the record written, amendment 49 puts the quarantined bundle in front of the gate.

### 8.2 Ruling

**The finding is UPHELD; the proposed rule is REJECTED.**

The premise sentence is replaced (amendment 49 (b), last paragraph). The proposed rule, "the final analysis licenses no claim for a member id the log records more than once", would add a status to a function that licenses nothing. The protection already exists and sits in the right place: the only licence is the whole-window verdict, and it cannot pass with a re-done run unless the record exists, at which point the quarantined run is gated. What was missing is that neither fact was pinned by a test. Rows R49-10 and R49-11 pin them. If anyone later makes another module read `claim_readiness`, R49-11 fails and the question returns to a judge.

Amendment 56 does not stop the ruled workflow, which was the refuter's worry about its own RS-3 text: the final analysis keys on the evaluations of its own invocation, and the moved first run is not among them.

---

## 9. The NITs

- **RN-1. UPHELD.** X8 counts six markers on the row's own fixture. R50-8 is corrected.
- **RN-2. UPHELD.** One sentence is added to amendment 49 (f).
- **RN-3. UPHELD.** Clause (ii) of `non_claim` is a claim about where output goes. Its reason must now name the output, and the refuter checks each such row by searching for readers of that output.
- **RN-4. UPHELD.** The warning is added to amendment 53 (e) and to the round F step.

---

## 10. Amendments 49 to 56 as they stand (exact text; the fix-round brief quotes these)

Every test row names its production call site and the counterfactual under which it must fail. All new tests go in files already in S1's WRITE_SCOPE. **No path is added to S1's WRITE_SCOPE.** Text changed by this erratum is marked **[E]** at the start of the paragraph or row.

### Amendment 49 (amends text 12, the `members` sentence; S1's existing scope: `scripts/run_campaign.py`, `joulewise/whole_window.py`, `joulewise/analysis_engine/inputs.py`, `tests/test_bfgs_window_consumers.py`)

49. **Window members include every quarantined bundle, and two kinds of consumer are told apart.**

**(a) Two kinds.** A **window consumer** is a function that works out a window's membership itself, from the campaign's manifests and logs. A **set consumer** is a function that is handed a list of bundles by name (the cells of a spec, the entries of a manifest, a list of member ids). The window consumers are exactly:

```text
scripts/run_campaign.py::_authenticate_whole_window_members   (whole-window verdict)
scripts/run_campaign.py::run_campaign                         (final analysis)
scripts/run_campaign.py::run_axi_spec_campaign                (closing analysis)
joulewise/whole_window.py::_derived_neg8_decision
joulewise/analysis_engine/inputs.py::load_analysis_inputs
```

Every other gate call in the eight consumers is a set consumer's.

**(b) The member list of a window consumer** is the union of:

1. every selected bundle path;
2. every copy of a member's bundle id present inside the runs directory (`present_paths`, or `ordinary_present_bundle_paths`);
3. **[E]** for every selected bundle under `axi_attempt_bundles/<name>/`, every directory under that attempt root that holds `metadata.json`, and every attempt that amendment 56 (c) 4 adds from the attempt ledger;
4. **[E]** for every **field-valid** supersession record in the window's campaign log whose `bundle_id` is one of the window's member ids, the directory `Path(record["quarantine"]["path"])`, passed with the record's three digests;
5. **[E]** every member that amendment 56 adds because a finalization record names it.

**[E]** "Field-valid" means `whole_window.supersession_record_field_valid(record, runs_root)` returns `True` (amendment 55 (a)). The records are the first element of what `supersession_entry_validation_results(runs_root, log_path)` returns; its second element, the list of booleans, is **not** used to build item 4. "The window's member ids" are: in `_authenticate_whole_window_members`, the `bundle_id` of every entry of `membership.occurrence_resolutions` (which is filled on the resolved path and on the fallback path alike, `run_campaign.py:5925, :5956`); in `load_analysis_inputs`, the registered entries' bundle ids; in `_derived_neg8_decision`, the member ids it was given. When `supersession_entry_validation_results` returns `None` (the log cannot be read) the consumer adds no item 4, and the resolver's existing refusal stands. Residual, stated: an unreadable campaign log is a refusal today, as it was at base; whether it should be a custody failure is not ruled here.

**[E]** `run_campaign` (final analysis) has no item 4, for this reason and no other: **it licenses nothing.** Its row's `claim_readiness` field is read by no tracked file but `run_campaign.py` (executed, X9). A window that holds a re-done run is licensed only by the whole-window verdict. Without a supersession record that verdict cannot pass (executed, X2); with one, item 4 puts the first run in front of the gate. The sentence of the first ruling, "a supersession is recorded only after collection, by a separate command", is withdrawn: it is true and does not cover the rerun's own final analysis, which runs after the first run was moved aside and before any record exists.

**(c) How the quarantined bundle is authenticated.**

- The path is passed **as recorded**, without `resolve()`. Resolving would follow a symlink and hide it.
- Its label is `superseded:<bundle_id>:<recorded path>`.
- **[E]** It is passed to the gate as the three-element member `(label, path, recorded)` of amendment 55 (b), where `recorded` is `{"config.json": quarantine["config_sha256"], "metadata.json": quarantine["metadata_sha256"], "summary_metrics.json": quarantine["summary_sha256"]}`.
- It is passed **in the same call** as the other members, so that one refusal names every refused member.
- The consumer makes no check of its own before the call and catches nothing after it.
- **[E]** **The record's validity and the quarantined bundle's custody are decided separately.** For a field-valid record, the quarantined bundle is a member whatever the state of its directory. A path that is missing, is not a directory, or is a symlink makes the gate raise `CustodyUnreadable`; a file whose bytes do not hash to the recorded digest makes the gate raise `CustodyFailure`; both are labelled with the member. The resolvers keep calling `validate_occurrence_supersession_entry`, whose behaviour is unchanged. Its `False` for a field-valid record can only mean that the quarantined bytes are missing or changed. In a window consumer that outcome is never acted on, because the gate call comes before any use of the resolution: before a verdict row is appended, before a member receives a reason, before a member is excluded. A window consumer therefore never reports `ambiguous`, `unresolved`, or a per-member reason **on those grounds**. A record that is not field-valid is a record problem and keeps the resolver's `ambiguous`.
- Its status is judged exactly as any member's. A quarantined bundle measured before the battery check and not among the 69 listed runs is `prospective bundle` and refuses the window. No exemption is granted here.

**(d)** **[E]** **`_derived_neg8_decision` and `load_analysis_inputs`** obtain the records through `supersession_entry_validation_results(runs_root, log_path)`, which both modules already import or define, keep those that are field-valid, and add item 4 for each. Each function's gate call stays where it is at `49d77c74` (`whole_window.py:3907`; `inputs.py:3140`, which precedes every other step of the function).

**(e)** **[E]** **The closing analysis of `run_axi_spec_campaign`** calls the gate once, over **every** value of `finalized_bundles` (selected and not) and every attempt amendment 56 (c) 4 adds, each labelled with the physical id the function already builds (`<entry>__a<ordinal>__<run_id>`), before `_idle_admission_core_evaluation` is called. No directory test filters that list.

**(f) A set consumer** authenticates every bundle in the list it was handed, `FAILED` members included, and enumerates nothing else. The superseded runs of the window are the duty of the window's verdict. This is the reading of text 12's first sentence ("a set of bundles whose numbers are claimed") for a consumer that never sees a window. Residual, stated: `aggregate_experiment` binds no window verdict, so nothing shows it a superseded run. Its list is the repetitions of one experiment, where no supersession exists. **[E]** A set consumer relies on the window's verdict row having gated the superseded runs. When a verdict row is consumed later, `whole_window._prepare` gates again only the members the row references, so a row written by code older than this amendment is not re-checked for superseded runs. This is harmless today for two executed reasons: every bundle collected after the base is refused as `prospective bundle` until S1 merges, and the seven supersession records on disk are all already refused (the first ruling's E5). If the list of 69 historical runs ever grows, this sentence must be re-examined by the judge who grows it.

**Forcing fact for the record.** Seven supersession records exist on disk today. In all seven the selected and the quarantined bundle are both already refused as `prospective bundle`. This amendment changes the outcome of no existing window.

**Test rows for amendment 49.** Fixtures: `WindowMembersTests.pair_bundle` builds a bundle with a passing pair, or with `charging=True` a charging pair. "Production path" in a row means: the record is written by `run_record_supersession`, the manifests by the campaign's own writer or the repository's fixture for it, and no resolution object is built by the test. `/tmp/cg_r2e/rb1_prod.py` is a working example of such a fixture.

| Row | Production call site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R49-1 | `_authenticate_whole_window_members` | the production shape: one selected bundle inside the runs directory, passing; `present_paths` holding that one path; a supersession whose quarantine path, outside the runs directory, holds a charging-pair bundle | `WindowBatteryRefusal` whose `members` is one entry, label beginning `superseded:`, status `battery_float_confounded` | the code at `49d77c74`, which returns one `pass` |
| R49-2 | same | as R49-1 with a passing quarantined bundle | two verdicts returned, both `pass`, one under the `superseded:` label | a rule that refuses whenever a supersession exists |
| R49-3 | same (helper level; **[E]** not the witness for custody on the production path, which is R49-3b) | as R49-2 with the quarantine directory deleted after the record is built | `type(exc) is CustodyUnreadable`; `exc.window_member` is the `superseded:` label | a helper that skips a quarantine path that is not a directory |
| **[E]** R49-3b | `run_whole_window_verdict`, production path | the log holds a record written by `run_record_supersession`; the quarantine directory is deleted afterwards | `CustodyUnreadable`; `exc.window_member` begins `superseded:`; **no row is appended to the campaign log** | the code at `49d77c74`, which raises nothing and appends a `failed` row carrying `whole_window_campaign_membership_ambiguous` (executed, X1 S3) |
| **[E]** R49-3c | same | the same record; one byte appended to the quarantined `summary_metrics.json` | `type(exc) is CustodyFailure`; `exc.window_member` begins `superseded:`; `exc.failures[0]["artifact"] == "summary_metrics.json"`; no row appended | the same (executed, X1 S4) |
| **[E]** R49-3d | same | the quarantined bundle carries a charging pair; the record is written; the directory is then deleted | `CustodyUnreadable`; no row appended | the same (executed, X1 S5). This is the case where the evidence of charging is destroyed. |
| R49-4 | `_authenticate_whole_window_members` | the quarantine path is a symlink to a passing bundle | `CustodyUnreadable` | a helper that calls `resolve()` on the path |
| R49-5 | same | selected bundle prospective, quarantined bundle charging | one `WindowBatteryRefusal` naming **both** | two gate calls, one per kind of member |
| R49-6 | `run_whole_window_verdict`, production path | quarantined bundle charging, present and unaltered | `WindowBatteryRefusal` naming the `superseded:` label; **no verdict row is appended** | the code at `49d77c74` (executed, X1 S2: the quarantine path is not in the gate's list) |
| R49-7 | `load_analysis_inputs` | a manifest whose one ordinary member has a field-valid supersession, quarantined bundle charging | `WindowBatteryRefusal` naming the `superseded:` label | the code at `49d77c74` |
| **[E]** R49-7b | `load_analysis_inputs`, production path | as R49-7 with a passing quarantined bundle whose directory is deleted after the record is written | `CustodyUnreadable` labelled `superseded:` | the code at `49d77c74`, which gives the member the payload `{"result": "unknown", "verified": False, …}` (read, NOT EXECUTED) |
| R49-8 | `_derived_neg8_decision` | same shape as R49-7 | same | the code at `49d77c74` |
| **[E]** R49-8b | `_derived_neg8_decision` | same shape as R49-7b | `CustodyUnreadable` labelled `superseded:` | a rule that builds item 4 from the validation booleans |
| R49-9 | `run_axi_spec_campaign`, closing analysis | two finalized attempts of one entry: attempt 1 not eligible with a charging pair, attempt 2 selected and passing | `WindowBatteryRefusal` naming attempt 1's physical id; no whole-window verdict row written | a gate over selected runs only |
| **[E]** R49-10 | `run_whole_window_verdict`, production path | the rerun is present inside the runs directory; the first run was moved outside it; **no** supersession record | a row is appended with `status` not `passed` and the condition `whole_window_campaign_membership_unresolved` | a resolver that selects the present copy when no record exists (executed at `49d77c74`, X2: the row is GREEN today; it pins the property RS-4's rejection relies on) |
| **[E]** R49-11 | tracked files under `joulewise/` and `scripts/`, by text search | the tracked tree | the string `claim_readiness` occurs in `scripts/run_campaign.py` and in no other file | a module that reads the campaign row's readiness as a licence. GREEN today (X9). If it goes RED the seat returns NEEDS_RULING. |

The existing test with two `present_paths` stays (it pins item 2) and its docstring says that it is not the supersession case.

### Amendment 50 (amends text 9, the sentences on the entry, the marker and the refusals; S1's existing scope: `joulewise/scored_reduce.py`, `tests/test_scored_reduce.py`)

Terms for this amendment. A **placement** is one scheduled execution of one block of test items in the scored campaign, keyed `(block_id, attempt)`. The **roster** is the executed schedule; it records for each placement an observation status: `completed`, `cut_off` (it started and was stopped) or `not_started`. A **capture window** is the reducer's input record carrying one placement's measured energy and the digest of the bundle it came from. The **key set** is every placement whose status is `completed` or `cut_off`. The **marker** is an evidence entry of the form `{"no_bundle": …}`.

50. **Every started placement owes a verdict; the marker is admitted for no status.**

**(a) The entry.** For every key in the key set, the entry is a `PairVerdict` of kind `bundle` whose `bundle_sha256` is 64 hexadecimal characters.

**(b) Binding.**
- Where a capture window exists for the key, `bundle_sha256` must equal that window's `bundle_sha256`.
- Where none exists, `bundle_sha256` must differ from every capture window's `bundle_sha256` and from every other entry's `bundle_sha256`.
- A failure of either is `battery_evidence_unbound`.

**(c) The marker.** An entry of the form `{"no_bundle": <anything>}` is refused with `battery_evidence_unbound`, for every status. The form stays recognised so that it is refused under that code and not as a malformed input. It can be admitted later only by a cold gate that names the roster field recording that a placement finalized no bundle. No such field exists (`scored_packer.py:237, :402`).

**(d) Order, and which code is reported.** Shape, duplicates and the two key-set checks first, as today. Then binding for every entry. Then status for every entry: if any entry is `battery_float_confounded` the code is `battery_float_confounded`; otherwise, if any is not `pass`, the code is `battery_float_evidence_missing`. The refusal's detail lists **every** key whose status is not `pass`, with its status, in placement order. All of this precedes `_check_window`, as text 9 rules.

**(e) Outcome for each (placement status × evidence form).**

| Roster status | Capture window | Evidence supplied | Outcome |
|---|---|---|---|
| `not_started` | any | none | accepted (the key is outside the key set) |
| `not_started` | any | any entry | `battery_evidence_unbound` |
| `completed` or `cut_off` | any | none | `battery_evidence_missing` |
| `completed` or `cut_off` | any | the marker, any value | `battery_evidence_unbound` |
| `completed` or `cut_off` | any | anything that is not a bundle-kind verdict with a 64-hex digest | `battery_evidence_input` |
| `completed` or `cut_off` | exists | verdict whose digest differs from the window's | `battery_evidence_unbound` |
| `completed` or `cut_off` | none | verdict whose digest equals a window's or another entry's | `battery_evidence_unbound` |
| `completed` or `cut_off` | either | bound verdict, `pass` | accepted |
| `completed` or `cut_off` | either | bound verdict, `battery_float_confounded` | `battery_float_confounded` |
| `completed` or `cut_off` | either | bound verdict, `battery_float_evidence_missing`, `unobserved_historical` or `not_applicable` | `battery_float_evidence_missing` |

The placement's class (live, terminal, voided) changes no row.

**(f) Two consequences, stated.**
- A run killed before it wrote a bundle has no verdict to supply, so the reduction refuses with `battery_evidence_missing`. This is recorded under lane SCORED-CEILING-BATTERY-01 as a campaign-cost question.
- **Residual.** For a placement without a capture window the reducer has nothing to check the digest against. Rule (b) stops one verdict from being used for two placements; it cannot show that the verdict belongs to this placement's bundle. That binding is the duty of the harvest step that produces the evidence. The ruling that lands the real producer must either give the reducer the harvest's list of member digests keyed by placement, or say why not. Until then `reduce` has no production caller (text 9).

**(g) The fixture producer** in `tests/test_scored_reduce.py` supplies, for a started placement without a window, a verdict whose digest is `sha256(repr((block_id, attempt, "no-window")))`.

**Test rows for amendment 50.** Production call site for all: `scored_reduce.reduce`. Fixture: `_terminal_night(width=2, kind="ceiling_violation")`; placement V = `('large:decode:1:0', 0)` (voided, `cut_off`, no window).

| Row | Input | Expected code | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R50-1 | V carries a charging verdict with a fresh digest | `battery_float_confounded` | the code at `49d77c74`, which refuses `battery_evidence_unbound` |
| R50-2 | V carries a passing verdict with a fresh digest | the reduction returns | the code at `49d77c74` |
| R50-3 | V carries `{"no_bundle": "cut_off"}` | `battery_evidence_unbound` | the code at `49d77c74`, which returns a reduction |
| R50-4 | a voided `completed` placement carries `{"no_bundle": "completed"}` | `battery_evidence_unbound` | the code at `49d77c74` |
| R50-5 | V carries a passing verdict whose digest is another placement's window digest | `battery_evidence_unbound` | a rule that accepts any 64-hex digest where no window exists |
| R50-6 | two placements without windows carry one digest | `battery_evidence_unbound` | same |
| R50-7 | an earlier placement carries `battery_float_evidence_missing`, a later one a charging verdict | `battery_float_confounded`; the detail names both keys | a rule that reports the first non-pass entry in order |
| **[E]** R50-8 | the fixture producer's output for the fixture night | it holds no marker; the key set equals text 9's expression | the producer at `49d77c74`, which on this fixture emits **six** markers: two for voided `cut_off` placements, two for voided `completed`, two for terminal `completed` (executed, X8). The row asserts that the count of markers is zero; it does not depend on the number six. |

`test_complete_placement_universe_and_no_bundle_vocabulary` is rewritten to R50-8. Its assertion `set(markers) <= {"completed", "cut_off"}` is removed because this amendment supersedes the sentence it pinned; the report names it in the form (old expectation, new expectation, ruled sentence).

### Amendment 51 (amends text 12, the sweep sentence and the allowlist sentence; replaces amendment 26's clause "the sweep matches the function name and `BundleReader.metadata()`"; S1's existing scope: `tests/test_bfgs_consumer_sweep.py`)

51. **The sweep follows the path, checks that the gate dominates the read, and checks its own `behind_gate` rows.**

**(a) Terms.**
- A **watched name** is one of `summary_metrics.json`, `metadata.json`, `power_trace.csv`.
- A **watched constant** is a string constant that equals a watched name or ends with `/` followed by one.
- A **module constant** is a name assigned at the top level of any tracked file under `joulewise/` or `scripts/` from a path expression (below). Module constants are collected over all those files first and matched by name, so a constant imported from another module is recognised.
- A **path expression** is any of: a watched constant; a name that is a module constant or a path name of the function; an attribute whose name is an upper-case module constant; a `/` operation either of whose sides is a path expression; a tuple, list or set literal any of whose elements is a path expression; a call to a **path builder** any of whose arguments, or whose receiver, is a path expression.
- The **path builders** are `Path`, `PurePath`, `PurePosixPath`, `join`, `joinpath`, `str`, `fspath`, `with_name`, `with_suffix`, `resolve`, `absolute`, `expanduser`, `parent`, `glob`, `rglob`, `iterdir`. They return a path, never a file's content.
- A **path name** of a function is a name bound in that function (by assignment, annotated assignment, `:=`, a `for` target, or a comprehension target) from a path expression. Binding is repeated until no new name is added. A name bound from any other call is **not** a path name: it holds content, not a path.
- The **non-reading calls** are a constant list in the test of callee names that cannot return a file's content (`is_file`, `exists`, `is_dir`, `is_symlink`, `relative_to`, `as_posix`, `lstat`, `stat`, `unlink`, `rename`, `mkdir`, `write_text`, `write_bytes`, `append`, `add`, `print`, `add_argument`, the built-in container and string functions, and exception constructors). The seat may extend the list only with names of that kind; the refuter checks each entry.
- The **tolerant accessors** are the four reader methods `raw_metadata`, `raw_config`, `raw_summary`, `raw_artifact_bytes`, which return a file's content without the battery check.

**(b) A read site** is, inside one function (nested functions and methods are swept separately and inherit nothing):
1. any call of a tolerant accessor on any receiver; or
2. any call that is neither a path builder, nor a non-reading call, nor a gate call, and whose receiver or any argument (positional or keyword) is a path expression; or
3. any assignment of a path expression to an attribute or a subscript (`self.trace = bundle / "power_trace.csv"`), reported as operation `store:<target text>`, because the read then happens in another function through a value the sweep cannot follow.

Under item 2, handing a path to a helper (`read_support_intervals(bundle / "power_trace.csv")`) is a read site **in the caller**, where the watched name enters. The helper, which sees only a parameter, is not reported.

**(c) A gate call** is:
- **the window form:** a call of `authenticate_window_members`, by bare name or as an attribute, in a module that imports that name from `joulewise.bundle_read` or imports that module, or in `joulewise/bundle_read.py` itself; or
- **the reader form:** a call `X.metadata()` where `X` is a call of `BundleReader`, a name bound in the function from a call of `BundleReader`, a parameter whose annotation names `BundleReader`, or `self` inside the class `BundleReader`.

No other `.metadata()` call is a gate.

**[E]** **The reader form is bound to its reader.** A tolerant-accessor read site ((b) 1) is gated by a reader-form gate call only if the read's receiver is the **same name**, or the same `self`, as the gate call's `X`, and that name is not bound again between the gate call and the read. A gate call on a constructed reader that has no name (`BundleReader(a).metadata()`) gates no tolerant-accessor read.

**(d)** **[E]** **A read site is gated** only if some gate call of the same function (i) comes before it in source order (line, then column) and (ii) **dominates** it, by these rules:

1. Every `if`, `for`, `while`, `match` case, `else` of a loop or of an `if`, conditional expression, or right-hand operand of `and`/`or` that encloses the gate call must also enclose the read site.
2. **The body of a `try` counts as such a branch unless every handler of that `try` has `raise` (bare, or with an exception) as its last statement.** A handler that ends any other way lets execution continue past the `try` although the gate raised. The test is on the handler's last statement and not on the exception types it names, because the sweep reads syntax and cannot tell which classes descend from which.
3. **A read site inside a handler or inside the `finally` of a `try` is never gated by a gate call in that `try`'s body.** The handler runs exactly when something in the body raised.
4. A read site inside the `else` of a `try` is treated as if it followed the body: `else` runs only when the body finished without an exception.
5. **The body of a `with` counts as a branch when any of its context expressions is a call whose callee is named `suppress`** (bare or as an attribute). Otherwise it does not.

A read site that is not gated is **reported** as `(path, qualified function, operation, watched name, line)`.

**(e) The site-specific clause for `scripts/issue_dg071_dg075_statistics.py` is deleted.** Under (b) the script is reported at `main`, operation `direct:issue_artifacts`, watched name `power_trace.csv`, which is where the pinned path is named and handed to the reader. That report is the witness amendment 41's round-2 note requires. Its row is class `historical` and its reason cites amendment 41.

**(f) The allowlist.** The key is `(path, qualified function, operation, watched name)`; for the tolerant accessors the watched name is `-`. The set of reported keys must **equal** the set of allowlist keys. Each row carries a class and a reason, and a `behind_gate` row carries a third field.

| Class | A row may carry it only if | The reason must state |
|---|---|---|
| `strict_validation` | every value the function returns or writes is a digest, a boolean, an identity string, or a list of problem strings | what is validated |
| `non_claim` | (i) no field the function reads from the file is an energy, power, current, charge or voltage value or is computed from one; **or** (ii) nothing the function returns or writes is consumed by a claim artifact | which of (i), (ii); for (i) the fields read; **[E]** for (ii) **the path or the record type of everything the function writes, and the name of every function it returns a value to** |
| `historical` | the function reads energy values from bundles measured before the battery check, and cannot be pointed at a later bundle: it pins what it reads by digest in committed code, or reads only a corpus that a committed artifact names | the pin or the corpus |
| `behind_gate` | the function is reached only after a gate, in one of the two forms below | nothing beyond the third field |

A **claim artifact** is a file a paper number is taken from or licensed by: a floor artifact, a whole-window verdict row, an analysis output, a fill of the paper's results registry, a figure.

**[E]** **Clause (ii) is checked, row by row, by the refuter**, who searches the tracked tree for every reader of each output the reason names and confirms that none is a claim artifact or writes one. A row whose reason names no output, or whose output has a reader the refuter cannot classify, is returned. Example the seat must rule on in its report: `scripts/check_window_provenance.py::_run_assertions.check_a3` reads `gross_energy_j`; that script is outside S1's WRITE_SCOPE, so it cannot be gated in S1; its row is `non_claim` (ii) only if the refuter's search confirms it, and otherwise the site is returned to the lead.

**`behind_gate`, two forms, both checked by the sweep:**
- **Callers form.** Third field `callers`: a tuple of `path::qualified function`. The sweep asserts that every call of the helper's name (bare or as an attribute) in any tracked file under `joulewise/` or `scripts/` lies in a listed function, and that in each listed function either a gate call comes before and dominates that call, or the listed function itself has a `behind_gate` row. A chain that returns to a function already visited fails.
- **Consumers form**, for a function that runs during collection and whose result is used only later. Third field `consumers`: a tuple of (`path::qualified function`, name of the consuming call). The sweep asserts that in each named function a gate call comes before and dominates **every** call of the named consuming function.

**(g) Which sites may be exempted and which must be gated.**
1. A read site inside one of the eight consumer modules whose function returns, or passes on, a value from the file that includes an energy, power, current, charge or voltage value is **gated in the function or `behind_gate`**. It may carry no other class. `floor_extraction._read_summary` is such a site: its row is `behind_gate`, callers form.
2. The rows of `joulewise/whole_window.py` that today carry `strict_validation` with the reason "called behind the window gate" are re-classed: `behind_gate` where the function returns content, `strict_validation` where it returns only digests, booleans, identities or problems.
3. `scripts/run_campaign.py::evaluate_member` carries `behind_gate`, consumers form, with `consumers = (("scripts/run_campaign.py::run_campaign", "classify_campaign_members"), ("scripts/run_campaign.py::run_axi_spec_campaign", "_idle_admission_core_evaluation"))`.
4. `historical` is held by the eight rows that hold it at `49d77c74` (two in `envelope_gate.py`, five in `make_figures.py`, one in `issue_dg071_dg075_statistics.py`), re-keyed to the new key form, each checked by the refuter against the class's condition. A reported site in one of those same three files may take `historical` on the same ground. **Any other new `historical` row needs a cold gate.**
5. `scripts/paper_prefill_resolvability_projection.py::scan_corpora` is `non_claim` under (i): `read_support_intervals` reads `timestamp_s`, `interval_start_s` and `interval_end_s` and nothing else. The seat states the fields read by `read_model` and `recorded_label` in their rows; if either reads an energy value the site is returned to the lead.
6. Every other reported site is classed by the seat under the table's conditions, and **the refuter checks every row**. A site that fits no class is gated, or returned.

**(h) What the sweep cannot see, stated.**
- A read that never names the file: a loop over a directory listing, a copy of a whole directory, a digest of a whole bundle.
- A path that reaches a function inside an object the sweep did not see stored.
- Calls are matched by name, so two helpers of one name are treated as one.
- **[E]** **Which bundle the gate authenticated.** A window-form gate call on one member list followed by a read of another bundle's path counts as gated (executed, X5, source H3). So does a reader-form gate call followed by a path read ((b) 2) of a different bundle. Only tolerant-accessor reads are bound to their reader, by (c).
- **[E]** A context manager other than `suppress` that swallows exceptions in its exit method.
- **[E]** A handler that ends in `raise` inside a branch of its own and lets another branch fall through is judged by its last statement only.

**Test rows for amendment 51.** Each self-test calls the test module's `sweep_source` on a source string as file `joulewise/zz_new.py`; R51-14 to R51-17 run the sweep over the tracked tree. Sources K1 to K10 and G1 to G3 are those of `/tmp/cg_r2/sweep49_cases.py`; H1, H2, H4 and H6 are those of `/tmp/oc2/sweep_holes.py`; all are reproduced here in words.

| Row | Source | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R51-1 (K1) | the read `(b / "power_trace.csv").read_bytes()` | reported | none (pins the case that works today) |
| R51-2 (K2) | the path assigned to a name, then `name.read_bytes()` | reported | the detector at `49d77c74` |
| R51-3 (K3) | the watched name in a module constant | reported | the detector at `49d77c74` |
| R51-4 (K4) | `open_authentication_input(b / "power_trace.csv", …)` | reported | the detector at `49d77c74` |
| R51-5 (K5) | `event.metadata()` on a parameter of no declared type, then a read | reported | a rule that takes any `.metadata()` call as the gate |
| R51-6 (K6) | the read first, the gate after it | reported | a rule that accepts a gate anywhere in the function |
| R51-7 (K7) | the gate inside `if b.is_dir():`, the read after the `if` | reported | a rule that checks order and not dominance |
| R51-8 (K8) | the path handed to a helper | reported as `direct:helper` | a rule with a fixed list of read functions |
| R51-9 (K9) | `for name, field in (("config.json","c"), ("metadata.json","m")):` then `(b / name).read_bytes()` | reported, watched name `metadata.json` | a rule that binds names only by assignment |
| R51-10 (K10) | a local function named `authenticate_window_members`, not imported from the reader module, called before a read | reported | a rule that matches the gate by name alone |
| **[E]** R51-11 (G1 to G3) | the gate first then the read; `r = BundleReader(b)`, `r.metadata()`, then `r.raw_summary()`; gate and read inside the same `if` | not reported | a rule that reports every read |
| R51-12 | a store to an attribute: `self.trace = b / "power_trace.csv"` | reported as `store:self.trace` | a rule without item (b) 3. NOT EXECUTED in any prototype. |
| R51-13 | `joulewise/cli.py` from `git show 1417c0c4:` | the `raw_metadata` read at line 423 is reported; `skipTest` if the commit is absent | the anchor `b859317c` |
| R51-14 | the tracked tree | reported keys equal allowlist keys; every class is one of the four; every reason is non-empty; **[E]** every `non_claim` reason that states (ii) names at least one output | an allowlist row removed, or a row added for a site that does not exist |
| R51-15 | the tracked tree with the amendment-41 row removed | the sweep fails naming `scripts/issue_dg071_dg075_statistics.py`, `main` | the site-specific clause kept |
| R51-16 | a `behind_gate` row, callers form, and a new call of the helper added in an unlisted function | the sweep fails naming the unlisted caller | a `behind_gate` row that is not checked |
| R51-17 | the consumers-form row of `evaluate_member`, with the gate at `run_campaign` (final analysis) deleted | the sweep fails | a row that is not checked |
| **[E]** R51-18 (H1) | `try:` gate `except Exception: pass`, then the read after the `try` | reported | rule (d) as first ruled, under which the prototype is silent (executed, X5) |
| **[E]** R51-19 (H2) | `with contextlib.suppress(RuntimeError):` gate, then the read after the `with` | reported | the same (X5) |
| **[E]** R51-20 (H4) | `try:` gate `except RuntimeError:` the read inside the handler | reported | the same (X5) |
| **[E]** R51-21 (H6) | `BundleReader(a).metadata()` then `BundleReader(b).raw_summary()` | reported | a reader form not bound to its reader (X5) |
| **[E]** R51-22 (G4, G5) | G4: `try:` gate `except RuntimeError: raise`, the read after the `try`. G5: `try:` gate `except ValueError as exc: raise MintError(...) from exc` `else:` the read | neither reported | a rule that treats every `try` body as a branch, or that treats `else` as a handler |

**Size, so the seat can tell a wrong implementation from a right one.** The first judge's prototype, without item (b) 3, reports 120 rows over 89 functions at `49d77c74`. Rule (d) 2 adds the reads that follow three `try` statements (executed, X7: `calibration_bracketing.py`, `reduce.py`, `window_duration_margins.py:942`); (d) 5 adds none. I did not re-run the prototype with the new rules: the count after them is NOT EXECUTED, and should exceed 120 by a small number. A count far from that is a finding to return, not to explain away. `joulewise/reduce.py` is on the excluded list and must stay byte-identical; a site reported there gets an allowlist row or is returned, never an edit.

### Amendment 52 (amends amendment 36's round-2 rule, third sentence; S1's existing scope: `joulewise/bundle_read.py`, the eight consumer modules, `tests/test_bfgs_window_consumers.py`, `tests/test_bfgs_consumer_sweep.py`)

52. **No handler in a consumer can swallow the gate's exceptions.**

**(a)** Amendment 36's sentence "They do not catch `CustodyFailure`, by that name or through `except Exception`" is replaced by: "No handler in the eight consumer modules changes, replaces or discards a `CustodyFailure` or a `WindowBatteryRefusal`, whatever exception type the handler names."

**(b)** `joulewise/bundle_read.py` gains the module constant `GATE_EXCEPTIONS = (WindowBatteryRefusal, battery_float.CustodyFailure)`. The consumers import it from `bundle_read`. They still do not import `battery_float`.

**(c)** A **broad handler** is one whose caught types include `RuntimeError`, `Exception` or `BaseException`, or that names no type. In the eight consumer modules, every `try` statement that has a broad handler has, **before** it, the handler

```python
except GATE_EXCEPTIONS:
    raise
```

whose body is that one statement. This is not a catch within the meaning of (a): the same object leaves, unchanged. The one exception: a broad handler whose own last statement is a bare `raise` (the lock-release handlers) needs no such clause.

**(d)** Every handler that round 2 narrowed from `except Exception` to a tuple of types returns to the types it caught at `1417c0c4`, with the clause of (c) before it. The narrowing made exception classes outside the tuple crash where base produced a structured refusal; with (c) in place it is not needed.

**(e)** Handlers that name `BundleReadError` are untouched. A battery refusal raised by `BundleReader.metadata()` is a `BundleReadError` to its callers by amendment 42 (a), which ruled that "every existing caller of `metadata()` behaves as before".

**(f)** If the guard suite (`tests/test_battery_float_consumers.py`) goes red on (b) or (c), the seat stops and returns NEEDS_RULING. No guard row is granted here. NOT EXECUTED by me.

**(g)** **[E]** **Residual, named, with a lane.** `joulewise/analysis_manifest_v3.py` is not one of the eight consumers and is outside S1's WRITE_SCOPE. It reaches the gate through `AuthenticatedConsumptionSession._prepare` (`:3704`). Its handler at `:3712` names `RuntimeError` and re-raises the gate's exception as `AnalysisManifestFinalizationError("analysis_finalization_attachment_invalid", …)`; its public validator catches `Exception` at `:4499` and returns a `ManifestRefusal` (executed and read, X6). Both refuse; neither releases a number; both turn a custody failure into a refusal code. **S1 does not edit this file.** The lane BFGS-MANIFEST-CUSTODY-01 (§15) closes it, and must close before any analysis manifest is finalized or validated over a bundle measured after S1 merges. Until it closes, this is the one named place where the gate's exception is converted, and the sentence of the first ruling's §11, "Amendment 52 removes the one place found where a custody failure became a reason string", is corrected to: "Amendment 52 removes every such place found in the eight consumer modules; one more, in `joulewise/analysis_manifest_v3.py`, is named in 52 (g)."

**Test rows for amendment 52.**

| Row | Production call site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R52-1 | `inputs.bind_floor_artifact_evidence` | a salvage component one of whose members has its `raw/battery_float.post.ioreg` deleted after finalization | `type(exc) is CustodyFailure`; `exc.window_member` is the member's label | the code at `49d77c74`, which returns the problem string `whole_window_verdict_provenance_invalid` |
| R52-2 | same | the member carries a charging pair | `WindowBatteryRefusal` naming the member | the code at `49d77c74` |
| R52-3 | same | the component's validation raises a `RuntimeError` that is not a gate exception | the problem string, as at base | a fix that removes `RuntimeError` from the handler's tuple |
| R52-4 | the eight modules, by syntax tree | the tracked files | every `try` with a broad handler has the clause of (c) before it, or the handler ends in a bare `raise` | the Opus mutants M4b (the gate in `mint_floor_artifact._strict_bundle` wrapped and re-raised as `MintError`) and M4c (`except RuntimeError` around the gate in `extract_cells`), both of which survive today per the lens report |
| R52-5 | the eight modules, by syntax tree | the tracked files, plus the source `from joulewise import battery_float` inserted in `aggregate.py` | the import test fails | the matcher at `49d77c74` (the Opus mutant M7) |
| **[E]** R52-6 | every tracked file under `joulewise/` and `scripts/` **outside** the eight, by syntax tree | the tracked files | the set of files holding a `try` whose body calls `authenticate_window_members` or a method named `_prepare`, and that has a broad handler without the clause of (c) and not ending in a bare `raise`, **equals** the test's constant `NAMED_RESIDUALS = {"joulewise/analysis_manifest_v3.py"}` | (1) a check limited to the eight modules, which cannot see the file; (2) a new ninth module that wraps the gate, which must make the set differ. When the lane closes, the constant becomes empty and this row forces that edit. |

Size, measured by the first judge: 19 handlers name `RuntimeError` and 15 name `BaseException`, of which 12 already re-raise. About 22 `try` statements gain the clause.

### Amendment 53 (amends text 12's scope sentence for `run_campaign.py`; S1's existing scope: `scripts/run_campaign.py`, `tests/test_bfgs_window_consumers.py`)

53. **No gate during collection.**

**(a)** The gate call in `evaluate_member` (`run_campaign.py:2801-2802`) is removed. `evaluate_member` decides nothing about battery state and refuses nothing on it.

**(b)** **[E]** The gate of `run_campaign`'s final analysis (`:8928`) stays where it is: after the collection loop, before `classify_campaign_members`. Its list is every evaluated member **whose evaluation read a bundle, or whose bundle directory exists when the gate is called**. "Whose evaluation read a bundle" means that at least one of `evaluation.status`, `evaluation.summary`, `evaluation.metadata` is not `None`: `evaluate_member` sets each of them only from a file it read in the bundle directory (`:2803-2830`, read). A member that was evaluated from a bundle and whose directory is gone when the gate is called is handed to the gate, which raises `CustodyUnreadable` naming it. A member whose evaluation found no directory and read nothing is omitted, as today; that is a run that never wrote a bundle.

**(c)** The closing analysis of `run_axi_spec_campaign` is gated by amendment 49 (e).

**(d)** Collection therefore runs to its end whatever the battery readings show, every run's provenance row is written, and the refusal at the closing analysis names every refused run. A rule that stops a night early on a battery reading, if ever wanted, is a separate ruled change.

**(e)** **[E]** **Flagged for the lead and for round F, not ruled.** Text 12 refuses `not_applicable`, so the final analysis of a campaign made only of simulated runs raises. With the collection-time gate removed this happens after collection and names every run, where at `49d77c74` it happens at the first run. Tests that drive a simulated campaign through its final analysis will meet that refusal in round F. **The repair in round F is a fixture shaped like R53-1 (bundles that carry a real battery pair), never a gate put back into collection and never a handler around the final gate.** Whether the final analysis of an all-simulated campaign should refuse is text 12's existing ruling; I leave it as it stands.

**Test rows for amendment 53.**

| Row | Production call site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R53-1 | `run_campaign` | three members; the second carries a charging pair; the third has no battery record and is not among the listed runs | all three runs are collected and all three provenance rows are written; then `WindowBatteryRefusal` naming the second as `battery_float_confounded` and the third as `battery_float_evidence_missing` | the code at `49d77c74`, which raises at the second member, names one, and writes no row for it |
| R53-2 | `run_campaign` | as R53-1 | no campaign verdict row is written | the final-analysis gate deleted (the Opus mutant M5) |
| R53-3 | `evaluate_member` | a bundle directory with a charging pair | returns a `MemberEvaluation`; raises nothing | the code at `49d77c74` |
| **[E]** R53-4 | `run_campaign` | three passing members; the test wraps `evaluate_members` so that the real function runs and returns, and then the second member's directory is deleted | `CustodyUnreadable`; `exc.window_member` is the second member's bundle id; no campaign verdict row is written | the filter `if evaluation.bundle_path.is_dir()` at `49d77c74`, which omits the member (read, NOT EXECUTED) |

### Amendment 54 (amends amendment 47, test row R47-4; S1's existing scope: `tests/test_bundle_read.py`)

54. **R47-4 follows the classification rule.** Amendment 47's text is unchanged. Its test row R47-4 is replaced by the two rows below. The builder at `49d77c74` already behaves as they require; only the build-level test is owed. This amendment is unchanged by the erratum: the refuter reported no finding against it.

| Row | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R47-4 | `broken.json` that fails to parse and holds the line `bundle_tree_sha256: ` followed by 64 `a` characters, with no classification row | stderr names the file as `unparseable broken.json`; then `ValueError` matching `unclassified candidate pair`, naming the key `bundle_tree_sha256` and the file `broken.json` | (1) the `continue` of `b859317c`, which skips the file and returns `([], [])`; (2) a rule that classes a candidate in an unparseable `.json` file as `quoted` |
| R47-4b | `broken.json` that fails to parse and holds 64 `a` characters on a line with no key token | stderr names the file as unparseable; `build` returns no entry and no listed candidate; nothing is raised | a rule that raises on every unparseable `.json` file |

The seat's existing scan-level test (`_candidates` yields the candidate and names the file) stays.

### Amendment 55 (new; amends amendment 42's gate contract, the sentence that defines a member; S1's existing scope: `joulewise/bundle_read.py`, `joulewise/whole_window.py`, `tests/test_bundle_read.py`, `tests/test_bfgs_window_consumers.py`)

55. **A record's validity is read from its fields; the bytes it names are checked by the gate.**

**The forcing problem.** A supersession record stops passing validation at the moment the quarantined bundle is deleted or altered, so the one check that could have detected the loss removes the bundle from the list instead (executed, X1). The two questions must be asked by different functions.

**(a) Field validity.** `joulewise/whole_window.py` gains the function `supersession_record_field_valid(entry, runs_root) -> bool`, exported in `__all__`. With `root = Path(runs_root).resolve()`, it returns `True` exactly when all of the following hold. It opens no file of the quarantined bundle and does not require the quarantine directory to exist:

1. every condition of `validate_occurrence_supersession_entry` from its first line to the check `present != [canonical] or not canonical.is_dir()` inclusive (`whole_window.py:2778-2813` at `49d77c74`): the schema version, the record type, `runs_root == str(root)`, a non-empty `bundle_id`, a non-blank `reason`, a non-empty list of superseded occurrences, a mapping `quarantine`, `entry_sha256` equal to `supersession_entry_sha256(entry)`, every occurrence descriptor valid, no two descriptors equal, the selected one not among the superseded, and exactly one copy of the bundle id present inside the runs directory, at its canonical path;
2. `quarantine["path"]` is a non-empty string;
3. the location it names lies outside the runs directory, **decided without requiring the quarantine to exist**: with `q = Path(quarantine["path"]).resolve(strict=False)`, neither `q == root` nor `root in q.parents`. `resolve(strict=False)` follows the links of the path components that exist and keeps the rest as written, so an absent quarantine directory resolves without error (executed, X12). `os.path.abspath` must **not** be used: it follows no link, and on this machine the runs root resolves through `/private/var` while the path as written begins `/var`, so an inside path would be judged outside (executed, X12);
4. each of `quarantine["config_sha256"]`, `quarantine["metadata_sha256"]`, `quarantine["summary_sha256"]` is a string of exactly 64 characters from `0-9a-f`.

Condition 1's last check reads the runs directory, not the quarantine. It stays: two present copies of one bundle id is `ambiguous` by an earlier ruling, and the repository pins it (`test_recorded_supersession_never_resolves_two_present_copies`).

`validate_occurrence_supersession_entry` and `supersession_entry_validation_results` are **not changed**, in signature or behaviour. They are called by `scripts/check_window_provenance.py:955`, outside S1's WRITE_SCOPE, and by the record command (`run_campaign.py:6135`), which must go on refusing to write a record whose quarantined bytes do not match.

**(b) The gate accepts recorded digests.** A member handed to `authenticate_window_members` is `(label, path)` or `(label, path, recorded)`, where `recorded` maps a file name to the 64-hex SHA-256 recorded for it. For a member with `recorded`, **before** the member is classified and for each name in sorted order, the gate computes the SHA-256 of `path / name` with the reader module's existing `sha256_authentication_input`. Then:

- if the file, or the directory, is missing, is a symlink, or cannot be read: the gate raises `battery_float.CustodyUnreadable`, with `window_member = label`, as it does today for an unreadable member;
- if the digest differs from the recorded one: the gate raises `battery_float.CustodyFailure([{"slot": "supersession_quarantine", "artifact": name, "expected_sha256": <recorded>, "observed_sha256": <computed>}])`, with `window_member = label` and the note `window member: <label>`, as it does today for every custody failure it labels;
- otherwise the member is classified exactly as a two-element member.

The slot string is the caller's to choose only through the label; the gate uses `"supersession_quarantine"` when the label begins `superseded:` and `"recorded_member"` otherwise.

**(c)** No consumer constructs a custody exception, compares a digest of a quarantined file, or imports `battery_float`. `joulewise/battery_float.py` is not edited: the two exception classes are used as they are (`battery_float.py:55-85`, read).

**(d)** If the guard suite (`tests/test_battery_float_consumers.py`) goes red because `bundle_read.py` now constructs `CustodyFailure`, the seat stops and returns NEEDS_RULING. NOT EXECUTED by me.

**Worked example (the numbers are X1's).** Window: three bundles inside the runs directory, one of them the rerun of `p2-retried-work__r1`; the first run of that id was moved to a directory outside the runs directory; the record command wrote one record. The directory is then deleted. Today: validation `[False]`, the resolver says `ambiguous`, the gate is handed six labels none of which is the quarantine, the verdict command exits 1, one row is appended with `status failed`. Under amendments 49 and 55: the record is field-valid (its fields did not change), so the gate is handed a seventh member `superseded:p2-retried-work__r1:<path>` with three digests; the first file it tries to hash is missing; it raises `CustodyUnreadable`; no row is appended.

**Test rows for amendment 55.**

| Row | Production call site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R55-1 | `bundle_read.authenticate_window_members` | one three-element member: a passing bundle and its three true digests | the verdict is returned, `pass` | a gate that rejects a three-element member |
| R55-2 | same | as R55-1, one byte appended to `summary_metrics.json` after the digests were taken | `type(exc) is CustodyFailure` (not the subclass); `exc.window_member` is the label; `exc.failures[0]["artifact"] == "summary_metrics.json"` | a gate that ignores the third element (the gate at `49d77c74` cannot be handed one) |
| R55-3 | same | a three-element member whose directory does not exist | `CustodyUnreadable`, labelled | a gate that skips a member whose directory is absent |
| R55-4 | same | two members: the first prospective (status refusal), the second three-element with a wrong digest | `CustodyFailure` naming the second; the status refusal of the first does not pre-empt it | a gate that raises the status refusal first and never checks the digests |
| R55-5 | `whole_window.supersession_record_field_valid` | a record written by `run_record_supersession`, then the quarantine directory deleted | `True`, while `validate_occurrence_supersession_entry` on the same record returns `False` | a function that resolves the quarantine path with `strict=True` |
| R55-6 | same | a record whose `quarantine.path` is written as `<runs directory>/../<runs directory name>/inside`, with the runs directory created under a temporary directory whose path passes through a symbolic link (the platform's default temporary directory does on macOS) | `False` | (1) an outside-check on the string as written, without normalising `..`; (2) an outside-check through `os.path.abspath`, which follows no link (executed, X12: it yields a path that is not under the resolved root) |
| R55-7 | `run_whole_window_verdict`, production path | a record whose `entry_sha256` is wrong (one character of `reason` edited after writing); the quarantined bundle intact | **nothing is raised**; a row is appended with `status` not `passed` and the condition `whole_window_campaign_membership_ambiguous` | a rule that raises custody for every record that fails validation. A malformed record is a record problem, not a custody failure of bundle bytes. |
| R55-8 | `scripts/check_window_provenance.py`, by `git diff --quiet 1417c0c4 HEAD` on the file, and one call of `supersession_entry_validation_results` on the input of R55-5 | | the file is identical to base; the function returns `[False]` for that record, as at `49d77c74` | a fix that changes the existing validation function |

### Amendment 56 (new; amends text 12, the `members` sentence, and the member lists of amendments 49 and 53; S1's existing scope: `scripts/run_campaign.py`, `joulewise/whole_window.py`, `joulewise/analysis_engine/inputs.py`, `tests/test_bfgs_window_consumers.py`)

56. **A bundle that a record proves was written is never dropped from the gate's list because its directory is gone.**

**The forcing problem.** Window consumers build their lists partly by asking the disk (`if path.is_dir()`, a directory listing). A bundle deleted after it was measured is then simply not there, and what is not there is not checked. On the real `load_analysis_inputs`, deleting one registered member's directory changes the gate's list from 30 members to 29; the function returns and the member is marked `bundle_missing` (executed, X3, X4). The gate, handed the same path, raises a custody failure.

**(a) Finalization record.** A record is a finalization record of a bundle if it holds a SHA-256 of at least one of that bundle's own files, or states that the run finalized. The kinds, at `49d77c74`:

1. a supersession record: its three `quarantine` digests (they name the quarantined bundle);
2. a row of `evaluation_basis.member_occurrences` in a row of record type `idle_admission_whole_window_verdict` of the window's campaign log, when at least one of its `config_sha256`, `metadata_sha256`, `summary_sha256` is not null (`run_campaign.py:5961-5985` writes null for a file it could not read); it names the bundle at `<runs directory>/<bundle_path>`;
3. a row of the attempt ledger (`attempt_ledger.jsonl`, the file that lists every attempt of the speculative-decoding campaign) whose `run_id` is not null: the collection loop sets `run_id` only when the attempt finalized (`run_campaign.py:7668-7670`).

**(b) The rule.** A directory test or a directory listing may **add** a member to a window consumer's list. It may never **remove** one that a finalization record names. `bundle_missing` and `terminal_absent` remain the outcomes for a member that no finalization record names: that is a run that was planned, or started, and never wrote a bundle.

**(c) The sites.**

1. **`load_analysis_inputs`** (`inputs.py:3128-3140`). `joulewise/whole_window.py` gains `recorded_member_paths(runs_root, log_path=None) -> frozenset[str] | None`, exported in `__all__`: the set of `bundle_path` strings of every kind-2 row in the window's campaign log, read with the same reader and the same fail-closed rule as `supersession_entry_validation_results` (`None` when the log cannot be read; the empty set when there is no log). A registered entry whose path relative to the runs directory is in that set is added to the gate's list **whether or not its directory exists**. A registered entry not in the set, whose directory is absent, is omitted from the list and becomes `bundle_missing`, as today. When the function returns `None` nothing is added, and the existing refusals stand.
2. **`run_campaign`, final analysis.** Amendment 53 (b).
3. **`_authenticate_whole_window_members` and `_derived_neg8_decision`.** For every member id of the window that the resolver reports `terminal_absent`, if `<bundle id>` is in `recorded_member_paths(runs_dir, log_path)`, the path `runs_dir / <bundle id>` is added to the gate's list. Every selected path is passed without a directory test, as the helper does today.
4. **The attempts of the speculative-decoding campaign** (amendments 49 (b) 3 and 49 (e)). The list is the union of what the disk shows and the bundle of every kind-3 ledger row. **I did not read how a ledger row maps to its bundle's path.** The seat uses the function by which the collection loop chose the directory it wrote the attempt to. If no function yields that path from a ledger row without listing a directory, the seat finishes the independent work and returns NEEDS_RULING with the layout.

**(d) Two fences.**
- This amendment does not touch the salvage exclusion (`authorize_salvage_dangler_exclusion`), which lets a window proceed without one run that never wrote a bundle. No finalization record can name such a run. If the seat finds a finalization record naming a bundle id that a salvage closure excludes, it returns NEEDS_RULING. I did not read the salvage rules.
- Digests of kind-2 rows are **not** handed to the gate as `recorded`. Whether a present member whose bytes differ from an earlier verdict row's digests is a custody failure at the gate, or stays with the existing check in `_validated_evaluation_basis`, is not ruled here. This amendment covers absence only.

**(e) The ruled operator workflow still runs.** Quarantine, rerun, record: the rerun's final analysis keys on the evaluations of its own invocation (53 (b)), and the first run, moved aside before the rerun started, is not among them. A kind-2 row written before the quarantine names the canonical path, where the rerun's bundle now stands.

**Test rows for amendment 56.**

| Row | Production call site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R56-1 | `load_analysis_inputs`, production path | a corpus whose campaign log holds a whole-window verdict row naming member M in its evaluation basis with digests; M's directory deleted | `CustodyUnreadable`; `exc.window_member` is M's relative path | the code at `49d77c74`, which returns and marks M `excluded`, `bundle_missing` (executed, X4) |
| R56-2 | same | the same corpus, plus a registered entry that no record names and that has no directory | the function does not raise on that entry; it is `excluded`, `bundle_missing` | a fix that removes the directory test for every entry, which would make every unfinished campaign a custody failure |
| R56-3 | `run_campaign` | row R53-4 | as R53-4 | as R53-4 |
| R56-4 | `run_whole_window_verdict`, production path | the log holds an earlier verdict row naming member M with digests; M's directory is then deleted | `CustodyUnreadable` naming M; no row appended | a list built from the resolver's selected paths only, in which M is `terminal_absent` (read, NOT EXECUTED) |
| R56-5 | `run_axi_spec_campaign`, closing analysis | two attempts finalized and in the ledger; the directory of the one not selected deleted before the closing analysis | `CustodyUnreadable` naming that attempt's physical id | a list built from `_axi_discover_finalized_bundles` alone, which lists the disk (`run_campaign.py:7114-7135`, read). NOT EXECUTED. |
| R56-6 | `whole_window.recorded_member_paths` | a log with one verdict row whose basis has two rows, one with all three digests null | the set holds the other row's path only | a function that treats every basis row as proof of a bundle |

---

## 11. Kept intact

- **Custody is never a status.** RB-1 showed this was false on the production path at `49d77c74` and would have stayed false under amendment 49 as first ruled (X1). Amendments 49 (c) and 55 make the quarantined bundle's custody the gate's to raise. Amendment 56 does the same for a recorded member that was deleted. Amendment 52 (g) names the one place outside the eight consumers where the conversion remains, gives it a lane and a test that fails if a second such place appears. No amendment adds a status, a condition string or a reason code.
- **Authentication precedes every exclusion decision.** Item 4 of amendment 49 (b) is built from field-valid records, not from the resolver's outcome, and the gate call precedes the appending of any row and the assignment of any reason (49 (c)). `load_analysis_inputs` calls the gate as its first act after loading the manifest. Amendment 53 moves no exclusion ahead of authentication.
- **`joulewise/battery_float.py` is byte-identical** to `1417c0c4` (X10, SHA-256 prefix `4b4d7bb20625`). Amendment 55 uses its two exception classes and edits nothing in it.
- **FT §E's excluded list is byte-identical**, and no amendment names a path on it for editing. `joulewise/reduce.py` is on that list; amendment 51 says a site reported there is allowlisted or returned, never edited.
- **The eight consumers do not import `battery_float`** (X10). Amendment 55 (c) is written so that they need not: the digest comparison and both exception constructions are in `bundle_read.py`.
- **The historical set's 69 entries, bytes and pin are unchanged** (X10).
- **No path is added to S1's WRITE_SCOPE.** `joulewise/analysis_manifest_v3.py` and `scripts/check_window_provenance.py` are not edited.

---

## 12. Not executed

- **RB-1 at `load_analysis_inputs` and at `_derived_neg8_decision`** (rows R49-7b, R49-8b). Established by reading. No fixture I found builds an analysis corpus whose campaign log holds a supersession.
- **RS-3 at `run_campaign`'s final analysis and at the speculative-decoding campaign** (rows R53-4, R56-4, R56-5). Established by reading.
- **Whether, with one member deleted, the remaining members yield a number** (X4's limit).
- **A window passing, then failing**: in X1 the baseline is `failed` for fixture reasons in every scenario.
- **Any code written to amendments 49 to 56.** I ruled from probes of the code as it stands.
- **The prototype detector re-run under the new rules of amendment 51 (c) and (d).** X5 shows the old rules silent; X7 sizes the change; rows R51-18 to R51-22 are the test.
- **The guard suite** under amendments 52 (f) and 55 (d).
- **The callers of `validate_finalized_analysis_manifest_v3`**, which is why RS-2 is a lane.
- **The mapping from an attempt-ledger row to its bundle path; the salvage rules.** Amendment 56 (c) 4 and (d) say where the seat returns.
- **A symlink in a parent component** of a quarantine path. Still open from the first ruling.
- **The full S1 suites** V1, V2, V3, and the Opus lens's mutants, on whose report rows R52-4, R52-5 and R53-2 rely.
- **RN-3's example site**: I confirmed by search that `scripts/check_window_provenance.py` names `gross_energy_j` (`:747`); I did not trace where its output goes.

---

## 13. Probes written in this session

| File | Purpose |
|---|---|
| `/tmp/cg_r2e/rb1_prod.py` | X1, X2: supersession on the production path, six scenarios |
| `/tmp/cg_r2e/upgrade.py` | gives a fixture bundle a real battery pair (used by both probes) |
| `/tmp/cg_r2e/rs3_inputs.py` | X3, X4: `load_analysis_inputs` with one registered member deleted |
| `/tmp/cg_r2e/try_size.py` | X7: size of the new dominance rule |

Re-run from the refuter's scratch, unchanged: `/tmp/oc2/sweep_holes.py` (X5), `/tmp/oc2/gate_try.py` (X6), `/tmp/oc2/q2.py` (X8).

---

## 14. The S1 order of remaining work

| Step | Round | Contents | Ends with |
|---|---|---|---|
| 1 | **Fix round 3** (one seat, S1's existing WRITE_SCOPE, no path added) | In this order, because each later item builds on the code the earlier ones change: **(i)** amendment 54 (two test rows); **(ii)** amendment 50 (the reducer and its fixture producer; R50-8 with the corrected count); **(iii)** amendment 55 (the gate's three-element member; `supersession_record_field_valid`), first of the production work because 49 and 56 call it; **(iv)** amendments 53, 49 and 56 together (the gates of `run_campaign.py`; item 4 from field-valid records in the three resolvers; `recorded_member_paths`; the lists that no longer depend on a directory test); **(v)** amendment 52 (`GATE_EXCEPTIONS`, the pass-through clause, the handlers restored to their base types, the named residual and row R52-6); **(vi)** amendment 51 (the detector with the reader binding and the new dominance rules; the re-keyed allowlist; the classification of every reported row; every `non_claim` (ii) reason naming its outputs), last among production-facing work; **(vii)** the test fixes of the first ruling's §9 (S-3, S-4, S-5, N-1 to N-4, N-8), unchanged. | every row R47-4 to R56-6 shown RED under its counterfactual and GREEN after (rows R49-10, R49-11 and R55-8 are GREEN today and are shown RED under a mutation); V1 and V2 green; the builder's forward check `byte-identical entries=69`; the count of reported sweep rows stated; the allowlist listed in the report with class and reason per row |
| 2 | **Delta lenses on fix round 3** | two lenses with distinct methods. The contract lens checks **every allowlist row** against amendment 51 (f) and (g), searching the tree for readers of every output a `non_claim` (ii) row names; re-runs the Opus mutants M4b, M4c, M5, M5d, M7 and T10-M1, all of which must now be killed; and drives rows R49-3b, R49-3c, R49-3d and R56-1 itself on the production path. | findings, or none |
| 3 | **Round F** | amendment 38, unchanged: the fourteen test files, remedies R1 to R3. Three notes: fixtures that drive a simulated campaign through its final analysis meet the refusal of amendment 53 (e), and are repaired with bundles that carry a real battery pair, never by putting a gate back into collection; fixtures of the scored reducer use amendment 50 (g); `IdleAdmissionCoreVerdictTests`' supersession tests (X11) need the same battery pair before they can reach the verdict. | the full suite green except the four cases that fail at base; the F-6 counterfactuals and the F-7 partition |
| 4 | **Last commit** | the supply-map receipt clause of amendment 38 | the generator command and the diff pasted |

Early returns, as before: a text here that conflicts with the code, or a guard that goes red under amendment 52 or 55, or either stop named in amendment 56 (c) 4 and (d), is returned as NEEDS_RULING with the independent work finished first.

## 15. What becomes its own lane

| Lane | Why it is not in S1 | Contents | Must close before |
|---|---|---|---|
| **BFGS-MANIFEST-CUSTODY-01** (proposed name; the lead registers it) | `joulewise/analysis_manifest_v3.py` is outside S1's WRITE_SCOPE, and the public validator's contract is to return refusals, so the change alters what its callers receive (§6.2) | (1) read every caller of `finalize_prospective_analysis_manifest_v3` and `validate_finalized_analysis_manifest_v3`; (2) rule whether the gate's exceptions leave both functions unchanged, by a cold gate if the validator's contract changes; (3) the pass-through clause of amendment 52 (c) at `:3712`, at every handler between `:4379` and the unchecked validator's return, and at `:4499`; (4) a row at each production call site: a member with a deleted battery reading gives `CustodyFailure`, not `analysis_finalization_attachment_invalid`; (5) empty the constant `NAMED_RESIDUALS` of row R52-6 | any analysis manifest is finalized or validated over a bundle measured after S1 merges |
| **SCORED-CEILING-BATTERY-01** (existing) | unchanged from the first ruling | what it costs a scored campaign that a run killed before writing a bundle refuses the reduction (amendment 50 (f)) | the scored reducer gets a production caller |

Two questions this erratum leaves open and names, for the lead to queue or drop: whether an unreadable campaign log should be a custody failure (49 (b)); whether a present member whose bytes differ from an earlier verdict row's digests should raise at the gate (56 (d)).

---

## 16. Plain summary for Ed (5 lines)

1. **The reviewer's one blocking finding ("RB-1") is real, and I reproduced it by running the actual commands, not a mock-up.** When a run is repeated, the first attempt's folder is moved aside and a log entry records where it is and the checksums of its files. If that folder is later deleted or altered, the system raises no alarm: it writes a result row marked "failed" with the note "membership ambiguous". The rule "lost or altered evidence is a hard stop that names the file, never a status label" ("custody is never a status") was broken there. No wrong number gets out, since the row is a failure either way.
2. **The fix splits one check into two ("amendment 55", new).** Whether the log entry is well-formed is read from the entry itself; whether the moved-aside folder still matches its recorded checksums is checked by the battery check ("the gate", the one function every number-producing program must call first), which stops everything and names the folder.
3. **The same hole existed for ordinary runs, and is closed the same way ("RS-3", "amendment 56", new).** Programs built their list of runs to check by asking the disk which folders exist, so a deleted run was simply never checked; I ran the real analysis loader and watched its list go from 30 runs to 29. Now any run that an earlier record proves was written must still be there, or the computation stops. A run that was planned and never made stays an ordinary "missing".
4. **The automatic code scan ("the sweep", a test that finds file reads not preceded by the battery check) had three more blind spots, all upheld ("RS-1", "RS-5").** It accepted a check whose failure was caught and discarded, a read placed in the very error handler that runs when the check fails, and a check on one run followed by a read of another. One further module outside this work package converts the hard stop into an error code ("RS-2"); it still refuses, so it becomes its own small follow-up task, with a test that fails if a second such module appears.
5. **One proposed rule is rejected ("RS-4"); the four minor notes are accepted.** The reviewer was right that a repeat run's own end-of-collection report never sees the first attempt, but that report licenses nothing: I confirmed no other program reads it, and that a session with a repeated run and no log entry cannot pass. Both facts now have tests. Next: one fix round covering amendments 49 to 56 in the order of section 14, a review of it, then the repair of older test fixtures.
