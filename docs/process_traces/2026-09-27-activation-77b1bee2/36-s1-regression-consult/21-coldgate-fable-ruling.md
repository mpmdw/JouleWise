RULING: S1-REGRESSION-01 ISSUED

# Cold gate S1-REGRESSION-01 — how S1 closes its full-suite regression

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, one foreground session, no subagents, no background tasks. Session 2026-09-27, 17:11 to 17:22 PDT by the host clock. Python was `/opt/homebrew/bin/python3 -B`. Scratch is under `/tmp/cg-s1reg-77b1bee2/`. No file in any repository was modified; this file is the only file written. No process was left running (every command ran in the foreground and returned).

## 0. Contamination disclosure

**Loaded by the harness without my choosing, before my first turn:** the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md` of the worktree I was started in, and the memory index `MEMORY.md` (one-line pointers, several of which name loop context such as checkpoints, directives and model assignments). A system reminder also supplied the git status and five commit subjects. I used none of this for any ruling below. One exception is stated openly: the global file's writing standard (define each term at first use) matches what I would do anyway, and this text follows it.

**Not opened by me:** `RUN_STATE.md`, `TASK_QUEUE.md`, any `CLAUDE*.md`, `AGENTS.md`, any memory file, any skill file, the decision log.

**Read by me:** the charge; the scout report and its inventory; the three consult seats (Sol, Astra, Opus), in full; Final texts v1.1, in full; the final-pass ruling and the SWEEPCLASS ruling by targeted search only; the row-9 log; and the code named under Executed evidence. The three seats were read **before** I formed my own view, so my view is not blind to theirs. Each seat claim I rely on is marked below as re-executed by me, confirmed by my reading, or taken from the seat.

## 1. Terms used in this ruling

- **S1.** The pull request that makes every reader of a measurement bundle check the bundle's battery evidence first. Head `c7593edb`.
- **Bundle.** One run's directory: `config.json`, `metadata.json`, `events.jsonl`, the power trace and the summary.
- **Battery pair.** Two recorded readings of the laptop battery, one before and one after the measured span, each with the raw `ioreg` bytes and their digest. The pair shows whether the battery was charging, which would add energy the meter attributes to the workload.
- **Verdict statuses.** `pass` (pair authenticated, battery at float); `battery_float_confounded` (charging); `battery_float_evidence_missing` (no usable pair); `unobserved_historical` (an old bundle on a closed, digest-pinned list); `not_applicable` (the bundle's digest-bound config names the synthetic `mock` telemetry backend, so no physical energy was measured).
- **The window gate.** The function `authenticate_window_members` in `joulewise/bundle_read.py`. It takes a set of bundles (a **window**) and either returns one verdict per member or raises.
- **Mock bundle.** A bundle whose status is `not_applicable`. **Mock window:** within one call of the window gate, a window with at least one member that owes a pair, where every such member is `not_applicable`. **Mixed window:** at least one `not_applicable` member and at least one member of any other status.
- **Claim artifact.** Any output from which a paper number can be taken: an analysis artifact, a whole-window verdict, a minted or extracted detection floor, a window-duration margin record, a scored reduction, a figure.
- **Full suite.** Every test module, run in six shards; its last line is `WORKERS SUMMARY …`. **Integration tree:** the candidate head merged with main's head.
- **Evidence-forward repair.** A failing test is repaired by giving its fixture the evidence the gate now demands, and the test's assertions stay byte-identical. **Expectation rewrite:** the assertion itself changes. **R-list:** the list, by test ID, of every expectation rewrite, each approved by the lead.
- **Repin.** Replacing a stored digest with the digest recomputed from current bytes.

## 2. Executed evidence (this session, all in the foreground)

| # | Probe | Result |
|---|---|---|
| E1 | `git rev-parse HEAD` on the three worktrees; `git status --short` | S1 `c7593edb…`; integration tree `42e2af3e…`; record tree `91aa2c4b…`. All three clean. `origin/main` = `e7c8bcc6…`. |
| E2 | `git log -1 --format='%h parents: %p' 42e2af3e`; `git merge-base --is-ancestor e7c8bcc6 42e2af3e` | Parents are `c7593edb` and `daaff807`. **`e7c8bcc6` is NOT an ancestor of the integration tree.** The integration tree is S1 merged with main as of pull request 435; main has since gained pull request 436. **The charge's fact "the integration tree is S1 with current main" is therefore inexact by one merge.** |
| E3 | Decompressed `60-row9-integration-FAIL.log.gz`; counted `^(FAIL|ERROR): `; read the summary line | 533 lines. `WORKERS SUMMARY shards=6 modules=270 tests=7647 failures=115 errors=418 skipped=108 … result=FAIL`. **The 115/418 fact is confirmed from the log.** |
| E4 | Parsed `62-regression-inventory.jsonl` | 533 rows, 42 modules; G1 135, G2 98, G3 62, G4 40, G5 81, G6 20, G7 17, G8 10, G9 23, G10 11, G11 36; 418 ERROR, 115 FAIL. Matches the scout. |
| E5 | Recorded main runs: `82-pr435-row9-tail.txt` and `…3ba66eeb/50-census/21-row9-fullsuite-a441703a-tail.txt` | Both: `modules=266 tests=7525 failures=0 errors=0 skipped=109 result=PASS`. **Neither is a run on `e7c8bcc6` itself.** I found no recorded full suite on exactly `e7c8bcc6`. |
| E6 | Read `joulewise/bundle_read.py:282-354` | The window gate appends every `not_applicable` verdict to `refused` (`:344-351`) and raises (`:352-353`). It has no parameter. So its return value can never contain `not_applicable`. |
| E7 | Read `scripts/run_campaign.py:9019-9086` | The gate call (`:9032`) precedes the collection verdict, `claim_bearing` (`:9043`) and `append_verdict` (`:9068`). `battery_float_members` is written from the returned verdicts (`:9083-9085`). |
| E8 | My own script over the row-9 log: for each `not_applicable` refusal, the nearest production frame outside `bundle_read.py` | 44 at `run_campaign.py:9032`; 34 at `inputs.py:3195` (`load_analysis_inputs`); 12 at `aggregate.py:104`; 3 at `inputs.py:2824` (`_read_bundle`); 2 at `whole_window.py:680` (`_prepare`); 2 at `run_campaign.py:7848`; 1 at `run_campaign.py:6256`. Total 98. **Re-executed; equals Opus X3.** |
| E9 | `grep` for every call of the window gate under `joulewise/` and `scripts/` | 24 call sites in 8 files. **Seven are single-member calls** (`inputs.py:2824`, `aggregate.py:155`, `whole_window.py:3640`, `mint_floor_artifact.py:378`, `run_campaign.py:5350`, and the per-record forms), where the "window" the function sees is one bundle. |
| E10 | `grep -i mock` over the eight consumers | An independent mock barrier (`mock_telemetry_claim_ineligible`) exists in `inputs.py:1943-1944`, `:2889-2890` and `floor_extraction.py:1989-1990`. **None exists in `aggregate.py`, `window_duration_margins.py`, `scripts/mint_floor_artifact.py`, `scripts/extract_detection_floors.py` or `scored_reduce.py`.** |
| E11 | Read `whole_window.py:988-1000`; `grep custody_telemetry_identity tests/test_analysis_integration.py`; listed the 35 G2 test names of that module | The barrier's input is `CustodyTelemetryIdentity.mock_config`, computed by `custody_telemetry_identity`. The window gate decides "mock" by a different function, `_digest_bound_mock_config` (`bundle_read.py:503-517`). Ten tests patch `custody_telemetry_identity` to a production identity. G2 tests in this module include `test_attribution_limited_floor_is_claim_bearing_in_final_artifact` and `test_authenticated_v2_whole_window_source_reaches_claim_consumption`: **they are claim-path tests that use mock bundles as stand-ins for real ones.** |
| E12 | `grep aggregate_experiment` | Two production callers: `joulewise/controller.py:3004` (the experiment manifest) and `scripts/make_figures.py:43` (figures). `_read_member` has one caller, `aggregate.py:110`, which runs after the whole-set call at `:104`. |
| E13 | Parsed `configs/paper_supply/supply_map.json`; read `docs/contracts/paper_supply_custody.md:198-206` | Five roles, all named `fixture.*`, all `mode = "test_fixture_non_issuing"`, all `issuance_gate_id = null`. Two `production.*` roles exist only under `pending_roles`, status `pending_desk_day`. The contract says: "The fixed map currently registers five synthetic roles only… These are synthetic authentication controls." **Opus's G9 claim is confirmed.** |
| E14 | Read `tests/fixtures/paper_custody/repin.py:21-30` | The helper assigns `supply['pending_roles']` a dictionary holding **only** the `qwen3-1p7b` role. The map holds two (E13). Running it unchanged deletes the `qwen3-8b` pending role. It also rewrites modes, the source census and one fixture file. **Astra's F5 is confirmed by reading.** |
| E15 | `git log -- configs/paper_supply/supply_map.json` | Earlier repins were made as "hash-only repin" inside the commit series that changed the validator sources (`6e380f55`, `21331ac9`, `31f39466`, `6c34cfe6`). |
| E16 | Read `calibration_bracketing.py:1519-1540`, `:1677-1690`, `:1814-1865`, `:1905-1913`; the row-9 traceback of `test_campaign_core_callers_keep_replacement_custody_replay_only`; `tests/test_run_campaign.py:8080-8097` | The candidate loader resolves custody through `probe_custody(original, inspect, …, mode=mode)`, which in `read_replay` mode can supply a moved copy. The battery classifier reads `Path(observation.custody_locator)` directly and takes no `mode`. The traceback: `discover_calibration_candidates(ledger_snapshot, mode=mode)` → `:1909` → `:1863` → `:1826` raises `CustodyFailure … observed absent` on `…/absent/runs/member/instrument_evidence.json`. The test requires the original to stay absent (`assertFalse(original.exists())`). **Astra's F1 is confirmed: part of G7 is a production regression, not a fixture gap.** |
| E17 | My script: Opus's four-seat module partition against the inventory | Covers all 39 failing modules outside G9; no module in two seats; every file exists; outcome counts A 166, B 104, C 207, D 33 (sum 510 = 533 − 23). **No failing module is inside S1's ruled WRITE_SCOPE.** |
| E18 | `git diff --name-only e7c8bcc6...c7593edb -- joulewise scripts configs` | 16 paths. `joulewise/envelope_gate.py` is outside §E's list; the SWEEPCLASS ruling granted it by name (`…/30-sweepclass-samesig/21-…:279`) and the final pass recorded it (`51-…:59`). No unexplained path. |
| E19 | Read `joulewise/arm_readiness_evidence.py:2446-2466` | The `THREE_WINDOW_REGRESSION` derivation runs `tests.test_calibration_live_three_window` and records `PASS`. That module has 20 errors in the row-9 log (G6). **Opus's claim that G6 blocks the next pack freeze is confirmed.** |

**NOT EXECUTED by me:** any full suite (about one hour; outside the budget); any repair; Opus's in-memory stand-in for its rule (X6) and Astra's relocation probe (V5), which I take from the seats and from E16's log evidence; the claim-readiness value a mock campaign receives at completion; whether the campaign flow reaches the analysis loader in the same process after completion; why the integration run has 108 skips where main's recorded runs have 109; the content of `tests/receipt_corpus.py` beyond one count (it contains no `instrument_evidence` string).

## 3. Ruling 1 — G2: what the window gate does with mock bundles

### 3.1 The contradiction Opus names is real

Text 12 of Final texts v1.1 has two sentences that the code at `c7593edb` cannot satisfy together.

- First sentence: every consumer that builds a set of bundles **whose numbers are claimed** refuses the whole set on any `not_applicable`.
- Last sentence: "`unobserved_historical` and `not_applicable` are visible in every window-level output."

S1 implemented one function with one behaviour and called it from every consumer (E6, E9). Under that function no window-level output is ever produced from a window holding a `not_applicable` member, so `not_applicable` is visible in none (E6, E7). The last sentence is met only if some window-level output exists that the first sentence does not govern: the output of a set whose numbers are **not** claimed. Text 12 names, for `scripts/run_campaign.py`, "its final analysis and whole-window verdict". It does not name the campaign's completion record. **S1's gate at `run_campaign.py:9032` is stricter than text 12 and is what breaks the last sentence.** Text 18 ("a MOCK bundle reduces as today") points the same way.

### 3.2 Why none of the three seat proposals is adopted as written

**Sol (strict everywhere, tests changed): REJECTED.** A mock campaign is the only campaign that can run end to end without hardware. If completion refuses it, every test of what happens after completion (collection verdict, member classification, the completion record) loses its hermetic input, and a subprocess cannot be handed a fake battery probe without a new production hook. That deletes coverage at scale. It also leaves text 12's last sentence unmet.

**Opus (rule 12a decided by the data, in all 24 call sites): REJECTED as written.** Three defects, each found by reading the code.

1. **It relaxes consumers that have no second barrier.** Opus's safety argument is that mock numbers carry an independent claim lock. That lock exists in the analysis loader and in floor extraction only (E10). The floor minter, the floor extractor, the window-duration margins, the aggregate and the figures script have none. Under a data-decided rule an all-mock window would pass the battery gate in each of them with nothing behind it. No failing test needs that relaxation: G2 has no outcome in any of those consumers except the aggregate (E8).
2. **Where the second barrier exists, it is decided by different code.** The gate decides "mock" with `_digest_bound_mock_config`; the barrier decides it with `custody_telemetry_identity` (E11). At `c7593edb` a mock bundle is stopped on a claim path by both. Under Opus's rule it is stopped by one. Ten existing tests already replace that one with a production identity (E11); under Opus's rule those tests would build claim artifacts from mock bundles with the battery gate satisfied by the mock route. That is one barrier fewer on a claim path, which the charge forbids.
3. **Single-member calls cannot see a mixed window.** Seven call sites pass one bundle (E9). To the function, one mock bundle is a mock window. Under a data-decided rule each of those sites admits a mock member of a mixed window; the protection against mixing then rests entirely on a whole-set call earlier in the same flow, which the rule does not require.

Opus's own condition M-4 ("if any writer emits a claim artifact from a mock window, that consumer passes `strict=True`") concedes the point: the rule ends with a per-consumer keyword anyway, but with the unsafe value as the default.

**Astra (one non-claim completion branch in `run_campaign.py`, the gate unchanged): closest, ADOPTED IN SUBSTANCE**, with two changes: the admission lives in the gate function behind a keyword, so the mixed-window rule and the custody raises are the same code for every caller; and the experiment aggregate is covered, which Astra's branch leaves failing (12 outcomes, E8).

### 3.3 The rule, as ruled: text 12a

> **12a. Mock window (amends text 12; every other sentence of text 12 stands).**
>
> **(a) Definition.** Within one call of `authenticate_window_members`, the *obligated members* are the members for which the function computes a verdict, that is, every member except one whose parsed journal shows no `idle_baseline` stage start. The call holds a **mock window** when it has at least one obligated member and the verdict of every obligated member is `not_applicable` under text 8 (iii).
>
> **(b) Signature and behaviour.** `authenticate_window_members(members, *, admit_mock_window: bool = False)`.
> With the default, behaviour is exactly that of `c7593edb`: any `not_applicable` member refuses the window.
> With `admit_mock_window=True` **and** a mock window, the function returns its verdicts without raising.
> With `admit_mock_window=True` and any other window, behaviour is exactly that of the default: a mixed window raises `WindowBatteryRefusal` naming every `not_applicable` member together with every `battery_float_confounded` and `battery_float_evidence_missing` member.
> `CustodyFailure` and `CustodyUnreadable` propagate in every case. The keyword changes nothing else.
>
> **(c) Closed list of call sites that pass `True`.** Exactly two flows, and no other:
> 1. the campaign completion call in `scripts/run_campaign.py`, function `run_campaign` (line 9032 at `42e2af3e`);
> 2. `joulewise/aggregate.py`: `aggregate_experiment(runs_root, manifest, *, admit_mock_window: bool = False)` forwards its keyword to its whole-set call (`:104`) and to `_read_member` (`:155`); **only** `joulewise/controller.py:3004` (the experiment manifest) passes `True`. `scripts/make_figures.py` passes nothing and stays strict.
>
> Every other call site passes nothing and stays strict: `joulewise/analysis_engine/inputs.py` (`:1894`, `:2824`, `:3195`), `joulewise/whole_window.py` (`:680`, `:3640`, `:3791`, `:4078`), `joulewise/floor_extraction.py:2883`, `joulewise/window_duration_margins.py:950`, `scripts/mint_floor_artifact.py` (`:378`, `:458`, `:1020`), `scripts/extract_detection_floors.py:142`, `scripts/run_campaign.py` (`:5350`, `:6256`, `:7848`). Text 9 is unchanged: the scored reducer refuses `not_applicable`. A site is added to the closed list only by cold gate.
>
> **(d) What an admitted mock window may produce.** The campaign completion record and the experiment manifest's aggregate block, each carrying `battery_float_members` with every member shown as `not_applicable` (this is text 12's last sentence, now satisfiable). **No claim artifact.** The completion record of an admitted mock window must not report claim readiness as satisfied. If the code at `c7593edb` would report it satisfied, the production seat adds the reason `mock_telemetry_claim_ineligible` to claim readiness in the same edit and reports which case held (NOT EXECUTED by me).
>
> **(e) Pin.** A sweep test over the syntax trees of tracked `*.py` under `joulewise/` and `scripts/` asserts that the set of (file, enclosing function) pairs that pass `admit_mock_window` equals the closed list of (c), and flags any value that is not the literal `True` or the forwarded parameter of `aggregate_experiment`.

**Why this keeps every claim-bearing path strict.** Every consumer that writes a claim artifact keeps the behaviour of `c7593edb` with no byte changed at its call site. The default is the strict value, so a consumer written later is strict unless a cold gate says otherwise. The two admitted outputs are operational records; each names its members as `not_applicable`. A mixed window refuses everywhere. The status itself is still decided from the config whose digest `metadata.config_sha256` binds, so a bundle cannot be relabelled "mock" without changing its digest.

**Size.** About 10 lines in `bundle_read.py`, 4 in `aggregate.py`, 1 in `controller.py`, 1 in `run_campaign.py` (plus (d) if needed). All four files are inside S1's ruled WRITE_SCOPE.

### 3.4 What 12a does not clear, and how those tests are repaired

12a clears the refusals whose frame is `run_campaign.py:9032` or `aggregate.py:104` (56 of the 98, E8), subject to what each test meets next. The other 42 sit on claim paths (`inputs.py`, `whole_window.py:680`, `run_campaign.py:6256` and `:7848`) and **stay refused**. They are repaired in the test, one of two ways:

- **The test's subject is a claim computed from stand-in bundles** (for example `test_attribution_limited_floor_is_claim_bearing_in_final_artifact`). Evidence-forward: the fixture is given a non-mock telemetry config, a rebound `metadata.config_sha256`, agreeing backend labels in metadata and summary, and an authenticated passing battery pair. Assertions stay byte-identical.
- **The test's subject is the refusal of mock bundles on a claim path** (for example `test_named_strata_manifest_preserves_terminal_mock_refusal`). R-list: the test asserts `WindowBatteryRefusal`, the member label and the status `not_applicable`. The old assertion on `mock_telemetry_claim_ineligible` moves to a sibling test that calls the barrier's own function directly, so the barrier keeps its coverage.

A seat that finds the first form infeasible for a named test returns `NEEDS_RULING` with the test ID. It does not extend the closed list.

### 3.5 Defect-shaped tests owed with 12a

Each row names the planted defect that must turn it RED. All live in `tests/test_bfgs_window_consumers.py` except T12a-9.

| Id | Input | Must observe | Planted defect that must turn it RED |
|---|---|---|---|
| T12a-1 | Keyword `True`; one mock member and one real member with a passing pair | `WindowBatteryRefusal` naming the mock member, status `not_applicable` | `all` replaced by `any` in the mock-window test |
| T12a-2 | Keyword `True`; one mock member and one `unobserved_historical` member | Refusal naming the mock member | the mock-window test counting only refused members |
| T12a-3 | Keyword `True`; no obligated member | Returns `{}` | none (pins today's behaviour) |
| T12a-4 | **Default**; an all-mock window driven through the public entry of each strict consumer: `load_analysis_inputs`, the whole-window verdict (`_prepare`), floor extraction, the floor minter, the floor extractor, window-duration margins, and `aggregate_experiment` called as `make_figures.py` calls it | Refusal in every one; no claim artifact file written | the keyword's default flipped to `True` |
| T12a-5 | Keyword `True`; a mock bundle whose `config.json` has one byte changed after binding | Refusal, `battery_float_evidence_missing`, reason "not bound" | the config digest comparison removed |
| T12a-6 | Keyword `True`; a bundle with a non-mock config that carries the marker `{"pre": null, "post": null, "not_applicable": "mock"}` | Refusal | the backend comparison removed |
| T12a-7 | Keyword `True`; an all-mock window with one member directory lacking `metadata.json` | `CustodyUnreadable` naming that member | the custody raise moved after the mock-window return |
| T12a-8 | A mock experiment and a mock campaign, end to end (the campaign in a subprocess) | `battery_float_members` shows every member `not_applicable`; claim readiness is not satisfied; **the mock barrier function is not patched in this test** | the visibility field dropped from either record |
| T12a-9 | The sweep of 12a (e), in `tests/test_bfgs_consumer_sweep.py` | Equal to the closed list | self-test: the keyword added at `inputs.py::load_analysis_inputs` is reported |
| T12a-10 | Keyword `True` on a single-member call outside `aggregate.py` | Does not exist in the tree (T12a-9); and a mixed experiment refuses at `aggregate.py:104` before `_read_member` runs | `aggregate.py:104` call removed |

## 4. Ruling 1b — G7 holds a production regression (text 10a)

The scout classed G7 as fixture-only. It is not (E16). Custody that has been moved to a backup root is a real state of this project; replay of such custody passed on main and raises on S1.

> **10a. Custody resolution for the battery classifier (amends the first sentence of text 10; the rest of text 10 stands).** `_battery_classification_for_observation(observation, *, mode)` obtains the capture directory through the same resolver the candidate loader uses (`probe_custody(original, inspect, …, mode=mode)`, `calibration_bracketing.py:1519-1540`), not by reading `observation.custody_locator` directly. In mode `issuing` only the original locator is read, as at `c7593edb`. In mode `read_replay` the resolver may supply a moved copy, and `instrument_evidence.json` and both raw battery files are read from that one directory. In both modes the evidence bytes must hash to `observation.artifact_sha256["instrument_evidence.json"]`, else `CustodyFailure`; no resolvable directory is `CustodyFailure`. `mode` is passed from `discover_calibration_candidates` and from each caller of the classifier (`:2260`, `:2289`, `:2833` at `42e2af3e`); no site defaults it silently to `read_replay`.

Tests owed, in `tests/test_bfgs_calibration_bracketing.py`: (a) `read_replay`, original absent, moved copy holds digest-matching evidence with a passing pair: the candidate is discovered; (b) the same in `issuing`: refused; (c) the moved copy with one evidence byte changed: `CustodyFailure`; (d) the moved copy with a raw battery file deleted: `CustodyFailure`; (e) the moved copy with a charging pair: excluded as `battery_float_confounded`, discovery for other observations unchanged. Planted defect for (b): `mode` hard-coded to `read_replay`.

**One open point, returned to the lead.** The existing test's `issuing` sub-case expects the condition `calibration_ledger_custody_invalid` and no exception. Under text 10 an absent original in `issuing` mode is `CustodyFailure`. Which of the two the campaign core reports is an R-list decision for that one test; the production seat reports what each choice costs, and the lead approves one. Text 10's `CustodyFailure` is the default if no report is made.

The other 12 G7 outcomes (`test_calibration_bracketing`, `test_epoch_continuation`) use invented digests (`cdcd…`, `800b…`) with no bytes behind them (E4 rows). They are fixture gaps and are repaired evidence-forward.

## 5. Ruling 2 — G9: the paper supply-map pins

**Are they synthetic fixtures? Yes (E13).** All five registered roles are `fixture.*`, `test_fixture_non_issuing`, with no issuance gate. No production role has been issued. **No real paper receipt is invalidated by S1.** The pins went stale because each receipt digest covers the source text of the validator's owning modules, and S1 changed `inputs.py` and `whole_window.py`. That is the tripwire working as designed.

- **Who.** The lead, at the bench. The change is three roles' recomputed digests; a delegated seat would cost more to brief than the work.
- **When.** As the **last commit before the full suite**, after every production byte is final (12a, 10a, and any ruled fix). If any later commit changes a byte in an owning module, the repin is redone before the next full suite.
- **Where.** In S1's own pull request. A separate pull request cannot be right before S1 merges (the digest needs S1's bytes) and leaves main red if it lands after (E15 shows this is the established practice).
- **How.** By a scratch script kept in the trace directory, which calls the custody module's own digest functions and rewrites **only** `expected_sha256` values. **`tests/fixtures/paper_custody/repin.py` must not be run**: it deletes the `qwen3-8b` pending role (E14).
- **Review, mechanical, by the delta refuter, who recomputes independently:**
  1. **Both directions.** Run on main's tree, the script reproduces main's current pins exactly. Run on the candidate, it produces the new ones.
  2. The diff of `supply_map.json` changes only `expected_sha256` values under `fixture.d165_closeout`, `fixture.reported_energy_parents` and `fixture.whole_window_verdict` (receipt and inventory). Both `pending_roles`, every mode, every `issuance_gate_id`, every subject, every source census and the two other roles are byte-identical.
  3. The source census still lists every owner it listed on main; no owner was removed to make a digest match.
  4. The 23 G9 outcomes turn GREEN and no other `test_paper_*` result changes. The existing refusals for a stale source and a tampered receipt still fire.
- **Standing note.** From the day a `production.*` role is issued, a source change invalidates a real receipt. A repin is then a re-issuance under that role's issuance gate, not a hash edit. This sentence goes in the pull-request description.

## 6. Ruling 3 — scope

§E of Final texts v1.1 is exhaustive, and **no failing module is inside S1's ruled WRITE_SCOPE** (E17). So the grant must name every file. The production files of 12a and 10a (`joulewise/bundle_read.py`, `joulewise/aggregate.py`, `joulewise/controller.py`, `scripts/run_campaign.py`, `joulewise/calibration_bracketing.py`) are already in S1's scope and need no grant; they are limited here to the edits of 12a and 10a.

**GRANTED, by exact path, for this repair only:**

```text
configs/paper_supply/supply_map.json            (expected_sha256 values of three roles only; §5)
tests/bfgs_fixtures.py                          (new)
tests/test_bfgs_fixtures.py                     (new)
tests/test_run_campaign.py
tests/test_analysis_integration.py
tests/test_analysis_finalizer.py
tests/test_analysis_claims.py
tests/test_collector_analysis_manifest_id.py
tests/test_experiment.py
tests/test_pipeline_smoke_tail.py
tests/test_corpus_strict_validation.py
tests/test_floor_extraction.py
tests/test_mint_floor_artifact.py               (§E-excluded; condition below)
tests/test_mint_floor_artifact_generalized.py   (§E-excluded; condition below)
tests/test_floor_mint_estimator.py
tests/test_detection_floor.py
tests/test_d117_floor_qwen25_1p5b_plan.py
tests/test_d117_floor_qwen25_7b_plan.py
tests/test_uncertainty_p2029.py
tests/test_aggregate.py
tests/test_custody_mode_inventory.py
tests/test_whole_window.py
tests/test_whole_window_selection.py
tests/test_d165_dominance_closeout.py
tests/test_dominance_closeout.py
tests/test_check_window_provenance.py
tests/test_bracket_binding_cli.py
tests/test_calibration_live_three_window.py
tests/test_calibration_bracketing.py            (§E-excluded; condition below)
tests/test_epoch_continuation.py
tests/test_p2038_production_path.py
tests/test_window_duration_margins.py
tests/test_phase_share.py
tests/test_launch_window.py
tests/test_arm_readiness_evidence_author.py
tests/test_arm_readiness_dry_run.py
tests/test_cli_run.py
tests/test_cli.py
tests/test_audit_amplification.py
tests/test_powermetrics.py
tests/test_package_bundle_pack.py
tests/test_partial_record_enclosure.py
```

**Condition on the three §E-excluded test files.** §E kept them byte-identical so that S1 could not make itself pass by editing the tests that pin older behaviour. That purpose is kept this way: **in those three files the R-list is empty.** Only fixture construction may change; every assertion is byte-identical to main, shown by the assertion census (§7.3 check 1). A test there that cannot pass without a changed assertion returns `NEEDS_RULING`.

**REFUSED:** `tests/receipt_corpus.py` (no seat showed a repair that needs it; it holds no `instrument_evidence` string); `tests/fixtures/paper_custody/repin.py` and `tests/test_paper_custody.py` (the repin needs neither; the helper's defect goes to a lane, §7.5); `tests/test_calibration_ledger.py`; `configs/battery_float/historical_bundles.json` and its builder (the historical set stays closed); every `configs/campaigns/d117_*` tree; every file under `configs/calibration/`; `joulewise/reduce.py`, `joulewise/bundle.py`; the four raw-capture tripwire scripts. **What follows from a refusal:** a seat that needs a refused or unnamed path stops and returns the exact path and the test that needs it; the lead brings it to a cold gate. Nothing is inferred from a failing test.

## 7. Ruling 4 — the repair plan

### 7.1 Is Opus's plan ordered? Yes, with four corrections

1. Its step 0 lands a rule this gate rejects as written; 12a as ruled (§3.3) and 10a (§4) replace it.
2. It treats G7 as fixture-only; §4 corrects that.
3. It gates on a skip **count**; this gate requires the skipped test **IDs** (check 8), because a new skip can hide behind a removed one (108 against 109 is already unexplained, E3, E5).
4. It merges the candidate with "current main" once; main moved during this very consult (E2), so the merge is rebuilt at every gate.

### 7.2 Steps, seats and WRITE_SCOPEs

Every seat works in its own linked worktree from the head named. Scopes are exhaustive.

| Step | Seat | Base | WRITE_SCOPE | Output |
|---|---|---|---|---|
| 0 | Lead, bench | — | none | **Reference run:** the full suite on main's exact head, same host, same `TMPDIR` form as every later run; record the head, counts, and the list of skipped test IDs. The assertion census of main (check 1). |
| 1 | **P**, production, one seat | `c7593edb` | `joulewise/bundle_read.py`, `joulewise/aggregate.py`, `joulewise/controller.py` (the one keyword at `:3004`), `scripts/run_campaign.py`, `joulewise/calibration_bracketing.py`, `tests/test_bfgs_window_consumers.py`, `tests/test_bfgs_calibration_bracketing.py`, `tests/test_bfgs_consumer_sweep.py` | 12a and 10a with T12a-1 to T12a-10 and 10a (a) to (e); the report on 12a (d) and on §4's open point |
| 1′ | **H**, fixture helper, one seat, parallel with P | `c7593edb` | `tests/bfgs_fixtures.py`, `tests/test_bfgs_fixtures.py` | Functions: write a passing pair; write a charging pair; rebind a config (rewrite `config.json`, `metadata.config_sha256` and the backend labels together); write parseable capture evidence with its digest and pair; a deterministic injected battery runner. `tests/battery_float_fixture.py` is read, not edited. The helper's own tests are counterfactual: a helper bundle passes the gate; one raw byte flipped raises `CustodyFailure`; the charging pair gives `battery_float_confounded`; a config byte changed after binding refuses. |
| 2 | Lead, bench | P + H merged | none | Checks 3, 4, 5 (G2 row), 7 on the merged head. No gate is charged yet. |
| 3 | **A**, campaign and analysis | step-2 head | the 8 files `tests/test_run_campaign.py` … `tests/test_corpus_strict_validation.py` (first block of §6) | Repairs; R-list by test ID |
| 3 | **B**, floor and mint | step-2 head | the 10 files `tests/test_floor_extraction.py` … `tests/test_custody_mode_inventory.py` | Repairs; R-list (empty for the two minter files) |
| 3 | **C**, whole window and calibration | step-2 head | the 15 files `tests/test_whole_window.py` … `tests/test_arm_readiness_dry_run.py` | Repairs; R-list (empty for `test_calibration_bracketing.py`). **G6 first**: it blocks the next pack freeze (E19). |
| 3 | **D**, command line and controller | step-2 head | the 6 files `tests/test_cli_run.py` … `tests/test_partial_record_enclosure.py` | Repairs; every G10 test injects the runner |
| 4 | Lead, bench | A–D merged | none | All checks of §7.3. G11's 36 outcomes are re-read by their **new** first failure; each survivor is assigned to a seat or returned for ruling. |
| 5 | Lead, bench | step-4 head | `configs/paper_supply/supply_map.json` | The repin of §5, as the last commit |
| 6 | Lead | step-5 head merged with main's head at that moment | none | The full suite (§7.4 gate G-2) |

**Seat stop rules, in every brief.** (i) A repair that seems to need a production edit, or a new injection point, returns `NEEDS_RULING`; no environment-variable hook is ever added. (ii) No run ID is added to the historical set. (iii) A copied or edited historical bundle gets no exemption by its name. (iv) A seat never edits a file outside its list, including the helper.

**Sizing.** Four repair seats for 510 outcomes in 39 modules: fewer would be slow and would blur the per-test R-list judgment; more would collide on shared fixture builders. Seat C carries the ledger, receipt and sequence digests of G6 and G7 and is the one to raise in effort if its first report shows need.

### 7.3 Checks the lead runs (the seats do not run them on themselves)

1. **Assertion census against main.** A script walks the syntax tree of every granted test file on main and on the candidate. For each test function it records the number of `self.assert*` and `assert` calls and every literal expected argument. **Any decrease, or any changed literal, outside the approved R-list fails.** For the three §E-excluded files the permitted difference is zero. Every R-list entry asserts the specific exception type, the member label and the status. Where the old assertion covered logic that runs after the gate, that coverage moves to a sibling test that has evidence: split, never delete.
2. **Banned patterns, by `grep` over `git diff c7593edb HEAD -- tests`.** Patching or replacing any of `authenticate_window_members`, `_battery_verdict`, `_digest_bound_mock_config`, `BundleReader.metadata`, `battery_float.authenticate_*`, `HISTORICAL_BUNDLE_SET_SHA256`, `BFGS_HISTORICAL_*`; a new `_allow_unissued_fixture=True`; any new `skip`, `skipIf`, `skipUnless` or `expectedFailure`; `except` around an assertion; `assertRaises(Exception)` or `assertRaises(BaseException)`; a new patch of `custody_telemetry_identity` (the ten existing ones stay, none is added); `admit_mock_window` anywhere under `tests/` except in the files of seat P and in direct tests of the two admitted flows.
3. **Production diff.** `git diff --name-only c7593edb HEAD -- joulewise scripts configs` equals exactly: `joulewise/bundle_read.py`, `joulewise/aggregate.py`, `joulewise/controller.py`, `scripts/run_campaign.py`, `joulewise/calibration_bracketing.py`, `configs/paper_supply/supply_map.json`. One path more or fewer fails.
4. **Historical set.** `scripts/build_battery_float_historical_bundles.py --check` prints `entries=69`; `historical_bundles.json` and `HISTORICAL_BUNDLE_SET_SHA256` are byte-identical to `c7593edb`.
5. **Planted defects, one per group, each must turn a repaired test RED and is then reverted.** G1, G8: the passing pair swapped for the charging pair. G3: `metadata.json` deleted from one member. G4, G5: one config byte changed after binding. G6, G7: the evidence bytes swapped, then deleted. G10: the injected runner removed and the real probe replaced by one that exits 1. G2: T12a-1 and T12a-4. 10a: `mode` hard-coded. The lead commits the seat's landing **before** planting anything, and plants in a scratch worktree.
6. **Hermeticity (text 18).** With the real battery probe replaced, at the bench only, by a function that raises, the six seat-D modules and every module that reaches the controller's reduce stage stay GREEN. Today 11 tests read the battery of the laptop that runs them (Opus X14, confirmed by the G10 signature in E4).
7. **S1's own fences.** The frozen-function digests, the protected-path fence (`tests/test_bundle_read.py:586`) and the raw-capture tripwire are GREEN and their files are untouched.
8. **Skips by ID.** The set of skipped test IDs on the candidate's full suite equals the set on the reference run, apart from tests that exist only on one side, each of which is listed and explained.

### 7.4 The gate sequence

**Standing rule, ruled here: no refuter, cold gate or final pass is charged on a head unless a full-suite record exists for that exact head merged with main's head as of the charge.** The record holds: the candidate SHA, main's SHA, the merge SHA and its two parents, the command, the `TMPDIR` form, the summary line, the skipped IDs and the exit code. If main moves before the gate reports, the gate's verdict holds only if the lead shows the new main commits touch no file the candidate touches; otherwise the merge and the suite are redone. A later targeted pass never supersedes a red full suite.

| Gate | Precondition | What it judges |
|---|---|---|
| G-1 | Step 0 done | Nothing is judged; it is the reference. |
| G-2 | Steps 1 to 5 done | **Full suite** on head ⊕ main: 0 failures, 0 errors, check 8. |
| G-3 Delta refuter | G-2 green on the exact head | The diff `c7593edb..head`: 12a and 10a against their texts; every R-list entry; the repin (§5 review 1 to 4); checks 1 to 8 re-run independently on a sample the refuter chooses. The refuter is from a different model family than seats P and A–D. |
| G-3′ Fix round | refuter findings | New head → repin redone if an owning module changed → **full suite again** → the refuter reads the delta. At most two fix rounds; a third goes to a cold gate on whether the defect set is shrinking. |
| G-4 Cold final pass | full suite green on the exact final head ⊕ main | The whole of S1 as it will merge. **The MERGE verdict issued on `c7593edb` is void**: its premise that targeted suites compose was false for the merged tree. |
| G-5 Merge | G-4 says merge | By **merge commit** (the earlier condition M1 stands: `204424e6` must stay reachable). The pull-request description keeps the earlier M2 text and adds: text 12a, text 10a, the repin record with §5's standing note, and the lanes of §7.5. |
| G-6 After merge | — | One full suite on main, recorded. |

### 7.5 Opus's should-fix items, and Astra's, by scope

| Item | In this repair? | Ruling |
|---|---|---|
| Opus S1: campaign completion exits with no verdict row when a member directory lacks `metadata.json` | **Tests in; production out** | The refusal is safe for the science and stays. The five tests split: one asserts `CustodyUnreadable` at campaign level; the classification assertions move to direct tests of `classify_campaign_members` and `collection_verdict_for`. Whether the completion record should be written before the raise is lane **BFGS-COMPLETION-RECORD-01**. |
| Opus S2: a battery refusal inside `measured_window()` is reported as `environment_admission_missing` | **Test rule in; production out** | The two tests at `test_whole_window_selection.py:1179` and `:1257` get evidence and keep their assertion `()`. They are **never** rewritten to expect the mislabel. The label goes to the existing lane BFGS-ENVELOPE-REASON-01. |
| Opus S3: G10 tests run the real battery probe | **In, mandatory** | Seat D; check 6. |
| Opus S4: skip parity | **In, as check 8**, by ID, not by count | |
| Opus N1: some members gated twice at completion | Out | Harmless; the same bundle is authenticated twice. |
| Opus N2 / scout F3: a test hard-links into `TMPDIR` | **In, as a run condition** | Every full suite uses the `TMPDIR` form of the reference run. |
| Astra F1: replay custody | **In, as text 10a** | §4. |
| Astra F5: the repin helper deletes a pending role | **Prohibition in; repair out** | The helper is not run (§5). Its repair, with a test that both pending roles survive, is lane **PAPER-REPIN-HELPER-01**. |

## 8. Ruling 5 — split or abandon S1?

**Neither. HOLD and repair on S1's branch.**

- **Do not merge `c7593edb`.** 533 failing outcomes on main would turn every other stream's checks red and would block the next pack freeze, which runs a test module that now has 20 errors (E19). "Fix forward" was ruled for a handful of residual failures, not for this.
- **Do not split the production diff.** The reader's gate, the gated energy accessors and the consumers' gate calls are one mechanism. Any split leaves a main on which some consumers check the battery and others do not. That intermediate state is the one S1 exists to remove, and a split would reopen review that is closed.
- **Do not abandon.** Of the 533 outcomes, 23 are a tripwire working as designed (G9); at least 376 are fixtures that never carried the evidence real bundles carry; two are genuine contract questions, both now ruled (12a, 10a). Nothing found here shows the gate itself is wrong.
- **The one condition that reopens this question.** If, after steps 1 to 5, the full suite still shows failures whose repair needs a production file outside the five of check 3, the lead stops and brings the list to a cold gate. That gate, not the lead, decides whether the consumer gating separates from the controller and reader.

## 9. Corrections to the charge's facts

1. The integration tree `42e2af3e` is S1 merged with `daaff807`, not with main's head `e7c8bcc6` (E2). The 115/418 result is confirmed for that tree (E3). Pull request 436 is not in it.
2. "Main `e7c8bcc6` is green" is **not verified by me and not shown by any record I found** (E5). The two recorded green runs are of earlier main heads. Step 0 closes this.
3. The final pass did not "run only targeted suites" by oversight: it stated the full run on the merged tree as not executed and ordered it after the merge. The ruling was open about it; the order was wrong. §7.4's standing rule replaces that order.

## 10. Plain summary

1. Hold S1 and repair it on its own branch: keep the battery gate strict for everything a paper number can come from, let only two non-claim records (a mock campaign's completion record and a mock experiment's summary block) go through with every member visibly marked, and fix one real bug the scout missed, where replaying calibration data that has been moved to a backup location is wrongly refused.
2. The stale paper pins are test fixtures, not real receipts; the lead recomputes three of them as the last commit with a small recorded script (the existing helper must not be run, because it deletes a pending entry), and 39 existing test files, two new test-helper files and that one config file are opened for repair under a rule that tests get real evidence and keep their assertions.
3. From now on nothing is sent to a reviewer or judge until the whole test suite has passed on the exact candidate merged with the main branch as it stands that day; the earlier "merge" verdict is void, and the tree tested so far was already one merge behind main.
