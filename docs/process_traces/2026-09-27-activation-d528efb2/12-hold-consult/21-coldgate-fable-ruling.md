RULING: HOLD-BY-CONSTRUCTION-01 ISSUED

# Cold ruling HOLD-BY-CONSTRUCTION-01 — the 25G83 claim hold is keyed to the operating-system build and enforced where authority is created and where it is spent

Judge: Claude Fable 5.1, cold session, one foreground session, 2026-09-28. Candidate read: `feat/2026-09-27-d138-25g83-issuance` at `8458f797`, in the read-only worktree `/Users/edr/code/JouleWise-wt-d138-hold2-d528efb2`. I modified no repository file except this one.

**Read this first: nothing in this ruling was executed by me.** Every shell command I issued was returned unrun by the session's permission service (an error of that service, not a refusal). I therefore could not run a probe, a test, `git`, or `date`, and I could not create the scratch directory. Every fact in §2 is marked **read**: I opened the file and read the lines cited. Facts marked **executed by others** are outputs saved by the refuters, the seats or the earlier judge, which I read and did not reproduce. I do not know the wall-clock start and end of this session. §9 states what this costs and how the gates make up for it.

## 0. Contamination disclosure

1. **Injected by the session harness before the charge, not opened by me:** the owner's global instruction file (a writing standard and a list of skill names); the project instruction file of my worktree (notes on the model bridge); a one-line-per-entry index of the owner's memory store; the five most recent commit subjects. The index carries lines on the owner's directives about gates, about what bears on the truth of a number, and about threat models. The commit subjects say the hold refuter found one route and that the matter was escalated to a consult; the charge says the same.
2. **Not opened:** any memory file, any skill file, `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, any `CLAUDE*.md`.
3. **What I took from the injected material:** the writing standard, as form. Nothing as evidence.
4. **Same model family.** I am Fable 5.1, as were the judges of the two rulings I amend. I sat on neither.
5. **Read in full:** the consult charge; both seats; the Opus hold refuter's report; the design ruling and its addendum A1. **Read in part:** the contract refuter's second report (its two findings), the mutation report (its table), the replay report (item vi), the cap council addendum (§5, the sequence), the science addendum (§5.3, the text of H1). I did not open the refuter's probe scripts.
6. **Values seen:** the held file's three operative numbers, as they appear in code and reports. I used them for nothing.

## 1. Words used

Terms from the two rulings I amend keep their meaning. So that this file reads alone:

| Term | Meaning |
|---|---|
| **Calibration file** | A JSON file stating how large the instrument's timing uncertainty may be before a measurement is refused. |
| **Build** | The operating-system build string the machine reports (`sysctl kern.osversion`). The old build is 25F84, the new one 25G83. A calibration file records the build it was derived on, in its field `identity_epoch.os_build`. |
| **R7** | The calibration file of build 25F84. It is the default: the file code reads when it names none. |
| **The new file** | `configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json`, derived at build 25G83. |
| **H1** | The science ruling's condition, in its own words: "No claim-bearing window is armed at 25G83 until a written ruling closes the cap-and-cadence question… Windows that carry no claim may run, and are the way to gather the evidence." |
| **Window, claim-bearing, pack** | A window is one scheduled measurement session. Claim-bearing means its results may be reported as findings. A pack is the frozen set of plans a claim-bearing window runs from. |
| **Bracket** | The pair of calibration captures taken just before and just after a measurement. Bracket evaluation decides whether the measurement's timing uncertainty is acceptable. No reported result exists without a bracket whose status is `passed`. |
| **Authenticator** | The function `_acceptance_bound_from_authenticated_bytes`. It takes the bytes of a calibration file and returns the parsed content only if the bytes' digest equals a digest written in code and the content passes the validator. It is where bytes become something code trusts. |
| **Loader** | `load_calibration_acceptance_bound`. It reads a path and calls the authenticator. |
| **Continuation** | A registered file stating that an existing calibration file also judges a second build. None is registered today. |
| **Go receipt** | The record that authorises one window to start. It carries an authorisation record with a field `claim_eligible`, true or false. |
| **Derivation night** | A window with no pack and no claim, whose captures exist to derive a calibration. |
| **Route** | Defined in §6.1, because the stop rule depends on it. |
| **Census test** | A test that lists every place in production code that touches a protected thing, and fails when the list changes without review. |
| **RED-then-GREEN** | A test shown to fail on the code before the fix and to pass after it. |

## 2. Facts I verified, all by reading at `8458f797`

| # | Fact | Where |
|---|---|---|
| F1 | The hold sits in the loader, **after** the authenticator has already returned the content. The authenticator itself knows nothing of the hold. | `joulewise/calibration_bracketing.py:1214-1221`, `:1224-1266` |
| F2 | The arm evidence author calls the authenticator directly, not the loader. | `joulewise/arm_readiness_evidence.py:335-341`, `:923` |
| F3 | The admission list stops at the first declared identifier it finds, in the order `issued`, `issued_acceptance.acceptance_id`, `issued_artifact_id`. The evidence author reads `issued_acceptance`, else `issued_artifact_id`, and never `issued`. The two can therefore be shown different files. | `arm_readiness.py:6205-6220`; `arm_readiness_evidence.py:897-911` |
| F4 | The numbers table returns a generation's numbers from its identifier alone, with no hold check. | `calibration_bracketing.py:590-638` |
| F5 | The code row that registers the new file does not record its build. The build exists only inside the file. | `calibration_bracketing.py:401-425` |
| F6 | The hold table is keyed by file identifier and has one entry. | `calibration_bracketing.py:218-223` |
| F7 | Bracket evaluation writes the status `passed` at exactly one place. A search of `joulewise/` and `scripts/` for an assignment of that status to a bracket result finds no other in the calibration module. | `calibration_bracketing.py:2720` |
| F8 | Bracket evaluation, the allowance projection and continuation authentication each re-read the pinned file through the loader at the moment of use. They do not trust the content a caller hands them. | `calibration_bracketing.py:1282`, `:1320-1340`, `:2096-2101`; `calibration_epoch_continuation.py:194` |
| F9 | In bracket evaluation, a measurement whose identity matches no build the file judges returns "stale" at one statement. Everything after that statement runs only for an identity the file judges. | `calibration_bracketing.py:2203-2216`, `:2271-2274` |
| F10 | A continuation adds its build to the builds a file judges, and nothing there consults the hold. | `calibration_epoch_continuation.py:207-211`, `:348-364` |
| F11 | Capture preflight refuses when the machine's identity is not among the builds the loaded file judges. | `scripts/validate_powermetrics_fiducial.py:412-436` |
| F12 | The derivation-night route needs the default to **not** judge the machine's build, and its input writer accepts exactly one refusal reason from preflight, `acceptance_artifact_epoch_mismatch`. | `validate_powermetrics_fiducial.py:2081-2131`; `scripts/write_derivation_night_inputs.py:146-187` |
| F13 | The derivation-night route also checks that the default's recorded estimator digests equal the running code's, because it calls the same preflight function. | `validate_powermetrics_fiducial.py:397-402`, `:547-550` |
| F14 | A manual campaign whose config carries no launch marker returns from its preflight at once; nothing about calibration or build is checked there. | `scripts/run_campaign.py:1866-1881`, `:8090-8094` |
| F15 | Nothing in `arm_readiness.py`, `arm_readiness_evidence.py` or `night_gate.py` reads the machine's build. The only occurrence is a synthetic fixture. | search; `arm_readiness.py:8137` |
| F16 | The go receipt's authorisation is validated in `_authenticate_pack_launch_go`, which has `claim_eligible` in hand and already distinguishes a live check from a replay with `require_current_boot`. | `arm_readiness.py:10020`, `:10093`, `:10112-10134` |
| F17 | The capture writer accepts a machine identity from a file given with `--identity-epoch-json-for-test`. Unlike the test-only cell budget, that option is not tied to the test sampler. | `validate_powermetrics_fiducial.py:2029-2066` |
| F18 | The four files whose digests a calibration file records are `joulewise/powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, `reduce.py`. None of the files this ruling changes is among them. | `calibration_bracketing.py:230-235` |
| F19 | The promotion tool checks a citation only if both of its fields are present, and its hold check asks only whether an entry with id `H1` exists. | `scripts/promote_calibration_candidate.py:75-87`, `:106-108` |
| F20 | The keyword and the file-keyed table appear in four test files, 15 times. No production file outside the definition uses the keyword. | search of `tests/`, `joulewise/`, `scripts/` |

**Executed by others, read by me, not reproduced:** the mixed pack is admitted and its held bytes certified (Opus probe rows C, D); the authenticator returns the held content and the numbers table returns `0.013701` (Opus B1–B3; Astra V2 reproduced both); four R7-freeze mutants stay GREEN (mutation report, last four rows); replay item (vi) fails because evaluation re-reads the held file without the keyword (replay report V6).

## 3. Item 1 — the design

### 3.1 The forcing problem

H1 is a statement about **a build**: nothing claim-bearing at 25G83. Both earlier designs enforced a statement about **a file**: first "this identifier may not be named by a pack", then "this identifier is hidden by the loader". A file-keyed rule must be repeated at every place a file can be presented, and it says nothing about a file that does not exist yet. That is why each round ended with a new route, and why the cap council's own plan (an interim re-issue at 25G83, under a new identifier) would have walked past the hold unless someone remembered a table entry (S-4).

**Worked example.** Suppose the interim re-issue is registered tomorrow as `…n12_25g83_r2`. At `8458f797` the loader asks "is `…r2` in the hold table?" The table holds only `…r1` (F6). The answer is no, and `…r2` loads as ordinary authority at build 25G83. Under this ruling the question becomes "what build does `…r2` judge?" The answer, 25G83, is held, whatever the file is called.

### 3.2 The rule

**One table, keyed by build, in one new module that imports nothing from the project.**

`joulewise/claim_hold.py`:

```python
CLAIM_HELD_OS_BUILDS: dict[str, str] = {
    "25G83": "H1-25G83-CAP-CADENCE (SCI-25G83-CANDIDATE-01-A1 §5.3)",
}
UNKNOWN_BUILD_HOLD = "UNKNOWN-OS-BUILD (a build that cannot be read is treated as held)"

def claim_hold_for_os_build(os_build: object) -> str | None:
    """The name of the hold on this build, or None if claims are allowed."""
    if not isinstance(os_build, str) or not os_build:
        return UNKNOWN_BUILD_HOLD
    return CLAIM_HELD_OS_BUILDS.get(os_build)

def machine_os_build() -> str | None:
    """`/usr/sbin/sysctl -n kern.osversion`, stripped; None on any failure."""
```

No other production file may name `CLAIM_HELD_OS_BUILDS`; they call the two functions. `CLAIM_HELD_ACCEPTANCE_IDS` and the keyword `allow_claim_held` are **deleted**. The set of held files is no longer written anywhere: it is whatever files judge a held build.

**Where it is enforced.** Authority over a claim is created at one place and spent at three. The hold stands at all four.

```
   calibration bytes on disk
            |
            v
   [G1] AUTHENTICATOR  -- file's build held? --> returns nothing
            |                                     (loader, evidence author,
            |  content, trusted                    bootstrap: all callers)
            v
   builds this file judges = its own  +  CONTINUATIONS
                                          [G2] continued build held? --> continuation refused
            |
            +--------------------+---------------------------+
            v                    v                           v
   [S1] BRACKET EVALUATION   [S2] GO RECEIPT             [S3] MANUAL CAMPAIGN
   measurement's build       claim_eligible is true      policy is claim-bearing
   held?  --> not passed     and machine's build held?   and machine's build held?
                             --> no authorisation        --> does not start
```

Named elements. **G1** and **G2** are gates on the *file side*: they decide what a calibration file may be trusted for. **S1, S2, S3** are gates on the *measurement side*: they ask what build the measurement or the machine is at, and do not care which file, default, pack or continuation is involved. A route must get past a file-side gate **and** a measurement-side gate; each side is complete without the other, and each is tested with the other switched off.

| Gate | File, function | Exact behaviour |
|---|---|---|
| **G1** | `calibration_bracketing.py`. Rename the present body of `_acceptance_bound_from_authenticated_bytes` to `_authenticate_acceptance_bytes` (digest pin and validator, no hold). The old name stays and becomes: call `_authenticate_acceptance_bytes`; if the result is not `None` and `claim_hold_for_os_build(result["identity_epoch"]["os_build"])` is not `None`, return `None`. | The loader loses its keyword and its own hold check; it reads the path and calls the old name. Every existing caller (F2 and the bootstrap) is covered without an edit. |
| **G1, by identifier** | New table `REGISTERED_GENERATION_OS_BUILD: dict[str, str]` beside `ISSUED_ACCEPTANCE_REGISTRY`, one entry per registered identifier, each value copied from that file's `identity_epoch.os_build`. `_authenticate_acceptance_bytes` refuses an issued file whose identifier has no entry or whose build differs from its entry. New function `claim_hold_for_acceptance_id(acceptance_id)` = `claim_hold_for_os_build(REGISTERED_GENERATION_OS_BUILD.get(acceptance_id))`. | `acceptance_generation_operatives` returns `None` when that function returns a hold (closes S-3). A private `_registered_operatives_unchecked` serves the validator and the inspection function only. The table is separate from the registered row (F5) because the issued file carries a copy of that row, and changing the row would change a protected field. |
| **Default guard** | Replaces the present guard at `:222-223`. | Refuse to import if `claim_hold_for_acceptance_id(ACTIVE_ACCEPTANCE_ID)` is a hold, **or** if `ISSUED_ACCEPTANCE_REGISTRY[ACTIVE_ACCEPTANCE_ID]["path"] != DEFAULT_ACCEPTANCE_BOUND_PATH` (closes nit N-2). |
| **G2** | `calibration_epoch_continuation.py`, `authenticate_epoch_continuation`, directly after the check at `:211`. | `_require(claim_hold_for_os_build(epoch.get("os_build")) is None, "continued_identity_epoch_claim_held")`. |
| **S1** | `calibration_bracketing.py`, `evaluate_calibration_bracket`, as the first statement after the stale return at `:2271-2274`. | If `claim_hold_for_os_build(observed_identity.get("os_build"))` is a hold: set `artifact.claim_eligible` to `False`; set freshness to `{"status": "stale", "reason": "observed_epoch_claim_held", "hold": <name>}`; return the reason code `calibration_acceptance_bound_stale`. Placed here, it changes the outcome only of an evaluation that would otherwise have continued (F9), so no existing refusal changes its wording. The branch at `:2102-2120` keeps the reason `acceptance_artifact_claim_held`, now looked up with `claim_hold_for_acceptance_id`. |
| **Admission list** | `arm_readiness.py`, `_issued_d079`. | Collect every identifier the policy declares under the three keys of F3. Admit only if exactly one distinct identifier is declared, it is in `_ISSUED_D079_IDS`, and `claim_hold_for_acceptance_id` of it is `None`. This is the Opus refuter's cure; its sketch kept all nine committed packs admitted (executed by Opus, `probe_fix.py`). |
| **S2** | `arm_readiness.py`, `_authenticate_pack_launch_go`, directly after the check at `:10133-10134`. | If `authorization["claim_eligible"]` is true and `require_current_boot` is true and `claim_hold_for_os_build(machine_os_build())` is a hold: `raise _go_invalid("claim_hold: " + name)`. A replay (`require_current_boot` false) does not read the machine. |
| **S3** | `scripts/run_campaign.py`, in `main`, directly before the call at `:8091-8094`. | If not a dry run, and the policy's idle-admission extension exists and is `claim_bearing`, and `claim_hold_for_os_build(machine_os_build())` is a hold: print the hold's name to standard error and return 2, before any child process starts. |
| **Identity seam** | `scripts/validate_powermetrics_fiducial.py`, beside the argument checks at `:1894-1901`. | `--identity-epoch-json-for-test` without `--sampler-direct-for-test` is an argument error. Reason: S1 and capture preflight trust the recorded build. F17 is the one place a live capture could record a build the machine is not at. Conditional; see §4.4. |

**What is deliberately not edited.** Capture preflight (F11) and the derivation-night input writer (F12) get no hold logic. At a held build the ordinary capture already refuses: the default cannot be a held file (default guard), a held file named by path returns nothing (G1), and no continuation into a held build authenticates (G2), so no loadable file judges the build. Sol proposed a gate in preflight and Astra warned that a new refusal reason there would break the input writer; leaving both files alone satisfies both.

### 3.3 What a non-claim caller is, and how it is authorised

There is no flag, keyword, environment variable or command-line option that lifts the hold. There are three non-claim things, each authorised by something that already exists and is reviewed or registered:

| Non-claim thing | Authorised by | Meets which gate | Outcome at build 25G83 |
|---|---|---|---|
| **Derivation-night capture** (the cap plan's evidence windows) | A derivation-kind session declared in the ledger before it runs (F12) | None. It reads the default, R7, whose build is not held, and records it as provenance. Its rows are excluded from bracket endpoints by existing code (cited by the Opus refuter, `calibration_bracketing.py:1914-1925`; not read by me). | Runs, as W1 and W2 did. |
| **Window with a pack and no claim** (a rehearsal) | An authorisation record with `claim_eligible: false` | S2, which acts only on `claim_eligible: true` | Authorised. A pack that names a held-build file is still refused at the admission list; that known cost of the first ruling is unchanged. |
| **Governance inspection** (tests, the corpus verifier, later the re-issue tool) | New function `inspect_acceptance_without_claim_authority(path)` in `calibration_bracketing.py`, returning a frozen record `AcceptanceInspection(artifact, claim_hold, file_sha256)`. Callers in `joulewise/` and `scripts/` are an allowlist in the census test, **empty at this change**. | It returns data, never authority: by F8 every function that can produce a claim re-reads the file through G1 at the moment of use, so holding the content opens nothing. | Returns the content and the hold's name. |

### 3.4 Seat disagreements, resolved

| Question | Sol | Astra | Opus sketch | Ruling | Why |
|---|---|---|---|---|---|
| A separate authority object, carried to every consumer | no; policy in the authenticator plus an inspection function | yes; new module, new type, about eight consumer files migrated | not raised | **Sol's shape.** | F8: authority is decided at the moment of use from pinned bytes, never from what the caller holds. A second type would add plumbing to many files and close nothing G1 leaves open. The one place that trusted an identifier alone (F4) is closed by the build table. |
| The keyword `allow_claim_held` | remove | remove | keep, pass it down | **Remove.** | A boolean at the authenticator is the general escape both seats warn of. |
| A gate on the machine's build at arm | yes | yes | not raised | **Yes, S2, at the go receipt.** | F15, F16. H1's own verb is "armed". The go receipt is where claim eligibility is known. |
| Manual campaign | refuse before claim work | refuse before child launch | not raised | **Yes, S3.** | F14. |
| Hold logic in capture preflight | yes | decouple the derivation check first | no | **No edit.** | §3.2, last paragraph. |
| Bind authority to digest, window and policy version; re-check stored authority | not raised | yes | not raised | **Not adopted.** | No stored authority object exists in this design, so there is nothing to re-check. |
| The test identity option (F17) | silent | essential | outside the transaction | **In this round, conditionally** (§4.4). | A hold keyed to the recorded build is only as good as the record. |
| Census method | syntax-tree allowlist | adds import resolution and runtime read tracing | tighten the keyword census | **Text-level name census plus planted routes** (§4.3). | A text search catches aliases, `getattr` strings and `**` expansion, which a syntax-tree search for one call shape does not. Runtime tracing is left out of this round. |

## 4. Item 2 — the changes, the tests, the write scope

### 4.1 Tests for the known routes

All in `tests/test_claim_hold_routes.py`, replacing HR-1 to HR-8 where they overlap. No mock of the loader or the authenticator. Where a test says a gate is "switched off in memory", it means the real unheld function is put in the gate's place (for G1: the name `_acceptance_bound_from_authenticated_bytes` is pointed at the real `_authenticate_acceptance_bytes`), never a stand-in that returns a prepared value.

**The machine's build in tests.** Every test that reaches S2 or S3 sets the build by patching `machine_os_build` and states the value it sets. No test may depend on the build of the machine it happens to run on: the bench is at 25G83 and a hosted runner is not, so such a test would pass in one place and fail in the other.

**Rule for RED.** A RED run is an *assertion failure*. A failure to import, or a missing attribute, is not RED. Route tests must therefore import only names that exist at `325d9f77` and reach newer functions through a helper with fallbacks, as the present `_held_artifact` does. Where the old code has no seam to simulate the input (E-7, E-8), RED is shown by **mutation on the fix head**: the gate's statement is deleted and the test fails. The record says which kind each RED is. Each test has a **control**: the same input with the hold table emptied in memory must open the route, which proves the test passes because of the hold.

| Id | Known route | Input | GREEN, required | RED |
|---|---|---|---|---|
| E-1 | Round 1, pack naming R7 judged by the default | pack tree `issued` = R7; capture preflight, no file named, identity at 25G83 | admitted; preflight refuses `acceptance_artifact_epoch_mismatch`, `stale_fields == ['os_build']` | `325d9f77`: returns `0.038078579302948` (executed by the addendum judge) |
| E-2 | Round 1, same route at the bracket | evaluation at a 25G83 identity with two fresh endpoints, the held content passed explicitly, **G1 switched off in memory** | not `passed`; reason `observed_epoch_claim_held` | mutation: delete S1's statement; result is `passed` |
| E-3 | Round 1, manual campaign | the two configs of the present HR-3; then preflight by default and by held path, the allowance projection, explicit evaluation | refuses at each | `325d9f77` (executed by the addendum judge) |
| E-4 | Round 2 B-1, nested | `issued` = R7 and `issued_acceptance` = the new file with path and digest | `_issued_d079` false; successor row REQUIRED; ACCEPTANCE_OWNER raises underivable | `8458f797`: admitted, certified PASS (executed by Opus) |
| E-5 | Round 2 B-1, flat | `issued` = R7 and `issued_artifact_id` = the new file | as E-4 | `8458f797` |
| E-5c | Controls for E-4, E-5 | each of the nine committed packs; a policy naming R7 under one key | admitted | — |
| E-6 | S-1 | the held file's bytes given to `_acceptance_bound_from_authenticated_bytes` | `None` | `8458f797`: returns the content |
| E-6b | S-2 | loader called with `allow_claim_held=True` | `TypeError`: the keyword does not exist | `8458f797`: returns the content |
| E-6c | S-3 | `acceptance_generation_operatives` and `acceptance_bracket_screen_s` with the new identifier | `None` | `8458f797`: returns `0.013701` |
| E-6d | S-4, a later file at 25G83 | in memory: a copy of the new file under identifier `…n12_25g83_r2`, seals recomputed, registered with its digest and build | loader and authenticator return `None`; identifier is refused at the admission list | `8458f797`, same fixture: loads |
| E-6e | S-4, continuation of R7 into 25G83 | a valid synthetic continuation in an in-memory registry, built with the builder in `tests/test_epoch_continuation.py` | continuation refused `continued_identity_epoch_claim_held`; preflight at 25G83 still refuses; evaluation not `passed` | `8458f797`: R7 judges 25G83, evaluation `passed` |
| E-7 | New gate S2 | go authorisation with `claim_eligible` true, machine build patched to `25G83`; to `25F84`; unreadable; and `claim_eligible` false at `25G83` | refuse; pass as before; refuse; pass | mutation: delete S2 |
| E-8 | New gate S3 | claim-bearing policy, machine build patched to `25G83`, child launcher patched to raise if called | returns 2, launcher never called; at `25F84` proceeds as before | mutation: delete S3 |
| E-9 | Identity seam | `--identity-epoch-json-for-test` without the test sampler | argument error | `8458f797`: accepted |
| E-10 | Non-claim routes stay open | the input writer's `_stale_identity_fields` at 25G83 with the default; the derivation-only basis at 25G83; `inspect_acceptance_without_claim_authority` on the new file | `['os_build']`; returns R7's basis; returns the content with the hold's name | — (the first is the present HR-8) |
| E-11 | Default guard | subprocess importing the module with the default constants set to the new file; and with the default path and identifier disagreeing | both exit non-zero | first: present HR-7 |

Existing tests that load the new file with the keyword (F20) move to the inspection function. Tests that emptied the file-keyed table now empty `CLAIM_HELD_OS_BUILDS`. **No assertion from main is weakened or deleted.**

### 4.2 Mutation evidence to record

Delete, one at a time: the hold in G1; G2's line; S1's statement; the single-identifier rule in `_issued_d079`; the hold in `acceptance_generation_operatives`; S2; S3; one entry of `REGISTERED_GENERATION_OS_BUILD`. Each must turn a named test RED by assertion.

### 4.3 The census — the test for a route nobody has thought of

New file `tests/test_claim_hold_census.py`. It searches the **text** of every `.py` file under `joulewise/` and `scripts/`.

| Id | What it lists | Allowed at this change |
|---|---|---|
| C-1 | files containing `_authenticate_acceptance_bytes` | `joulewise/calibration_bracketing.py` only |
| C-2 | files containing `inspect_acceptance_without_claim_authority` or `_registered_operatives_unchecked` | `joulewise/calibration_bracketing.py` only |
| C-3 | files containing `CLAIM_HELD_OS_BUILDS` | `joulewise/claim_hold.py` only |
| C-4 | files containing `allow_claim_held` or `CLAIM_HELD_ACCEPTANCE_IDS` | none |
| C-5 | files that can reach a calibration file: any containing `configs/calibration`, `_CALIBRATION_CONFIG_DIR`, `calibration_acceptance_`, or a name ending `_ACCEPTANCE_BOUND_PATH` | a literal mapping in the test, file → one-line purpose, equal to the set found at the fix head. (My search for `configs/calibration`, `_CALIBRATION_CONFIG_DIR` and `calibration_acceptance_d079` found 11 files at `8458f797`. It did not cover names ending `_ACCEPTANCE_BOUND_PATH`, so the full list is longer; the seat builds it.) |
| C-6 | in `calibration_bracketing.py`, by syntax tree: assignments of the string `passed` to a result's `status` | exactly one, inside `evaluate_calibration_bracket`; and earlier in that function, an `if` statement at the top level of the function body (not nested inside another `if`, loop or `try`) whose test calls `claim_hold_for_os_build` and whose body returns |
| C-7 | for every identifier in `ISSUED_ACCEPTANCE_REGISTRY`: a build entry exists and equals the file's own build; if that build is held, the loader, the authenticator, the numbers table and the admission list each refuse it. For every entry of `EPOCH_CONTINUATION_REGISTRY`: its continued build is not held. | — |

**Proof that the census can see.** Four planted routes, each applied in a scratch copy and shown to turn the census RED, then removed: (a) a new file under `scripts/` that reads the new file's path with `json.loads`; (b) a call to `_authenticate_acceptance_bytes` from `arm_readiness_evidence.py`; (c) a second assignment of `passed`; (d) an `import … as` alias of the inspection function in `joulewise/whole_window.py`.

**What the census cannot see,** stated plainly: a path or a name assembled at run time from pieces. It bounds ordinary drift and honest mistakes. It is not a proof against code written to evade it.

### 4.4 The condition on two files

`scripts/run_campaign.py` (S3) and `scripts/validate_powermetrics_fiducial.py` (identity seam) are entry points of live windows. I could not run a search for their digests, so I do not know whether any registration, pack or launch chain that a live window checks pins them. **Before the seat starts, the lead searches the repository and the installed launch material for the sha256 of each file at main.**
- Not pinned by anything a live window checks: both edits are in the seat's scope.
- Pinned: that edit leaves the seat's scope and becomes a lane with its re-pin. It must merge **before the next window of any kind at 25G83**, the same deadline the rulings already set for the network-time conditions H5 and H6. The issuing record then says, in these words, which gate is not yet in code.

### 4.5 WRITE_SCOPE for fix round 3 — exhaustive

```
joulewise/claim_hold.py                                                (new)
joulewise/calibration_bracketing.py
joulewise/calibration_epoch_continuation.py
joulewise/arm_readiness.py
scripts/promote_calibration_candidate.py                               (§5.1 only)
scripts/run_campaign.py                                                (S3 only; subject to §4.4)
scripts/validate_powermetrics_fiducial.py                              (identity seam only; subject to §4.4)
configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json   (tool output only)
tests/test_claim_hold_routes.py
tests/test_claim_hold_census.py                                        (new)
tests/test_calibration_bracketing.py
tests/test_calibration_dispositions.py
tests/test_arm_readiness_evidence_author.py
tests/test_epoch_continuation.py
tests/test_promote_calibration_candidate.py
tests/test_acc_25g83_rev5.py
tests/test_epoch_equivalence_check.py
tests/verify_calibration_acceptance_corpus.py
```

Rules for the seat. Nothing outside this list: not the four files of F18, not `arm_readiness_evidence.py` (G1 covers it without an edit; if the seat believes an edit is needed, that is a finding), not the input writer, not any pack, not any older calibration file, not the issuance text or its builder, not any document. If the suite shows a failure whose cure lies outside the list, the seat stops and reports the path. The lead may amend the scope in writing with **test files only**, and only to patch the machine-build reader in a test that exercises S2 or S3.

**Lead-owned, before the seat starts:**
1. This ruling on main with the records.
2. The §4.4 search.
3. **A census by execution, which I could not do.** Build a scratch prototype of S2 and S3 (two statements and the new module) and run the whole suite on the bench, which is at build 25G83. Every test that then fails is a test from main that exercises a claim-eligible go receipt or a claim-bearing campaign on the real machine build. List those files and add them to the scope for the patch described above.
4. The issuance text: `issuance_record.hold_enforcement` becomes exactly: `H1 is enforced outside these bytes, in code, by a hold on the operating-system build this file judges. While the hold is in force, no function returns this file's content as authority for a claim, no bracket at that build can pass, and no claim-bearing window can be authorised to start on a machine at that build. Lifting the hold changes no byte of this file.` `issuance_record.transaction` cites this ruling after addendum A1. The sentence names no count of places and no function, so a later change of mechanism does not change the bytes again.

Because the bytes change, the file is regenerated by the tool, the input seal must still come out `e7363bdd…b011`, and digest X, the whole-file seal, the registry pin and the issuing record follow.

## 5. Item 3 — the other open questions

### 5.1 The promotion tool: fix now

**Ruling: fix in this round.** The tool is re-run in this round in any case (§4.5 item 4), and a tool that accepts an issuance text with its citations deleted is the tool that writes the bytes. Both seats agree.

In `_validate_text`, before `_verify_cited_files` runs:
- `source_candidate`, every entry of `rulings`, every entry of `network_time_provenance.source_rulings`, and `preserved_log` must each be an object carrying **both** of its path and digest fields, as non-empty strings. `source_rulings` must be a non-empty list.
- `holds` must carry entries with ids `H1`, `H5`, `H6`, `H7`, each with a non-empty `text`.

**Test P8:** the contract refuter's probes P5a, P5b, P5f and P5g, plus one hold with empty text, each refused. RED at `8458f797`, where the refuter executed the first four and all were accepted. The committed bytes are not put in doubt by this: the refuter confirmed the tool reproduces them.

### 5.2 The four GREEN R7-freeze mutants: a test gap, closed now

**Ruling: equivalent today, not equivalent in intent; close the gap in this round.** While the default is R7, "the default" and "R7" are the same value, so a tool that wrongly reads the default cannot be told from one that rightly names R7. The freeze exists for the day the default moves. A test that cannot fail until that day protects nothing on that day. Both seats agree.

In `tests/test_acc_25g83_rev5.py` and `tests/test_epoch_equivalence_check.py`: each freeze test patches the tool's imported `ACTIVE_ACCEPTANCE_ID` and `DEFAULT_ACCEPTANCE_BOUND_PATH` to a registered generation that is not R7 and not held (R6), then asserts the tool still resolves R7. The four mutants of the mutation report's last four rows are re-run and each must be RED.

### 5.3 The independent replay's item (vi), restated

Item (vi) of addendum A1 §8.1 step 4 asked for something the design forbids: production evaluation of a held file. It is replaced by three observations on the real ledger, read-only:

- **(vi-a)** Unmodified code, no file named: a 25G83 identity evaluates stale with `stale_fields == ['os_build']`, judged by R7; a 25F84 identity evaluates fresh.
- **(vi-b)** Unmodified code, the new file's content passed explicitly, 25G83 identity: refused, reason `acceptance_artifact_claim_held`, no artifact returned.
- **(vi-c)** In the replay seat's own scratch process, with `CLAIM_HELD_OS_BUILDS` emptied **in memory**: the same call reports freshness `fresh` with no stale field. This shows the file is sound and that the hold alone stands in the way. It is a replay observation. No production function offers it.

## 6. Item 4 — the stop rule

### 6.1 What counts as a route

A **route** is a sequence of calls into unmodified production code, on a machine whose build is held, with the machine's identity truthfully recorded, that ends in any of:
1. a bracket with status `passed` for a measurement at a held build;
2. a go receipt accepted with `claim_eligible: true`;
3. a claim-bearing campaign that starts a child process;
4. the content or the numbers of a held-build file returned by any function other than the inspection function;
5. arm evidence that certifies a held-build file.

**Not a route:** anything that needs a repository file edited, a digest forged, or a test-only option on a fake sampler; and any of the three non-claim things of §3.3. If §4.4 moved a gate to a lane, the matching end is excluded until that lane merges, and the record says so.

### 6.2 The rule

Fix round 3 is the last round that changes production logic for the hold.

| Outcome at the gates of §7 | What happens |
|---|---|
| No route; no blocker | Proceed to merge. |
| No route; findings that need only tests, comments or record wording | **One** closing pass, limited to those. Then the re-audit of the difference. It is not a round. |
| **Any route**, found by any seat at any gate | **The transaction stops for good.** No round 4. The branch is not merged. |
| A finding whose cure needs production logic changed again | The same: stop. That would be round 4 under another name. |
| Any of E-1, E-3 to E-6e or E-9 cannot be shown RED by assertion on its named commit; or any planted route fails to turn the census RED | Stop: the tests do not see what they are named for. |
| A cure needs one of the four files of F18, or an assertion from main weakened | Stop. |

**What goes back to the owner.** One brief, with the route as found and these options, each with its cost worked out: (a) withdraw the issued file from this transaction and land only the loader repair, the promotion tool and their tests, with the cap council ruling on its own step 1, which waits on this issuance; (b) accept a named, written residual; (c) a new design consult. The magistrate does not choose among them.

**Why stop and not try again.** Three rounds that each end in a new route would show that the hold cannot be confined by the present structure of the code. More patches would then raise confidence without raising safety.

## 7. Item 5 — the gate sequence to merge

1. **Lead:** the four steps of §4.5 ("Lead-owned").
2. **Fix seat:** §3.2, §4, §5.1, §5.2, in the scope of §4.5; regenerate the issued file; update the pin.
3. **RED record:** each test of §4.1 on its named commit and on the fix head, saved with commit ids; the mutations of §4.2; the four planted routes of §4.3.
4. **Pre-issue re-hash and independent replay** on the new bytes, by a seat that did not write them, with item (vi) as restated in §5.3.
5. **Old-epoch replay:** byte-identical outputs at main and at the fix head, as addendum A1 §6 item 1 requires. The default has not moved.
6. **Whole suite** on the head merged with current main, on the bench. Green, no new skip.
7. **Two refuters, fresh seats, from different model families, neither having sat on this transaction.** *Hold charge:* find a route as §6.1 defines it. By execution: every caller of the loader and of the authenticator; every reader listed by C-5; whether a valid ordinary capture at 25G83 can be written to the ledger; whether a derivation-night row can become a bracket endpoint; whether any launch avoids `_authenticate_pack_launch_go`; whether a campaign can reach a child process without passing S3. *Contract charge:* the new digest and pins; §5.1's checks; that no test from main was weakened; that the census allowlists equal what is in the tree.
8. **Pedagogy pass** on the revised issuing record and decision-log entry, as its own review. New terms to build at first use: "build", "held build", "go receipt", "inspection".
9. **Re-audit of the difference** after the fix round and after the closing pass, if one ran.
10. **Cold final pass:** a fresh judge, given the final difference, the issuing record, the design ruling, addendum A1 and this ruling, confirms each numbered item is met.
11. **Merge** as one commit.
12. **Post-merge, on main, recorded:** the four estimator digests and the cap; the loader with no argument returns R7; the loader and the authenticator return nothing for the new file; the inspection function returns it with the hold's name; the numbers table returns nothing for the new identifier; `_issued_d079` refuses it and refuses both mixed shapes; capture preflight at a 25G83 identity refuses on `os_build`; the census passes.

**Record text.** In the decision-log entry and the issuing record, the "three places" paragraph of addendum A1 §7.1 is replaced by a description of §3.2's diagram in the record's own words, and a new paragraph "What the third refuter found" is added beside the existing one. **Neither document may say that a claim is impossible at 25G83.** What may be said: no route, as §6.1 defines it, was found by the gates of step 7.

**Release of the hold.** Unchanged in kind: a reviewed change that deletes the entry `"25G83"` from `CLAIM_HELD_OS_BUILDS` and cites the cap council's closing ruling.

## 8. One matter for the cap council, flagged and not ruled

Read, and inferred, not run. The cap plan merges the cap change with an interim re-issue at build 25G83, then runs two non-claim windows. By F13 a derivation night needs a default whose recorded estimator digests equal the running code. After the cap change R7's will not. By F12 it also needs a default that does not judge 25G83, and by the default guard a held-build file cannot be the default. So the interim re-issue cannot serve as the default for those windows, and R7 as it stands cannot either. The cap transaction appears to need a re-issue of R7 at build 25F84 under the new estimator bytes, to be the default. This was equally true under addendum A1 and is not caused by this ruling. The cap council owns it. Step 9 of its sequence ("the interim file's identifier is entered in the code's hold list") becomes "the interim file's build is entered in `REGISTERED_GENERATION_OS_BUILD`", after which it is held without a further entry.

## 9. Limits of this ruling

- **I executed nothing.** §2 is reading. I built no prototype. The earlier judge built one for addendum A1 and ran the routes against it; this ruling has no such check. The gates that stand in for it are the lead's census by execution (§4.5 step 3), the RED record, and the refuters. If the lead's prototype shows that S2 or S3 cannot be added without changing what a test from main asserts, that is a stop under §6.2, last row.
- **S2's placement rests on a partial reading.** I read `_authenticate_pack_launch_go` from `:10060` to `:10190` and the head of `generate_arm_receipt`. I did not trace that every window launch passes that function. The hold refuter's charge carries it.
- **S3's placement rests on F14 and on a search for `claim_bearing`.** I did not read `main` of `run_campaign.py` in full, nor confirm that the idle-admission extension is the only carrier of the claim-bearing flag.
- **The build table's values** for the seven older files are not known to me. I assumed nothing about them; the seat copies each from its file and C-7 checks the copy.
- **Whether `_registered_operatives_unchecked` is needed** depends on whether the validator reads the numbers table through the public function. My search found the validator using the registered rows directly (`:834`), which suggests it does not. If so the private function serves the inspection function only.
- **E-6d's fixture** may be refused by the validator for a reason other than the hold, because the copied file carries a registered row. The control (hold emptied, fixture loads) exists to show which.
- **The identity seam** is a judgment that a hold keyed to a recorded build needs the record protected. The Opus refuter read that the seam alone gives no result because bundle bindings must also match. I did not verify either reading.
- **The census** bounds drift, not evasion (§4.3).
- I did not read the cap council ruling that its addendum amends, nor the refuters' probe scripts, nor the issuing record or decision-log text.

## Summary

1. The hold moves from "this file" to "this operating-system build": one table in one new module, checked where calibration bytes become trusted, where a continuation extends a file to another build, where a bracket can pass, where a claim-eligible window is authorised to start, and where a manual claim campaign starts. The keyword that let a caller ask for a held file is deleted; non-claim work goes through the derivation night, a go receipt marked not claim-eligible, or a read-only inspection function.
2. Every known route gets a test shown failing on the old code, a census fails when any new code touches calibration files or the protected functions without review, and the promotion tool, the four R7 tests and replay item (vi) are fixed or restated in the same round.
3. I could run nothing in this session, so the lead's prototype run and the refuters carry the verification; and this is the last round: if a fresh refuter finds a route, the transaction stops for good and goes to the owner with costed options.
