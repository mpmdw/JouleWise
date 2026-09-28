ADDENDUM: D138-25G83-DESIGN-01-A1 ISSUED

# Cold addendum D138-25G83-DESIGN-01-A1 — the hold is open; how it is closed before the transaction may merge

Judge: Claude Fable 5.1, cold session, one foreground session, 2026-09-27 23:44 to 2026-09-28 00:12 PDT (bench clock, from `date`; 23:44 is my first command that ran).
Candidate judged: branch `feat/2026-09-27-d138-25g83-issuance` at `325d9f77b3ffb73fd0dd0f876f3ce59d567a092b`, read in the worktree `/Users/edr/code/JouleWise-wt-d138-final-d528efb2` (clean before and after; I re-read its head at the end). Main at `9eab16f8` is its merge base.
Every line marked **executed** below was run by me in this session. My probes are in `/tmp/cg-d138a1-d528efb2/` (sha256, first 16 characters: `probe_count.py` `8a7bc7e1e1aba4e5`, `probe_trigger.py` `73daa617f8e2fa23`, `probe_routes.py` `a0e6ee891be062da`, `probe_derivation.py` `2795c2242d495f44`, `apply_proto.py` `d9f5fee1cd181199`). I modified no repository file except this one.

**Result in one paragraph.** Both refuters are right: the hold is open, and the ruled stop applies. The cause is one design choice in the ruling I amend: it moved the default calibration file to the new file and put the hold only at the list that admits packs. I reverse that choice. **The new file is issued and registered, but it does not become the default until the hold lifts.** A second guard is added at the one function through which every calibration file is read: a held file is returned only to a caller that states in code that it makes no claim. I built this design in a scratch copy and ran both refuters' routes against it: each route returns the held file's numbers at the candidate head and refuses in the prototype. I also confirm by execution that the eleven set-aside rows count toward the file's "corpus doubled" trigger, which is wrong, and that this defect was the only thing that stopped a passing claim-eligible result at the candidate head.

## 0. Contamination disclosure

1. **Injected by the session harness before the charge, not opened by me:** the owner's global instruction file (a writing standard and a list of skill names), the project instruction file of this worktree (notes on the model bridge), a one-line-per-entry index of the owner's memory store, and the five most recent commit subjects. The index includes lines saying the owner approved the file name, that a D-138 implementation seat was running, and the owner's directives on gates and on what bears on the truth of a number. One commit subject says the contract refuter dissented and that two independent hold routes were found; the charge says the same. I opened no memory file, no skill file, no `RUN_STATE.md`, no `TASK_QUEUE.md`, no `AGENTS.md`, no `CLAUDE*.md`.
2. **What I took from the injected material:** the writing standard, as form. Nothing as evidence.
3. **Same model family.** I am Fable 5.1, as was the judge of the ruling I amend and of the cap council addendum. I sat on neither.
4. **Other rulings and scratch I read.** The ruling I amend, in full. Both refuter reports, the pedagogy pass and the second old-epoch replay report, in full. The cap council addendum CAP-COUNCIL-25G83-01-A1, in full; I did not read the cap council ruling it amends, nor the four seats. The refuters' scratch files `/tmp/d138-holdref-d528efb2/probe_hold.py` and `probe_entrypoints.py`, and the contract refuter's `probe_default.py` and `probe_default.out`. My trigger probe is adapted from the hold refuter's `probe_hold.py`.
5. **Values I have seen.** The three operative numbers of the new file, and member values as they pass through my synthetic bracket. I used them only as inputs to refusal tests.
6. **Protocol deviation, stated.** One of my test commands exceeded the harness's ten-minute limit and the harness moved it to the background. I stopped it by process id (70707 and its child 21362) and used only the output it had already written. A later test run was stopped by my own time limit and left one child (64114), a test process driving a fake sampler from a fixture; I stopped it by process id. No capture, no powermetrics, no battery read, no subagent. I did not touch processes belonging to other sessions.

## 1. Words used

Terms defined in §1 of the ruling I amend keep their meaning. Repeated here so this file reads alone:

| Term | Meaning |
|---|---|
| **Calibration file** | A JSON file that states how large the instrument's timing uncertainty may be before a measurement is refused. It holds the captures it was derived from and three numbers derived from them. |
| **Capture** | One recording of the power sampler under commanded load pulses. It yields one timing-uncertainty number, **B**, in seconds. |
| **Epoch** | The machine state a calibration file is valid for. The field that differs here is the operating-system build: old epoch 25F84, new epoch 25G83. |
| **R7** | The calibration file of the old epoch, `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`. It is the default on main today. |
| **The new file** | `configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json`, derived from 12 captures (its **members**) of the new epoch. sha256 at the candidate head: `80c23036…351b` (re-hashed by me). |
| **Loader** | The function `load_calibration_acceptance_bound` in `joulewise/calibration_bracketing.py`. Every route by which code reads a calibration file ends in it. |
| **Default** | The calibration file the loader reads when the caller names none (`DEFAULT_ACCEPTANCE_BOUND_PATH`). |
| **Bracket** | The pair of captures taken just before and just after a measurement. **Bracket evaluation** (`evaluate_calibration_bracket`) decides whether the measurement's timing uncertainty is acceptable and, if so, attaches a number to it. No reported result exists without a passed bracket. |
| **Capture preflight** | The check a capture makes before it records (`_derive_preflight_systematic_screen_s` in `scripts/validate_powermetrics_fiducial.py`). It reads a calibration file and refuses if the machine's epoch is not one that file judges. |
| **Window, claim-bearing, pack, arming** | A window is one scheduled measurement session. Claim-bearing means its results may be reported as findings. A pack is the frozen set of plans a claim-bearing window runs from. Arming authorises a window to start. |
| **Admission list** | The list in `joulewise/arm_readiness.py` of calibration identifiers a pack may name (`_issued_d079`). |
| **H1, "the hold"** | The science ruling's condition: no claim-bearing window at epoch 25G83 until the cap question is ruled. **The cap** is the limit on the search work one capture may use; **the cap question** is whether that limit removes captures selectively by machine state. |
| **Held file** | An issued calibration file listed in the code's hold table. Today: the new file only. |
| **Disposed row** | One of eleven captures of 2026-09-19 that a written decision set aside as diagnostic, never members, because they ran under a different launch setting. |
| **Doubling trigger** | A rule inside bracket evaluation: when the number of valid captures at the file's epoch reaches twice the number of members, the file is declared stale and must be re-derived. For the new file: 12 members, threshold 24, trigger name `corpus_doubles_from_12_to_24`. |
| **Derivation night** | A window that runs with no pack and makes no claim; its captures exist to derive a calibration. The two windows that produced the 12 members were of this kind. |
| **RED-then-GREEN test** | A test shown to fail on the code before the fix (RED) and to pass after it (GREEN). It proves the test can see the defect. |

## 2. What I verified by execution

All at the unmodified export of `325d9f77` ("head") and at a scratch copy with the design of §3 applied ("prototype", built by `apply_proto.py`).

| # | Fact | Head `325d9f77` | Prototype |
|---|---|---|---|
| E1 | Prior set of the new file: 86 rows; valid rows at epoch 25G83 | 23 = 12 members + 11 disposed; `excluded_members` is empty | same bytes |
| E2 | Capture preflight, no file named, machine at 25G83 (contract refuter's route) | returns level screen `0.038078579302948` from the held file | refuses `acceptance_artifact_epoch_mismatch ['os_build']` |
| E3 | Capture preflight, held file named by path | returns `0.038078579302948` | refuses `acceptance_artifact_unauthenticated` |
| E4 | Manual campaign preflight with a checked-in config that carries no launch marker (hold refuter's route) | returns `None`, admission list never consulted | same: returns `None`, never consulted |
| E5 | Allowance projection used by the floor mint, from the held file | returns allowance `0.013701` | returns `None` |
| E6 | Bracket evaluation, no file named, measurement at 25G83 | judged by the held file: `fresh`, `claim_eligible: true` | judged by R7: `stale`, `stale_fields ['os_build']`, refused |
| E7 | Bracket evaluation, held file passed explicitly | evaluated | refused, no artifact returned |
| E8 | Admission list: pack naming R7 / pack naming the new file | admitted / refused | admitted / refused (tests H-T1, H-T2, H-T3 pass, 3 of 3) |
| E9 | Doubling trigger with 0, 1, 2 new valid captures after the file's cutoff | 0: not observed. **1: observed.** 2: file stale, bracket refused | see E10 |
| E10 | Doubling trigger after the fix of §4, hold table emptied in memory | — | 1, 2, 4, 11 new captures: not observed. 12: observed, file stale |
| E11 | **Bracket result after the fix of §4, hold table emptied in memory, two new endpoints** | — | **`passed`, `claim_eligible: true`, operative bound `0.0384310413330314` s, allowance `0.013701` s** |
| E12 | Derivation-night input writer at a 25G83 machine, default file | refuses: "this is an ORDINARY night" | returns `['os_build']`: the derivation night is allowed |

Two readings matter.

**E9 with E11.** At the head, the only thing that stood between the held file and a passed, claim-eligible bracket was the doubling trigger firing on the first new capture. That trigger fires for a wrong reason (§4). So the head was protected by a defect. Fix the defect alone and the route opens completely. **The trigger fix and the hold repair must land in the same commit.**

**E4.** The manual campaign is not stopped at its own preflight in either tree. That is also the state of main today. What changes is whether anything it collects can become a result; §3.3 rules on this.

Not completed: main's version of `tests/test_validate_powermetrics_fiducial_derivation_only.py` on the prototype. The machine was busy and my 120-second limit ended the run after 7 tests, all passing. E12 is the direct evidence; the fix seat runs the file in full.

## 3. Item 1 — where H1 is enforced

### 3.1 The forcing problem

Before the candidate, no result could exist at 25G83 for one reason: the default file, R7, judges only 25F84, so every capture preflight and every bracket evaluation at 25G83 refused. That barrier covered every route, because every consumer reads the default (no production caller of bracket evaluation names a file; contract refuter, confirmed by my `grep`).

The candidate moves the default to the new file. That removes the barrier for every route at once. It replaces it with a check at one place, the admission list, which sees only the identifier a pack *declares*. Two kinds of route never present the held identifier there:

```
                        what the admission list sees        what judges the measurement
 pack naming new file   "…n12_25g83_r1"  -> REFUSED          (never runs)
 pack naming R7         "…n17_r7"        -> admitted         the DEFAULT  = held file at head
 manual campaign        (list not consulted)                 the DEFAULT  = held file at head
```

Named elements: the left column is the route; the middle column is the input to `_issued_d079`; the right column is the file that capture preflight and bracket evaluation load. The hold must act on the right column.

### 3.2 The three options, weighed

| Option | Closes the R7-pack route | Closes the manual route | Evidence captures for the cap question | Cost |
|---|---|---|---|---|
| (a) Check the hold wherever a file is consumed, default moved | yes | yes | **Harmed.** With the default at a 25G83 file the derivation night refuses at 25G83 (E12). Every non-claim capture must take the ordinary path and is screened by the held file's level screen. | New check in many consumers; any consumer added later is unprotected until someone remembers |
| (b) A claim-bearing pack must declare the default | yes | **no**: a manual campaign has no pack | harmed, as (a) | Every committed pack declares an older file; all nine would stop arming |
| (c) Do not move the default until H1 lifts | yes (E2, E6) | yes (E2, E5, E6) | **Preserved** (E12) | The new file is not "active" |

**Why being screened by the held file is unsound for the evidence captures.** The cap council's plan (addendum CAP-COUNCIL-25G83-01-A1 §5) re-sizes the cap, then runs two non-claim windows whose captures both test the new cap and form the corpus of the successor calibration. The held file's level screen is the largest B among 12 members that survived the old cap, which stopped 8 of 24 captures. If the ordinary path applied that screen, a capture with a larger B would be classed as a machine failure and removed. The successor corpus would then be cut off at a limit set by the very selection the cap question is about. The derivation night applies no such screen. Option (c) keeps it available; (a) and (b) close it.

**What (c) costs is nothing the plan needs.** Under the cap council's sequence the cap changes, the new file's recorded estimator digests stop matching the running code, and the file is re-issued twice (an interim re-issue, then the successor). No claim may rest on the new file before that. The original ruling's reasons for issuing now still hold under (c): the loader repair and the promotion tool are proven on real bytes, and the generation is registered as a predecessor.

### 3.3 The ruling

**R-1. The default does not move in this transaction.** `ACTIVE_ACCEPTANCE_ID` and `DEFAULT_ACCEPTANCE_BOUND_PATH` stay at the R7 constants. This replaces §6.1 item (iv), §6.4, and the last two boxes of the flow diagram in §1 of the ruling I amend. The new file is added, registered in `ISSUED_ACCEPTANCE_REGISTRY` and `_D102_GENERATION_DERIVATIONS`, pinned by digest, admitted-and-held at the admission list, and covered by the pinset schema, all as already built.

**R-2. A held file cannot be the default.** The hold table moves to `joulewise/calibration_bracketing.py`, directly under the two default constants, and the module refuses to import if the default is held. Exact text:

```python
ACTIVE_ACCEPTANCE_ID = ANCHOR_V3_R7_ACCEPTANCE_ID
DEFAULT_ACCEPTANCE_BOUND_PATH = ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH
# Issued calibrations that may not yet back any claim. Each entry names its
# hold. The loader hides a held file from every caller that does not state a
# non-claim purpose, and a held file can never be the default.
CLAIM_HELD_ACCEPTANCE_IDS: dict[str, str] = {
    EPOCH_25G83_R1_ACCEPTANCE_ID:
    "H1-25G83-CAP-CADENCE (SCI-25G83-CANDIDATE-01-A1 §5.3)",
}
if ACTIVE_ACCEPTANCE_ID in CLAIM_HELD_ACCEPTANCE_IDS:
    raise RuntimeError("the default calibration acceptance is claim-held")
```

In `joulewise/arm_readiness.py` the literal table is replaced by an import of the same object, so that there is one table and the existing tests that patch it keep working:

```python
from joulewise.calibration_bracketing import (
    CLAIM_HELD_ACCEPTANCE_IDS as _CLAIM_HELD_ACCEPTANCE_IDS,
)
```

Executed: the import works, the two names are the same object, H-T1 to H-T3 pass unedited.

**R-3. The loader hides a held file unless the caller states a non-claim purpose.** Exact text:

```python
def load_calibration_acceptance_bound(
    path: Path = DEFAULT_ACCEPTANCE_BOUND_PATH,
    *,
    allow_claim_held: bool = False,
) -> dict[str, Any] | None:
    """Load the file-pinned D-102 acceptance artifact fail-closed.

    A claim-held generation is returned only to a caller that states a
    non-claim purpose with ``allow_claim_held=True``.
    """

    try:
        raw = read_authentication_input(
            path, grammar="json", label="calibration acceptance artifact"
        )
    except OSError:
        return None
    artifact = _acceptance_bound_from_authenticated_bytes(raw)
    if (
        artifact is not None
        and artifact.get("acceptance_id") in CLAIM_HELD_ACCEPTANCE_IDS
        and not allow_claim_held
    ):
        return None
    return artifact
```

Why here. The loader is the one point every route passes. Capture preflight, bracket evaluation, the in-memory authentication used by the mint (`_authenticated_explicit_acceptance_bound`, which calls the loader), the analysis loader and every script all receive `None` for a held file and refuse as they already do for an unreadable file. No consumer is edited, and a consumer written next month is covered without anyone remembering the hold. This closes the hold refuter's F2 (no consumer checks H1) in one place.

**R-4. Who may pass `allow_claim_held=True`.** In `joulewise/` and `scripts/`: **no file, at this change.** Tests and `tests/verify_calibration_acceptance_corpus.py` may. A later reviewed change may add a governance tool (for example the re-issue tool, when the interim re-issue names this file as predecessor); it edits the census test of §3.4 in the same change. No flag, no environment variable, no command-line option may set it.

**R-5. Refusal wording.** Bracket evaluation's existing branch for a missing file sets the freshness reason. When the file asked for is held, the reason text becomes `acceptance_artifact_claim_held` and the record carries the hold's name from the table; the returned reason code stays `calibration_acceptance_bound_stale`, so no downstream vocabulary changes. This is diagnostic wording. The refusal itself comes from R-3.

**R-6. Release of the hold.** Unchanged in kind: a reviewed change that deletes the table entry and cites the closing ruling of the cap council. It is now also the only change that can move the default to a 25G83 file, because of R-2. Under the cap council's sequence the file that becomes default will be the successor, not this one.

**R-7. What is *not* closed by code, stated plainly.** A manual campaign run by hand at a 25G83 machine can still start and collect raw measurements (E4). That is equally true on main today. It cannot produce a result: a result needs a passed bracket, a bracket needs two valid ordinary captures, and at 25G83 every ordinary capture refuses at preflight while the default is R7 (E2). Captures of a derivation night are excluded from bracket endpoints by existing code (the skip in `discover_calibration_candidates`, `calibration_bracketing.py:1894-1900`; cited by the hold refuter, read by me, not run by me). I did not run a campaign end to end. The repeated hold refutation (§7 step 5) carries this as its charge.

### 3.4 Tests

New file `tests/test_claim_hold_routes.py`. No mock of the loader. "RED" is the behaviour I executed at `325d9f77`; the fix seat records the RED run on that commit and the GREEN run on its head.

| Id | Input | GREEN (required) | RED at `325d9f77` (executed by me) | Wrong implementation it catches |
|---|---|---|---|---|
| HR-1 | **Contract refuter's route.** A pack tree naming R7 passes `_issued_d079`. Then capture preflight with no file named, identity = the new file's epoch. | admitted; preflight raises `acceptance_artifact_epoch_mismatch`, `stale_fields == ['os_build']` | admitted; preflight returns `0.038078579302948` | a moved default |
| HR-2 | Same route, bracket evaluation with no file named, identity at 25G83, ledger snapshot built on the default file's own prior set and cutoff | reason `calibration_acceptance_bound_stale`; artifact id is R7; `stale_fields == ['os_build']` | artifact id is the held file; freshness `fresh`; `claim_eligible: true` | a moved default |
| HR-3 | **Hold refuter's route.** Config `configs/campaigns/p2_015_floors/11_neg8_end/p2015-neg8-reference-end.json` (no launch marker) and policy `configs/campaign_policies/quiet_mac_p2_production.json` (`claim_bearing` true). `authenticate_campaign_writer_preflight` returns `None` with the admission list patched to raise if called. Then, at the 25G83 identity: preflight with no file; preflight with the held path; `issued_calibration_allowance_projection` on the held content; bracket evaluation with the held content passed explicitly. | preflight refuses twice (`acceptance_artifact_epoch_mismatch`, then `acceptance_artifact_unauthenticated`); projection is `None`; evaluation refuses with no artifact | level screen `0.038078579302948` twice; allowance `0.013701`; evaluation proceeds | a hold that lives only at the admission list |
| HR-4 | **Counterfactual for the loader gate.** Same as HR-3's last three calls with `CLAIM_HELD_ACCEPTANCE_IDS` patched empty | held path loads; preflight returns `0.038078579302948`; projection returns `0.013701`; a synthetic bracket of two new endpoints returns `passed` with operative bound `0.0384310413330314` | — | a test that passes for a reason other than the hold |
| HR-5 | Loader called on the held path without the keyword, and with it | `None`; the file | the file; (keyword does not exist) | a gate with the default inverted |
| HR-6 | **Census.** The set of files under `joulewise/` and `scripts/` whose text contains `allow_claim_held=True` | equals the literal set in the test, empty at this change | — | a claim route that opts in quietly |
| HR-7 | `ACTIVE_ACCEPTANCE_ID` is the R7 identifier; it is not in the hold table; a subprocess that imports the module with the default constants set to the new file's exits non-zero with the message of R-2 | as stated | default is the held file | moving the default to a held file |
| HR-8 | The derivation-night input writer's check `_stale_identity_fields`, machine at 25G83, default file | returns `['os_build']` | refuses "ORDINARY night" | closing the non-claim route the cap council needs |

Mutation evidence to record (added to §9 step 5 of the ruling I amend): delete the three-line condition in the loader → HR-3 and HR-5 fail; restore the literal table in `arm_readiness.py` with the entry removed → H-T1 fails; point the default at the new file → the suite cannot import.

Existing tests. Every test file the branch re-pointed because the default moved is restored to main's expectation of what "the default" is (R7, epoch 25F84, level screen and cutoff of R7). Expectations the branch added about the new file stay, reading it by explicit path with `allow_claim_held=True`. **No assertion from main is weakened or deleted.** Known from my prototype run: `test_l1_issued_loads` needs the keyword; `test_validate_powermetrics_fiducial_derivation_only` and `test_epoch_continuation.test_all_acceptance_bytes_and_registry_remain_frozen` fail until restored. I did not reach the remaining modules; §8 lists them all.

The three freezes of §6.3 of the ruling (tools that mean R7 now name R7) stay. They are correct under either default and will be needed when the default does move.

## 4. Item 2 — the doubling trigger

**Do disposed rows count? Yes, and wrongly.** Executed (E1, E9): the evaluation counts every valid ledger row at the file's epoch (`calibration_bracketing.py:2458-2465`). For the new file that count starts at 23, because the eleven disposed rows are valid rows of epoch 25G83. The threshold is 24. One new valid capture trips it.

**Why it is wrong.** The trigger's purpose: when the pool of captures that *could be members* has doubled since the derivation, the statistics are worth re-deriving. A disposed row can never be a member; the decision that set it aside says so, because it was taken under a different launch setting. Counting it says "the corpus has doubled" when the eligible pool went from 12 to 13. The consequence at the head is that the file can never pass a single bracket, since a bracket needs two new captures.

**The exact fix**, in `evaluate_calibration_bracket`, replacing the statement that begins `valid_counts_by_epoch = [`:

```python
    # Rows set aside by a decision this artifact declares are diagnostics that
    # can never be members, so they do not count toward corpus doubling.
    disposed_ids = disposed_content_ids_for(
        artifact["prior_observation_set"].get("disposing_decision_ids")
    )
    if disposed_ids is None:
        return result, ("calibration_acceptance_bound_stale",)
    valid_counts_by_epoch = [
        sum(
            observation.disposition == "valid"
            and observation.content_id not in disposed_ids
            and dict(observation.identity_epoch) == dict(epoch)
            for observation in distinct_observations.values()
        )
        for epoch in judged_epochs
    ]
```

`disposed_content_ids_for` is already imported in that module (line 20). The seven older files declare no decision, so their set is empty and their behaviour is unchanged. A file that declares a decision the table does not know has already been refused by the loader; the `None` branch is a second refusal, not a new path.

**Executed on the prototype (E10).** With the hold emptied in memory: 1, 2, 4 and 11 new valid captures do not trip the trigger; the 12th does (12 + 12 = 24).

**What this means for the file's usable life.** After the fix, the new file goes stale at the twelfth new valid ordinary capture at 25G83, which is at most six brackets. That is a short life by design of a 12-member corpus, and it is moot for this file: it is held, it is not the default, and the cap change will make it stale first. It matters for the interim re-issue and the successor, which inherit the rule. The successor registration must state the expected count.

**Tests** (in `tests/test_calibration_bracketing.py`, each loading the real new file with `allow_claim_held=True` and the hold table patched empty):

| Id | Input | Expected | RED at `325d9f77` |
|---|---|---|---|
| DT-1 | 1 new valid capture at 25G83 | `observed_triggers == []` | `['corpus_doubles_from_12_to_24']` (executed) |
| DT-2 | 11 new valid captures | trigger absent | present |
| DT-3 | 12 new valid captures | trigger present; reason `calibration_acceptance_bound_stale` | present (for the wrong count) |
| DT-4 | A new valid capture whose identifier is patched into the decision's table | not counted | — |
| DT-5 | An R7 evaluation with 34 valid rows at 25F84 | `corpus_doubles_from_17_to_34` observed, as on main | same: proves old files are unchanged |

**Ordering rule.** The trigger fix may not merge in any commit that lacks R-2 and R-3 (E11). One commit carries both.

## 5. Item 3 — S2, S3, N1 and the nits

| Item | Ruling | Exact effect |
|---|---|---|
| **S1** (the no-pack route is closed at 25G83; more consumers move with the default than listed) | **Adopted; dissolved by R-1.** | With the default at R7 the derivation night stays open at 25G83 (E12) and no consumer moves. The sentence "Windows that run without a pack are not affected" becomes true again. §6 gives the record text. |
| **S2** (the promotion tool checks cited digests for form only) | **Adopted, modified.** | In `scripts/promote_calibration_candidate.py`: for every object in the issuance text that has both `relative_path` and `file_sha256` (the `rulings`, `source_candidate`, the `source_rulings` of the network-time block), the tool hashes the bytes at `<repository root>/<relative_path>` and refuses unless equal; a missing file refuses. For the preserved log, the tool recomputes the digest the block names in the way the block names it (the contract refuter confirmed the recorded value is the sha256 of the decompressed text). `network_time_provenance.text` must equal the `text` of disclosure D8. `claim_eligible_meaning` must equal the constant sentence of §7.4 of the ruling, held in the tool. `hold_enforcement` must be a non-empty string. Modified in one respect: `hold_enforcement` is not pinned to a constant, because this addendum changes it and the hold's release will change it again. **Test P6:** the contract refuter's six altered texts P4a to P4f, each refused; RED on `325d9f77`, where all six were accepted. |
| **S3** (the bytes assert a gate that is open, and omit A3) | **Adopted.** The issued bytes change. | Lead edits the issuance text (`10-issuance-text.json` and its builder). `required_verification` becomes exactly: `complete: cold science gate SCI-25G83-CANDIDATE-01 over exclusions, per-night diagnostics, the screen-challenge outcome and the D-125 default; addenda A1, A2 and A3. The merge gate of design ruling D138-25G83-DESIGN-01 section 9, as amended by addendum D138-25G83-DESIGN-01-A1, is recorded in the issuing record and is not asserted by these bytes`. `issuance_record.transaction` becomes: `D-138 issuance of epoch 25G83, design ruling D138-25G83-DESIGN-01 as amended by addendum D138-25G83-DESIGN-01-A1`. `issuance_record.hold_enforcement` becomes: `H1 is enforced outside these bytes, in code, at three places: this file is not the default calibration; the loader returns it only to a caller that states a non-claim purpose; and the arm admission list refuses a pack that names it. Lifting the hold changes no byte of this file`. The file is regenerated by the tool, never by hand. The input seal must still come out `e7363bdd…b011`. Digest X and the whole-file seal change; the registry pin and the issuing record follow. |
| **N1** (validator rules (b) and (f) cannot be observed) | **Adopted.** | New test L10: patch a second decision into the table whose identifier set contains one row of the prior set; the file, which does not declare it, must refuse. With rule (b) removed the test must fail. Rule (f) stays as a second guard, with a code comment: "implied by the completeness equality; kept so that a change to that equality cannot silently admit a disposed exclusion". The mutation record states that L4 catches "ignore the declaration" only for the combined mutation (drop (b) and use the whole table), and records that combined run. |
| **N2** (the input-seal stop is never reached by a test) | **Adopted, modified.** | Keep the stop. New test P7: patch the production function `derivation_input_sha256` to return a different digest; the tool must refuse with the input-seal message. With the stop removed P7 must fail. |
| **N3** (D-185's revisit trigger is too narrow) | **Adopted.** | D-185 text in §6. |
| **N4** (the table-equality check can be skipped by a caller-supplied digest) | **Adopted.** | Comment above the condition in `parse_disposition_registry`: "Equality with the code table is required only for the production pin. A caller that supplies another digest (tests do) gets a parse without that check and must not treat the result as authority." `joulewise/calibration_dispositions.py` enters the write scope for this comment only. |
| **N5** (L9 guards less than the ruling asked) | **Adopted.** | L9 guards `builtins.open`, `os.open` and `Path.read_bytes` for the disposition file's path, and covers the new file as well as the seven old ones. |
| **N6** (the network-time block's keys differ from the ruling's sketch) | **Adopted.** | The built keys stand; the sketch in §7.2 of the ruling was an illustration. The issuing record states the built keys and that they follow addendum A3. |
| **N7** (the tool's self-check compares an object with itself) | **Adopted.** | Comment at the self-check: "Not an independent check: both sides derive from the same parsed object. The independent check is test P2 on the written file." |

**The two factual flags from the pedagogy pass.** Both are correct and both are adopted. (i) The two systematic-invalid rows of epoch 25F84 do carry B values; a systematic-invalid row is a capture whose B exceeded the level screen then in force. My E1 inventory agrees on the counts (25F84: 30 valid, 6 ordinary-invalid, 2 systematic-invalid; 25G83: 23 valid, 25 ordinary-invalid). (ii) §4.1 of the ruling I amend said "1 named exclusion". That was wrong. The file has none (executed: `excluded_members` is `[]`), and 30 + 12 + 11 = 53 accounts for every valid row. The ruling's worked example is corrected by this sentence; the mechanism it specified is unaffected.

## 6. Item 4 — the old-epoch replay (§10 item 2 of the ruling)

**What the ruled condition was for.** It guarded one mechanism: once the default moves to a file that judges only 25G83, a measurement recorded at 25F84 and evaluated through the default comes back stale. The lead was to run one recorded 25F84 analysis at main and at the head and compare.

**What the evidence shows.** No recorded 25F84 analysis passes on current main from recorded inputs: the brackets of the July measurement are historical imports, which current code skips, and every later finalized row is 25G83. Main returns `instrument_calibration_bracket_missing` with R7 fresh. The head returned `calibration_acceptance_bound_stale` on `os_build`. No number was produced on either side.

**Ruling.**

1. **For this transaction the condition is met by identity, and the replay is re-run to show it.** Under R-1 the default does not move, so the mechanism the condition guarded does not arise. The lead re-runs the second replay's commands (`oldepoch-2`, V2 to V4) at main and at the fix head. **Required outcome: the two outputs are byte-identical** (same refusal `instrument_calibration_bracket_missing`, same acceptance identifier R7, same freshness `fresh`; equal sha256 of the two output files). This is the branch "Identical: proceed" of the ruled text, read literally. Any difference stops the transaction.
2. **The evidence gathered at `325d9f77` does not satisfy the condition as ruled, and I do not reinterpret it to do so.** The ruled text let a clean stale refusal proceed where main produced a result to compare against. Here main produced none. A comparison with no baseline shows nothing about numbers. The second replay's own verdict, STOP, was the correct reading of the text.
3. **For the later transaction that does move the default** (at the hold's release): the condition is restated as follows, because no passing 25F84 baseline exists. (i) The record states, in these words, that no recorded 25F84 analysis passes on main from recorded inputs, with the two reasons above. (ii) A clean refusal naming the stale calibration is then sufficient at the head. (iii) Before that merge, a route that names R7 explicitly must exist for re-evaluating old-epoch results, with a test, so that the move removes no ability that main has. This restatement changes a ruled stop condition; it is made here explicitly and applies only to that later transaction.

## 7. Item 5 — D-185 and the issuing record

### 7.1 Claims about the hold that must change

The refuters showed that three sentences were false as built. With the design of §3 they are replaced, not defended.

| Where | Text at `325d9f77` | Replacement |
|---|---|---|
| `docs/decision_log.md:12245` (D-185, Decision 5) | "…so no pack naming it can arm." | "Hold H1 is enforced in code at three places. (1) The new file is not the default: `ACTIVE_ACCEPTANCE_ID` stays R7, so every capture and every evaluation at a 25G83 machine that names no file is judged by R7 and refuses on the operating-system build, exactly as before this change. (2) The loader returns a held file only to a caller that passes `allow_claim_held=True`; no file under `joulewise/` or `scripts/` does, and a test fails if one starts to. (3) The arm admission list refuses a pack that names the held identifier. The hold table is `CLAIM_HELD_ACCEPTANCE_IDS` in `joulewise/calibration_bracketing.py`; the module refuses to import if the default is in it." |
| `docs/decision_log.md:12261` (Hold cost) | "Windows that run without a pack are not affected." | "H1 also stops a pack that names the new file for a rehearsal with no claim. Windows that run without a pack (derivation nights) are not affected, because the default stays R7 and the derivation night is the route for a machine whose epoch the default does not judge. The first design moved the default, which closed that route at 25G83; addendum D138-25G83-DESIGN-01-A1 reversed it for that reason." |
| `docs/decision_log.md:12263` (Likely re-issue) | "…while H1 keeps any claim off this file." | "Issuing now registers the generation and exercises the loader repair and the promotion tool on real bytes. It does not make the file the machine's default. If the cap is re-sized (route R), binding B4 makes this file stale and forces a re-issue; the file that becomes the default at the hold's release will be a successor." |
| D-185, Decision 1 and index row | default moved; digest X `80c23036…` | default unchanged; new digest X and whole-file seal as regenerated |
| D-185, revisit trigger (N3) | "a new disposition decision touching 25G83 rows" | "a new disposition decision that disposes **any** row of this file's 86-row prior set, of either epoch. The file then stops loading. That failure is closed and is cured only by a re-issue." |
| D-185, new Consideration | — | "*Doubling trigger.* The file goes stale when 12 further valid captures at 25G83 exist in the ledger. The eleven set-aside rows do not count; before addendum A1 they did, and the file would have gone stale at the first new capture." |
| Issuing record §4.4 (line 93, Mechanism, Known cost, Release) | the framing above | the three replacements above, in the record's words |
| Issuing record, new §4.5 "What the refuters found" | — | One paragraph each: the contract refuter's route (a pack naming R7, judged by the default); the hold refuter's route (a manual campaign, no pack); the doubling defect and why it masked both; the cure. Cites this addendum by path and digest. |
| Issuing record §8 (old-epoch replay) | two attempts, STOP | adds the outcome of §6 item 1 of this addendum, with the two output digests |
| Issuing record, header "head at drafting" | `e14e00bb…` | the final head |

**A sentence neither document may contain:** any statement that a claim is impossible at 25G83. What is shown is that no result can be produced through the code routes tested. R-7 states what is not closed by code.

### 7.2 Pedagogy fixes

**Confirmed: all 37 are to be applied** (A1 to A25, B1 to B10, C1, C2), with the replacement texts the pass gives, subject to three notes.

1. Where a pedagogy replacement describes the hold or the default (A17 Mechanism and Release; B3; B8), the text of §7.1 governs and the pedagogy gloss is fitted to it. In particular B8's "every measurement at 25G83 would be refused as stale" remains true after this change and should say so in the present tense.
2. A9 and A12 carry the two factual corrections of §5.
3. The pass asked the lead to verify three glosses against their sources (ruling A267; "the writer"; the two floor definitions) and to fill one path (A15; the preparation tool is `scripts/issue_calibration_acceptance_generation.py`, confirmed by my `grep`). Those verifications are done before the text lands, and the record says they were.

A second pedagogy pass runs on the revised texts (§8 step 7), because §7.1 adds new terms: "default", "loader", "non-claim purpose", "derivation night". Each is built or glossed at first use.

## 8. Item 6 — the revised gate sequence and the write scope

### 8.1 Gate sequence to merge

Steps replace §9 of the ruling I amend from its step 5 onward; steps 1 to 4 of that section are repeated on the new head because the bytes change.

1. **Lead:** land this addendum on main with the records. Edit the issuance text and its builder per S3. Commit before the seat starts, so the seat's worktree contains them.
2. **Fix seat** (one seat, scope of §8.2): R-1 to R-5; the trigger fix; S2, N1, N2, N4, N5, N7; regenerate the issued file with the tool and update the pin; restore re-pointed tests; add `tests/test_claim_hold_routes.py`, DT-1 to DT-5, L10, P6, P7.
3. **RED record.** Each of HR-1, HR-2, HR-3, HR-5, DT-1, DT-2 and P6 is run against `325d9f77` and shown to fail, then against the fix head and shown to pass. Both runs are saved with commit ids.
4. **Pre-issue re-hash and independent replay** (§9 steps 1 and 2 of the ruling) on the new bytes, by a seat that did not write them. Item (vi) of step 2 changes: on the real ledger, read-only, **the default evaluates "stale" on `os_build` for a 25G83 identity and "fresh" for a 25F84 identity; the new file, loaded by path with the keyword, evaluates "fresh" for a 25G83 identity.**
5. **Old-epoch replay** per §6 item 1: byte-identical outputs.
6. **Whole suite** on the head merged with current main. Green, no new skip.
7. **Mutation evidence:** the list of the ruling's §9 step 5, plus the three mutations of §3.4, plus N1's combined mutation.
8. **Two refuters, fresh seats, different families from each other.** *Hold charge:* find any route from the issued file to a claim-bearing result. Include, by execution where no hardware is needed: every caller of the loader; every place the keyword could be set; whether a valid bracket endpoint at 25G83 can be written to the ledger while the default is R7 (R-7); whether a derivation-night capture can become a bracket endpoint. *Contract charge:* the new digest and pins; S2's checks; that no test from main was weakened (compare each restored test file with main's). **If the hold refuter finds a route, the transaction stops until it is closed.** That sentence is unchanged and still binds.
9. **Pedagogy pass** on the revised issuing record and D-185.
10. **Re-audit of the difference** after every fix round.
11. **Cold final pass** on the final head: a fresh judge, given the final difference, the issuing record, the ruling and this addendum, confirms each numbered item of both is met.
12. **Merge** as one commit.
13. **Post-merge, on main:** the four estimator digests and the cap; the loader with no argument returns R7; the loader on the new path returns `None` without the keyword and the new identifier with it; sha256 of the issued file equals the pin; `_issued_d079` refuses the new identifier; capture preflight at a 25G83 identity refuses on `os_build`. Recorded in the issuing record.

**Stops.** Those of §10 of the ruling stand, with item 2 replaced by §6 here. Added: stop if any of HR-1, HR-2, HR-3 cannot be shown RED on `325d9f77`, because then the test does not see the defect it is named for.

**Before the next window of any kind at 25G83:** H5 and H6 (network time), as the ruling and the cap council already require. Unchanged, and outside this change.

### 8.2 WRITE_SCOPE for the fix seat — exhaustive

```
configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json   (tool output only)
joulewise/calibration_bracketing.py
joulewise/arm_readiness.py
joulewise/calibration_dispositions.py                                  (N4 comment only)
scripts/promote_calibration_candidate.py
tests/test_claim_hold_routes.py                                        (new)
tests/test_calibration_bracketing.py
tests/test_calibration_dispositions.py
tests/test_promote_calibration_candidate.py
tests/test_arm_readiness_evidence_author.py
tests/test_acc_25g83_rev5.py
tests/test_calibration_exits.py
tests/test_calibration_live_three_window.py
tests/test_calibration_writer_crash_matrix.py
tests/test_epoch_continuation.py
tests/test_epoch_equivalence_check.py
tests/test_floor_mint_pinsets_schema.py
tests/test_issue_calibration_acceptance_generation.py
tests/test_issuer_corpus_root.py
tests/test_mint_floor_artifact_generalized.py
tests/test_powermetrics_fiducial.py
tests/test_validate_powermetrics_fiducial_derivation_only.py
tests/verify_calibration_acceptance_corpus.py
```

Rules for the seat. Nothing outside this list: not the four estimator files, not the disposition file, not the issuance text or its builder, not any document, not any older calibration file, not any pack, not `scripts/validate_powermetrics_fiducial.py` or any other consumer (the design needs no consumer edit; if the seat believes one is needed, that is a finding, and it stops and reports). The three scripts frozen to R7 and the pinset schema are already correct and are not in scope. If the suite shows a failure whose cure lies outside the list, the seat stops and reports the path; the lead amends the scope in writing, and an amendment may add test files only.

**Lead-owned, outside the seat:** this addendum and the records on main; `10-issuance-text.json` and `build_issuance_text.py`; `00-issuing-record.md`; `docs/decision_log.md` (D-185, its index row, the dated note on the D-126 disposition entry); the pedagogy fixes; the trackers.

## 9. Limits of this ruling

- The prototype is a scratch copy with four text edits. It shows the design closes the routes tested and keeps the hold tests passing. It does not show that an implementation is complete.
- Of the 14 affected test modules, 7 ran to completion on the prototype: 4 passed (`test_promote_calibration_candidate`, `test_floor_mint_pinsets_schema`, `test_epoch_equivalence_check`, `test_acc_25g83_rev5`) and 3 showed the failures listed in §3.4. From `test_arm_readiness_evidence_author` I have a result only for its three hold tests, which pass; my whole-module run of it produced no summary line and I did not repeat it. The other 6 modules, and the whole suite, I did not run.
- E4 and R-7: I did not run a campaign. That a manual campaign cannot yield a result rests on E2 and on reading the code that a bracket needs two valid ordinary captures.
- The synthetic brackets use a ledger snapshot I built in memory from the file's own prior set. They exercise the real evaluation code and the real file, not the real ledger.
- I did not read the cap council ruling that its addendum amends. If it conflicts with §3.2 on how the evidence windows run, that council governs its own subject and this addendum's R-1 should be re-checked against it.
- I did not verify S2's six probes or N1's mutations myself; I rely on the contract refuter's saved outputs, which the fix seat's RED record re-runs.

## Summary

1. The hold was open, as both refuters said: moving the default to the new file let it judge windows that never name it, and the only thing that stopped a passing result was an unrelated counting defect, which I confirmed by running it.
2. The cure is to issue and register the new file but leave R7 as the default until the hold lifts, and to make the loader hand a held file only to code that states it makes no claim; in a scratch build both refuters' routes went from returning the held numbers to refusing, and the non-claim capture route the cap plan needs stayed open.
3. Before merge: fix the counting defect in the same commit, correct the file's own text and the two records that overstated the hold, show each new test failing on the old code, and send fresh refuters to look for a route again; if they find one, the transaction stops again.
