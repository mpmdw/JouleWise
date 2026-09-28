ADDENDUM: S1-REGRESSION-01-A1 ISSUED

# Cold addendum S1-REGRESSION-01-A1 — rulings on the paired refuter's SF-1 to SF-4

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, one foreground session, no subagents, no background tasks. Session 2026-09-27, 17:40 to 17:51 PDT by the host clock. Python was `/opt/homebrew/bin/python3 -B`. Scratch is under `/tmp/cg-s1add-d528efb2/`. No file in any repository was modified; this file is the only file written. No process was left running (every command ran in the foreground and returned). `git status --short` on S1's worktree printed nothing before and after my one executed probe.

This addendum amends only the repair plan of S1-REGRESSION-01. The HOLD, the void MERGE verdict and every other ruling stand as written.

## 0. Contamination disclosure

**Loaded by the harness without my choosing, before my first turn:** the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md` of the worktree I was started in, the memory index `MEMORY.md` (one-line pointers; several name loop context such as checkpoints, directives on gates, and model assignments), a list of skills and agent types, the git status and five commit subjects. I used none of it for any ruling below. Every ruling rests on the code and records listed under Executed evidence. One exception is stated openly: the global file's writing standard (define each term at first use) matches what I would do anyway, and this text follows it.

**Not opened by me:** `RUN_STATE.md`, `TASK_QUEUE.md`, any `CLAUDE*.md`, `AGENTS.md`, any memory file, any skill file, the decision log, the three consult seats, the first cold-gate charge.

**Read by me:** the addendum charge; the ruling (`21-…`) and the refuter (`22-…`), both in full; one line each of two earlier rulings, found by search, to read text 12 in its own words; the regression inventory, by script; the refuter's 13-line scratch probe `mockpair.py`; and the code named below. I read the refuter before forming my view, so my view is not blind to it. Each refuter claim I rely on is marked as re-executed by me, confirmed by my reading, or taken from the refuter.

## 1. Terms used in this addendum

Terms defined in the ruling's §1 keep their meaning (S1, bundle, battery pair, verdict statuses, the window gate, mock bundle, mock window, mixed window, claim artifact, full suite, evidence-forward repair, R-list, repin). Added here:

- **Marker.** The value the controller writes into `metadata.json` for a run on the synthetic `mock` telemetry backend, in place of a battery pair: `{"pre": null, "post": null, "not_applicable": "mock"}`.
- **Bound config.** The `config.json` of a bundle whose SHA-256 equals `metadata.config_sha256`. "Names `mock`" means its `hardware_target.telemetry_backend` is `mock`.
- **Pair on a mock config.** A bundle whose bound config names `mock` and whose metadata nevertheless carries a battery pair. The controller cannot write this state (A2); only a hand or a test fixture can.
- **The paired-entry campaign.** The campaign flow in the function `run_axi_spec_campaign` (`scripts/run_campaign.py:7305`), which the refuter calls "the AXI campaign". It runs manifest entries in `spec_off`/`spec_on` pairs and may run an entry more than once. **Attempt ledger:** its file `attempt_ledger.jsonl`, one row per attempt, recording which attempt of each entry was selected.
- **Whole-window verdict record.** A campaign-log row with `record_type = "idle_admission_whole_window_verdict"`. It states whether a whole window passed idle admission, and it carries a field `claim_licensing`. The ruling's §1 lists "a whole-window verdict" as a claim artifact.
- **Completion record.** The campaign-log row with `record_type = "campaign_verdict"`, written when a campaign finishes.
- **Claim readiness.** The field `claim_readiness` of the completion record. Its `verdict` is `ready_for_analysis`, `not_ready_for_analysis` or `not_assessed`.
- **Child launcher.** The function through which a campaign starts one run as a separate process. In the paired-entry campaign it is `run_authenticated_campaign_child` (`:7660`).
- **Repair range.** The commits after `c7593edb` up to the candidate head, that is, `c7593edb..HEAD` on S1's branch.
- **Path fence.** A check that the set of file paths changed in a commit range is inside a fixed allowed set.

## 2. Executed evidence (this session, all in the foreground)

| # | Probe | Result |
|---|---|---|
| A0 | `shasum -a 256` of the ruling and the refuter; `git rev-parse HEAD` on S1's worktree and on the charge's example checkout | Both digests equal the charge's. S1 is `c7593edb…`, clean. **The example checkout `JouleWise-wt-d138-scout-d528efb2` is at `c772b019`, not at main.** `e7c8bcc6` is its ancestor and equals `origin/main`; outside `docs/` the two differ in `RUN_STATE.md`, `TASK_QUEUE.md` and `tests/test_gen_state.py`. I therefore read main only through `git show e7c8bcc6:…` and `git grep … e7c8bcc6`. |
| A1 | My script `/tmp/cg-s1add-d528efb2/mockpair.py`: builds S1's own fixture `WindowMembersTests.pair_bundle` (`tests/test_bfgs_window_consumers.py:30-59`) from S1's head, prints the facts, calls the window gate; then replaces the pair by the marker in the same bundle and calls the gate again | `bound config telemetry_backend = mock`; `config digest bound = True`; reader's mock decision `(True, '')`; **`gate verdict = pass`**. With the marker: `WindowBatteryRefusal … not_applicable`. **One and the same mock bundle passes with a pair and is refused with the marker. The refuter's R2 is re-executed and holds.** |
| A2 | Read `joulewise/bundle_read.py:461-517` and `joulewise/controller.py:2117-2123` at `c7593edb` | The reader takes the pair branch at `:477-481` (keys `pre` and `post` present, key `not_applicable` absent) and calls `authenticate_bundle` **before** it looks at the backend (`:491-495`). The controller writes the marker whenever the backend is `mock` (`:2119-2122`), so no production run produces a pair on a mock config. |
| A3 | `git grep "def authenticate_window_members\|admit_mock_window" e7c8bcc6 -- joulewise scripts` | No match. **Main has no window gate; the pattern of A1 exists only on S1.** |
| A4 | Read `scripts/run_campaign.py:7831-7865` and `:8018-8151` at `c7593edb`; `git diff e7c8bcc6 c7593edb -- scripts/run_campaign.py` | The gate at `:7848` takes every attempt the ledger records plus every attempt directory found on disk. It runs before the attempt ledger is written (`:7859-7865`). **Later in the same function, `:8071-8114` builds and appends a whole-window verdict record**, with `claim_licensing` set from the policy profile and the policy's `claim_bearing` flag (`:8076-8080`), not from the backend. The completion record follows (`:8128-8142`) and is written **without** `battery_float_members`; the gate's return value at `:7848` is discarded. |
| A5 | `grep idle_admission_whole_window_verdict` over `joulewise/` and `scripts/` | Two writers: `run_campaign.py:6435` (the dedicated whole-window command, behind the gate at `:6256`, which the ruling keeps strict) and `:8072` (the paired-entry campaign). `run_campaign()` itself, whose gate is `:9032`, writes none (`:9033-9095` read in full). Readers of the record include `analysis_manifest_v3.py`, `whole_window.py`, `window_duration_margins.py`, `scripts/check_window_provenance.py` and `scripts/render_results_fills.py`. |
| A6 | Text 12 in its own words, `…/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md:123` | "`members` = every finalized bundle of the window, `FAILED` included, **and every attempt the attempt ledger records, selected or superseded**". Consumers named for `scripts/run_campaign.py`: "its final analysis and whole-window verdict". |
| A7 | Read `tests/test_run_campaign.py:2427-2470` and `:2472-2620` | Both tests call `run_axi_spec_campaign` **in the test's own process**. The second asserts exactly one whole-window verdict record with `status == "passed"` (`:2603-2615`). The same module already replaces the child launcher in-process (`patch.object(run_campaign_module, "run_authenticated_campaign_child")`, `:2402-2404`). The fixture configs under `tests/fixtures/axi_ap_spec/` all name `mock`. |
| A8 | Read `scripts/run_campaign.py:226-228`, `:6586-6684`, `:6687-6823` at `c7593edb`; the same at main (`:222-224`, `:6515`, `:6527`, `:6616`); the hunk list of the S1 diff | `CLAIM_READINESS_NOTE` is "This verdict checks analysis inputs only; P2-037 decides claim outcomes." on both. The comment "Mock telemetry stays version-exempt: it cannot bear claims regardless" is on both. **No hunk of S1's diff falls inside either function**, so both are byte-identical to main. A mock member is exempt from the reducer-version and environment reasons (`:6614-6626`), so a complete mock campaign gets `ready_for_analysis`. |
| A9 | `grep -rl "claim_readiness\|ready_for_analysis" joulewise scripts` at `c7593edb`; `git grep -l` of the same at `e7c8bcc6` | One file on each: `scripts/run_campaign.py`. **No other production code reads claim readiness.** It is printed and logged; nothing gates on it. |
| A10 | Inventory rows for the four tests the refuter names; `tests/test_run_campaign.py:1677-1681`, `:3520-3545` | All four are G2 outcomes. The two readiness tests assert `ready_for_analysis` on a fixture whose backend defaults to `mock`; their refusal names `mock-r1-…` members. The fixture function takes a `telemetry_backend` keyword. |
| A11 | Read `tests/test_bundle_read.py:558-589` at `c7593edb`; `git ls-files 'tests/test_mint_floor_artifact*.py'` | The in-tree fence runs `git diff --exit-code 1417c0c4 204424e6 -- <protected>`. Both ends are fixed commits. **It cannot see any commit after `204424e6`. The refuter's R10 is confirmed.** The protected list holds `tests/test_calibration_bracketing.py` and the two minter test files, which are the ruling's three §E-excluded grants. |
| A12 | `git diff --name-only 204424e6 c7593edb -- <the same protected list>`; `git log --merges 204424e6..c7593edb`; `git diff --name-only e7c8bcc6...c7593edb -- <the same list>` | The two-commit form prints **three paths under `configs/calibration/`**. They came in with the merge `4aefdd12` ("Merge origin/main … into S1"). The three-dot form, which starts from the common ancestor with main, prints nothing. **So S1 itself did not touch a protected path, and a two-commit fence gives a false alarm across any merge of main.** |
| A13 | `git diff --name-only e7c8bcc6...c7593edb` | 27 paths: 16 under `joulewise/`, `scripts/`, `configs/` (equal to the ruling's E18) and 11 under `tests/`. |
| A14 | Inventory by script: G2 by module; `grep aggregate_experiment tests/test_experiment.py tests/test_aggregate.py` | G2 is 98 outcomes, 94 test IDs, in six modules; 12 outcomes are in `tests.test_experiment`. That module calls `aggregate_experiment` directly at `:553`, `:637`, `:651`, `:712`, `:738`. `tests/test_aggregate.py` has no G2 outcome. |
| A15 | Read `tests/test_bundle_read.py:67-71` | `load_config(**overrides)` replaces top-level config keys, so a test can build a bundle whose config names a non-mock backend by passing `hardware_target`. |

**NOT EXECUTED by me:** any full suite; any repair; the refuter's two in-memory stand-ins for rule 12a (its R7, R8 and the counts in N-1), which I take from the refuter; whether strict bundle validation (`run_campaign.py:7714`) accepts a non-mock bundle written by a test helper; what idle admission returns for mock members when it is not patched; whether `write_strict_analysis_campaign` writes the bundles itself (I read its signature and its call, not its body); the exact list in §E of Final texts v1.1 (I use the 27 paths of A13 instead).

## 3. SF-1 — a battery pair on a mock config: ADOPTED, MODIFIED

**Finding.** True and executed (A1, A2). The ruling's §3.4 asks for a non-mock config plus a pair, but forbids nothing. A seat that keeps the mock config and adds a pair gets `pass` from the gate, and the repaired test goes green for a reason no production run can reproduce.

**Two modifications to the refuter's fix.**

1. The refuter's ban is a sentence ("a battery pair written into a bundle whose bound `config.json` names `mock`"). A `grep` cannot decide what a config names at run time. The ban below has a static part that `grep` can check and a run-time count that catches every other route.
2. Seat P's own new tests need a "real member" (T12a-1, T12a-2). S1's existing fixture `pair_bundle` is itself a pair on a mock config (A1). Seat P must not use it for those members.

**Amended text.**

*§3.4, first bullet, add at its end:*

> The config is rebound first and the pair is written second. A fixture that keeps a config naming `mock` and adds a pair is not evidence-forward: the gate would pass on a state the controller cannot write (`controller.py:2119-2122`). It is banned by check 2 (k) and counted by check 2 (l).

*§7.3 check 2, add:*

> **(k) Pairs are written by helper H only.** In the added lines of `git diff c7593edb HEAD -- tests`, outside `tests/bfgs_fixtures.py`, `tests/test_bfgs_fixtures.py` and seat P's three test files: no call of `battery_float.observe(`, no string `raw/battery_float.`, and no dictionary literal that gives `battery_float` a `pre` or a `post`.
>
> **(l) Mock-pair count, at the bench.** The lead places, in a scratch directory on `PYTHONPATH`, a `sitecustomize.py` that wraps `battery_float.authenticate_bundle`. (`sitecustomize` loads at interpreter start, so test subprocesses are covered too.) For each call the wrapper reads the bundle's `config.json`; if it names `mock`, the wrapper appends one line to a log: the innermost stack frame that lies under `tests/` (file and function). It changes no return value. The lead runs every granted test module and seat P's three files this way on `c7593edb` and on the candidate. **The set of (file, function) pairs on the candidate must be a subset of the set on `c7593edb`.** One new pair fails. The wrapper is never committed.

*§7.2 step 1′ (helper H), add to Output:*

> The two pair writers first check the bundle: they hash `config.json`, compare with `metadata.config_sha256`, and parse the backend. If the digest differs they raise `ValueError("config not bound")`. If the backend is `mock` they raise `ValueError("battery pair on mock config")`. In both cases they write nothing.

*§7.2 step 1 (seat P), add to Output:*

> In T12a-1, T12a-2 and T12a-6 the non-mock member is built from a config whose `hardware_target.telemetry_backend` is not `mock` (`load_config(hardware_target=…)`, `tests/test_bundle_read.py:67-71`). The fixture `pair_bundle` with its default config is not used for a "real member".

**Defect-shaped tests added.**

| Id | Input | Must observe | Planted defect that must turn it RED |
|---|---|---|---|
| H-5, in `tests/test_bfgs_fixtures.py` | A bundle whose bound config names `mock`, handed to the passing-pair writer | `ValueError`; no file under `raw/`; `metadata.json` byte-identical to before the call | the backend check removed from the writer |
| H-6, same file | The same bundle after helper H's rebind to a non-mock backend, then the passing-pair writer, then the window gate | `pass` | the rebind leaving `metadata.config_sha256` unchanged (the writer must then raise "config not bound") |
| Check 2 (l) self-test, lead, scratch worktree | One repaired test with its rebind step deleted and the pair written directly | the count lists that test as new | none; this is the counterfactual of the check itself |

**Lane, not in this repair: BFGS-MOCK-PAIR-01.** The reader decides the backend before the pair branch, and refuses a pair on a mock config as `battery_float_evidence_missing` with the reason "pair on mock config". Its defect-shaped test is A1's bundle, which must not return `pass`. It is out of this repair because S1's own passing fixtures are pairs on mock configs (A1), so the change rewrites S1's test fixtures and reopens reviewed tests. It is listed in the pull-request description with the lanes of §7.5.

## 4. SF-2 — the gate at `run_campaign.py:7848`: ADOPTED, MODIFIED (the refuter's second branch)

**Ruling: `:7848` stays strict. It is not added to 12a (c).**

**Why it is claim-bearing.** The refuter's premise is that `:7848` is "the same thing as `:9032`". It is not (A4, A5):

- After the gate at `:9032`, `run_campaign()` writes a completion record and nothing else.
- After the gate at `:7848`, `run_axi_spec_campaign` writes the attempt ledger, the completion record **and a whole-window verdict record** (`:8071-8114`). That record is a claim artifact under the ruling's §1. Its `claim_licensing` field follows the policy, not the backend, so under a production policy a mock window would be written as licensed.
- Text 12 names, for this script, "its final analysis and whole-window verdict", and defines the members as "every attempt the attempt ledger records, selected or superseded" (A6). The gate at `:7848` is that sentence in code.
- The test the refuter wants to keep green unchanged asserts a whole-window verdict record with `status == "passed"` built from mock bundles (A7). Admitting it would be the exact outcome rule 12a exists to prevent.

**The refuter's feasibility argument does not hold for these two tests.** It says evidence-forward repair "needs non-mock bundles produced by the campaign's fake runner, which runs as a subprocess". Both tests call the campaign function in the test's own process, and the child launcher is a module attribute that this test module already replaces (A7). No production hook is needed to supply the bundles.

**Amended text.**

*12a (c), add after the sentence "Every other call site passes nothing and stays strict: …":*

> The gate in `run_axi_spec_campaign` (`scripts/run_campaign.py:7848`) is strict because that one function also writes a whole-window verdict record (`:8071-8114`), which is a claim artifact. Separating that function's completion record from its whole-window verdict record, so that the first could be admitted, is a production redesign and is decided only by cold gate.

*§3.4, add a third bullet:*

> - **The two paired-entry campaign tests** (`test_non_marker_axi_multi_entry_campaign_records_gate_before_entry_two`, `test_axi_runner_emits_campaign_wide_idle_admission_verdict`) are of the first form. Seat A copies the fixture manifest and its configs into the test's temporary directory with a non-mock backend, and replaces the child launcher in-process by a function in the test that writes, for each attempt, the bundle the child would have written, using helper H (rebind, then pair). Assertions stay byte-identical. If strict validation or any later predicate refuses such a bundle, the seat returns `NEEDS_RULING` with the test ID and the name of the refusing predicate. The tests are not rewritten to expect a refusal, and the keyword is not added.

**Defect-shaped test added, seat P, in `tests/test_bfgs_window_consumers.py`.**

| Id | Input | Must observe | Planted defect that must turn it RED |
|---|---|---|---|
| T12a-11 | An all-mock paired-entry campaign, run through `run_axi_spec_campaign` in-process, with the fixture of `tests/fixtures/axi_ap_spec` unchanged | `WindowBatteryRefusal` naming every attempt, status `not_applicable`; no `attempt_ledger.jsonl`; no whole-window verdict record and no completion record in the campaign log | `admit_mock_window=True` added at `:7848` (T12a-9 must report the same edit) |

**Observation, to a lane: BFGS-AXI-VISIBILITY-01.** The paired-entry campaign's completion record carries no `battery_float_members` (A4). Nothing is hidden today: the gate is strict, its members are written by the campaign itself, so the only status that can reach the record is `pass`. Showing it is a small edit for a later stream.

## 5. SF-3 — claim readiness of an admitted mock window: ADOPTED (the refuter's option (a))

**Finding.** Confirmed by reading (A8, A10). The condition in 12a (d) is met: a complete mock campaign gets `ready_for_analysis`. So (d) as written orders a production edit and rewrites at least two tests.

**Why main's meaning is kept.**

1. **Nothing reads the field.** Claim readiness is printed and logged; no production code outside `run_campaign.py` reads it (A9). Changing it protects no number.
2. **What protects the numbers is elsewhere and is already ruled.** The analysis loader passes no keyword, so it refuses every window with a mock member. That holds whatever the field says.
3. **The field's stated meaning is about inputs.** "This verdict checks analysis inputs only" (A8). For a mock campaign it answers "were the planned runs collected, with their cooldown evidence?", which is the subject of the two tests.
4. **The edit would cost coverage.** The readiness logic is tested on mock campaigns because they need no hardware. S1 did not touch either function (A8); (d) would make this repair the first change to them.

**What this costs, stated plainly.** A mock campaign's completion record will say `ready_for_analysis` while the analysis loader refuses that campaign. The record is not silent about it: the same row shows every member as `not_applicable`. The pull-request description explains the pair of facts in one sentence (below).

**Amended text.**

*12a (d), replaced in full:*

> **(d) What an admitted mock window may produce.** The campaign completion record and the experiment manifest's aggregate block, each carrying `battery_float_members` with every member shown as `not_applicable` (this is text 12's last sentence, now satisfiable). **No claim artifact.** The field `claim_readiness` of the completion record keeps the meaning and the value it has on main: it reports whether the campaign's planned inputs are complete, and it is not a permission to claim. `claim_readiness_for` and `_member_readiness_reasons` stay byte-identical to `c7593edb`. A mock campaign is kept from every paper number by the analysis loader, which passes no keyword and refuses the window.

*T12a-8, replaced in full:*

| Id | Input | Must observe | Planted defect that must turn it RED |
|---|---|---|---|
| T12a-8 | A mock experiment, and a mock campaign with complete planned inputs, end to end (the campaign in a subprocess) | (i) `battery_float_members` shows every member `not_applicable`, in the completion record and in the aggregate block. (ii) `claim_readiness.verdict` is `ready_for_analysis`, the value main gives the same fixture. (iii) `load_analysis_inputs`, called on that same campaign directory with no keyword, raises `WindowBatteryRefusal` naming every member, and no analysis artifact file exists afterwards. The mock barrier function is not patched. | for (i): the visibility field dropped from either record; for (iii): `admit_mock_window=True` added at `inputs.py:3195` |

*G-5, add to the pull-request description:*

> For a campaign run on the synthetic backend, `ready_for_analysis` means only that the planned runs were collected. The analysis loader refuses such a campaign, and its completion record shows every member as `not_applicable`.

Seat P's "report on 12a (d)" (§7.2 step 1, Output) is no longer owed.

## 6. SF-4 — a fence over the paths of the repair: ADOPTED, MODIFIED

**Finding.** Confirmed (A11). The in-tree fence compares two fixed commits and stays green whatever the repair does. Check 3 fences the production paths of the repair. Nothing fences its test paths.

**Three modifications to the refuter's fix.**

1. **"Exactly the three" becomes "at most the three".** A seat need not change all three granted files.
2. **The allowed set is the seats' own scopes, not "S1's §E list ∪ the grant".** S1's list holds test files that no repair seat may write (for example `tests/test_bundle_read.py`, `tests/test_controller.py`, `tests/test_reduce.py`, A13). The refuter's union would let the repair edit them unseen.
3. **The candidate branch takes no merge of main during the repair.** A12 shows why: a two-commit diff across a merge reports main's own changes as if they were the branch's.

**Amended text.**

*§7.3 check 7, replaced in full:*

> 7. **S1's own fences.** (a) The frozen-function digests, the in-tree protected-path test (`tests/test_bundle_read.py:558-589`) and the raw-capture tripwire are GREEN and their files are untouched. The in-tree test compares the fixed commits `1417c0c4` and `204424e6`, so it says nothing about later commits; (b), (c) and check 9 cover those. (b) `git diff --name-only c7593edb HEAD --` followed by the protected list of that test, expanded as the test expands it, prints at most these three paths: `tests/test_mint_floor_artifact.py`, `tests/test_mint_floor_artifact_generalized.py`, `tests/test_calibration_bracketing.py`. (c) `git log --merges c7593edb..HEAD` prints nothing. Main is merged only in the separate integration tree of step 6, never into the candidate branch.

*§7.3, add check 9:*

> 9. **Path fence over the whole repair.** `git diff --name-only c7593edb HEAD`, with no path filter, prints only paths from this set of 50: the six paths of check 3; the 41 test paths of the §6 grant (`tests/bfgs_fixtures.py`, `tests/test_bfgs_fixtures.py` and the 39 granted modules); and seat P's three test files (`tests/test_bfgs_window_consumers.py`, `tests/test_bfgs_calibration_bracketing.py`, `tests/test_bfgs_consumer_sweep.py`). One path outside the set fails. For the whole of S1, `git diff --name-only <main's head>...HEAD` (three dots: from the common ancestor) prints only the 27 paths it prints at `c7593edb` plus paths from the set of 50.

**Counterfactual for check 9, run by the lead once, in a scratch worktree cut from the candidate head.** Commit a one-byte change to `tests/receipt_corpus.py` (a refused path) and another to `tests/test_bundle_read.py` (an S1 path outside the repair). The fence must fail and name both paths. The in-tree test must stay GREEN on that same commit, which shows why it could not stand in for the fence. The scratch worktree is then removed.

The delta refuter (G-3) and the cold final pass (G-4) re-run checks 7 and 9 themselves.

## 7. The three NITs

| NIT | Changes the plan? | Ruling |
|---|---|---|
| **N-1** (the count "12a clears 56" is optimistic; five tests call the aggregate directly) | **Yes, one clause** | The count is informational and is not relied on. Check 2's phrase "direct tests of the two admitted flows" is made exact (below). The two paired-entry tests are ruled in §4. `test_dirty_unknown_and_changed_provenance_are_hard_excluded_at_admission` sits on the strict loader path and is repaired under §3.4 as the ruling says. |
| **N-2** (the floor extractor and the minter reach floor extraction's mock barrier) | No | Taken as a correction to the ruling's E10 for the record. Both consumers stay strict, and T12a-4 still drives both. |
| **N-3** (the two "mock" decisions agree on production inputs) | No | Accepted. Defect 2 of §3.2 stands on the count of barriers. |

*§7.3 check 2, last item, replaced:*

> `admit_mock_window` anywhere under `tests/` except: (i) seat P's three test files; (ii) in `tests/test_experiment.py`, a direct call of `aggregate_experiment` on the manifest of an experiment that the same test or its fixture ran, which is the data `controller.py:3004` aggregates. Seat A lists every such call by test ID and line in a **call-form list**, kept apart from the R-list; the assertions of those tests stay byte-identical. In every other file, `tests/test_aggregate.py` included, the keyword is absent and fixtures are repaired evidence-forward.

## 8. What changes in the plan

Order, seats, bases and every WRITE_SCOPE are **unchanged**. No path is added to or removed from the §6 grant. Only these change:

| Where | Change |
|---|---|
| Step 1, seat P, Output | T12a-8 as replaced (§5); T12a-11 added (§4); the non-mock member rule (§3); the report on 12a (d) dropped. The report on §4's open point of the ruling (text 10a) is still owed. |
| Step 1′, seat H, Output | The two refusals of the pair writers; H-5 and H-6 (§3). |
| Step 2, lead | Adds checks 2 (k), 7 (b), 7 (c) and 9 on the merged head of P and H. |
| Step 3, seat A | The two paired-entry tests by the method of §4; the call-form list (§7). |
| Step 4, lead | All checks, now including 2 (k), 2 (l) and 9; the two self-tests (check 2 (l) and check 9) are run once here. |
| §7.3 | Check 2 gains (k) and (l) and an exact last item; check 7 is replaced; check 9 is new. |
| G-5 | The pull-request description gains the sentence of §5 and the lanes BFGS-MOCK-PAIR-01 and BFGS-AXI-VISIBILITY-01. |
| Seat stop rules | Add (v): a seat never writes a pair into a bundle whose bound config names `mock`, and never calls a pair writer before the rebind. |

## 9. What I find wrong in the refuter's analysis

1. **SF-2's premise.** `:7848` is not "the same thing as `:9032`". The function behind `:7848` writes a whole-window verdict record; the function behind `:9032` does not (A4, A5). The refuter read `:7831-7900` and stopped before `:8071`.
2. **SF-2's feasibility claim.** The two tests run the campaign in-process and the child launcher is replaceable there (A7). The "subprocess needs a production hook" argument belongs to tests that start the campaign script as a separate process, not to these two.
3. **SF-1's reason for "not a claim risk".** The refuter says the mock barrier still fires. By its own R5 that barrier exists in the analysis loader and floor extraction only; the window-duration margins and the aggregate have none. The sound reason is a different one: the controller cannot write a pair for a mock run (A2). The lane is still right.
4. **SF-4's allowed set is too wide** and its "exactly three" too narrow (§6).
5. **SF-3's cost list, third item.** The refuter says moving the readiness tests to non-mock fixtures "meets SF-2's subprocess problem". The fixture takes a backend keyword and is called with the runs directory before the campaign starts (A10), which suggests the test writes the bundles itself. I did not execute it, and the point is moot because (d) is replaced.

Everything else I checked in the refuter holds: R2 (re-executed, A1), R10 (A11), the readiness facts of SF-3 (A8), the grant's coverage, and its concurrence.

## 10. Corrections to the charge's facts

1. The example "clean checkout" of main is at `c772b019`, a bookkeeping commit on top of main, not at `e7c8bcc6` (A0). Its code under `joulewise/` and `scripts/` equals main's; its `tests/test_gen_state.py` does not.
2. SF-3 is summarised as "12a (d) is already met". More exactly: the **condition** that triggers (d)'s production edit is met. (d) itself was not satisfied by the code; it is replaced here.

## 11. Plain summary

1. Three of the refuter's four fixes are adopted with tightening: test fixtures may not fake a passing battery check on a synthetic run (the helper refuses, and a bench count catches any other route); a synthetic campaign's record keeps saying its inputs are complete, because nothing reads that field and the analysis step refuses synthetic runs anyway; and a new check lists every file the repair may touch, 50 in all.
2. The fourth is decided against the refuter's preference: the paired-entry campaign's battery gate stays strict, because that one function also writes a whole-window verdict, which is something a paper number can come from; its two tests are repaired by giving them real-shaped evidence in-process.
3. No seat, scope, order or granted path changes; the plan gains three tests, two bench checks with their own self-tests, one sentence for the pull-request description and two small follow-up lanes.
