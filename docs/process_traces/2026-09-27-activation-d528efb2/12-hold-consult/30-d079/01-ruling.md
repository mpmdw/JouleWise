RULING: HOLD-BY-CONSTRUCTION-01-A1 ISSUED

# Cold ruling HOLD-BY-CONSTRUCTION-01-A1 — the bare identifier "d079" is refused, stays refused, and three test fixtures are re-pointed to a registered calibration file

Judge: Claude Fable 5.1, cold session, one foreground session, 2026-09-28, about 03:46 to 04:10 PDT. Candidate read: `feat/2026-09-27-d138-25g83-issuance` at `96852358`, compared with main at `9eab16f8`. I modified no repository file except this one. Everything I ran, I ran in scratch copies under `/tmp/cg-d079-d528efb2/` (a clone of the branch with three detached worktrees). The seat's worktree was still clean at `96852358` when I finished.

**The ruling in one paragraph.** Refusing the bare identifier `"d079"` is correct. It must not be given a build, because it names no file and a build can only be copied from a file. The two fixture lines that declare it are changed to `"d079_calibration_acceptance_v2_n17_r7"`, by the lead, as a test-only commit. That is not a fourth round. `"d079"` stays in the admitted set for this transaction, where it is inert, and two new tests pin that it is inert.

## 0. Contamination disclosure

1. **Injected by the session harness before the charge, not opened by me:** the owner's global instruction file (a writing standard and a list of skill names); the project instruction file of my worktree (notes on the model bridge); a one-line-per-entry index of the owner's memory store; the five most recent commit subjects.
2. **What in that material could lean on this question.** The memory index carries one-line summaries of owner directives: that test-only and document-only changes get lighter gates than measurement code, that refusals should exist only for physics, evidence and pre-registration, and that gates must be sensible. Each of these leans toward answering "yes, a test-only change is fine". I did not use them. Section 4 rests on the text of the ruling in force and on what I executed.
3. **The charge carries the lead's own position** on question 2 ("it should not, if no production logic changes") and the lead's search result. I treated the first as a claim to test and re-ran the second myself, more widely (§2, E4 and E5).
4. **The seat's report recommends the re-point.** I read it as a recommendation, not as evidence. I reproduced its three failures myself.
5. **Not opened:** any memory file, any skill file, `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, any `CLAUDE*.md`. My scratch copies contain those files on disk because they are tracked; I did not open them there either.
6. **Same model family.** I am Fable 5.1, as was the judge of the ruling in force. I did not sit on it.
7. **Read in full:** the ruling in force; the seat's fix-round-3 report. **Read in part:** `joulewise/arm_readiness.py` (the admission list and its difference from main), `joulewise/claim_hold.py` (whole), `joulewise/calibration_bracketing.py:200-235`, the two fixture regions and the failure output of `tests/test_arm_readiness_lifecycle.py`.

## 1. Words used

So that this file reads alone:

| Term | Meaning |
|---|---|
| **Calibration file** | A JSON file stating how large the instrument's timing uncertainty may be before a measurement is refused. Each records the operating-system build it was derived on. |
| **Build** | The operating-system build string the machine reports. The old build is 25F84, the new one 25G83. |
| **Held build** | A build at which no result may be reported as a finding until a named open question is closed by a written ruling. Today one build is held: 25G83. |
| **The ruling in force** | HOLD-BY-CONSTRUCTION-01. It made the hold a property of the build, not of any one file. |
| **Pack** | The frozen set of plans one measurement session runs from. A pack declares which calibration file judges it, in a block called its acceptance policy. |
| **Identifier** | The name of a calibration file, for example `d079_calibration_acceptance_v2_n17_r7`. |
| **Registered** | An identifier is registered when code records its file path and the SHA-256 of its bytes (table `ISSUED_ACCEPTANCE_REGISTRY`). Eight identifiers are registered. |
| **Build table** | `REGISTERED_GENERATION_OS_BUILD`: for each registered identifier, the build copied from inside its file. |
| **R7** | `d079_calibration_acceptance_v2_n17_r7`, derived at build 25F84. It is the default: the file code reads when it names none. |
| **The new file** | `d079_calibration_acceptance_v2_n12_25g83_r1`, derived at the held build 25G83. |
| **The bare identifier** | The five characters `d079`, with nothing after them. It is not registered. It has no path, no digest and no file. |
| **Admitted set** | `_ISSUED_D079_IDS` in `joulewise/arm_readiness.py`: the identifiers a pack may declare and still be treated as using an already issued calibration. |
| **Admission list** | The function `_issued_d079`, which applies the three checks drawn in §3.2. When it answers "no", the pack is treated as introducing a new calibration and an extra readiness check becomes required. |
| **Fixture** | Made-up input that a test builds for itself. Here: a made-up pack. |
| **Assertion** | The line of a test that states what the result must be. |
| **Round** | One cycle in which production logic for the hold is changed. The ruling in force allows three and forbids a fourth (its §6.2). |
| **RED, GREEN** | A test that fails (RED) or passes (GREEN). RED must be a failed assertion, not a failure to import. |

## 2. Facts

**Executed** means I ran it in this session. **Read** means I opened the file and read the lines.

| # | Fact | How |
|---|---|---|
| E1 | At `96852358` the bare identifier is refused and every registered 25F84 identifier is admitted. Of the nine members of the admitted set, seven are admitted, the new file is refused for the held build, and `d079` is refused with the hold name `UNKNOWN-OS-BUILD (a build that cannot be read is treated as held)`. | Executed: one probe per member through `_issued_d079`. |
| E2 | At main `9eab16f8` the bare identifier is admitted. | Executed: same probe, result `True`. |
| E3 | The refusal is caused by the missing build entry and by nothing else. With the entry `"d079": "25F84"` planted **in memory**, the bare identifier is admitted; with the plant removed it is refused again. | Executed. |
| E4 | No pack declares the bare identifier. The nine committed packs under `configs/campaigns/` each declare a full identifier. The custody store `/Users/edr/night-custody` holds 108 pack files (`plan_tree.json`); I parsed all 108: 72 declare a full identifier under the key `issued_acceptance.acceptance_id`, 36 under `issued_artifact_id`, none declares `d079`, and **none uses the key `issued` at all**. | Executed. |
| E5 | In the whole tree at `96852358` the quoted string `"d079"` occurs four times: the admitted set (`arm_readiness.py:6194`), the two fixture lines (`tests/test_arm_readiness_lifecycle.py:313` and `:475`), and one process-trace document. A search of every branch and every past commit for a declaration of the bare identifier under `configs/`, `scripts/`, `joulewise/` or `docs/contracts/` found nothing. | Executed. |
| E6 | The bare identifier entered the admitted set in commit `696576c0` (2026-08-12). The set then had two members: `"d079"` and `"d079_calibration_acceptance_v2_n19"`. The fixtures date from the same commit and from `66a433dd` (2026-08-17). | Executed (`git log -S`, `git show`). |
| E7 | The only production statement that reads the policy key `issued` is the admission list itself (`arm_readiness.py:6211`). | Executed (search of `joulewise/` and `scripts/`). |
| E8 | `tests/test_arm_readiness_lifecycle.py` at main: 69 tests, OK, 1 skipped. | Executed. |
| E9 | The same file at `96852358`: 69 tests, **3 failures**, 1 skipped. The three are `test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`, `test_boot_session_change_voids_verification_and_consumption`, and `test_historical_predecessor_resolves_and_still_anchors_the_chain`. Each fails on an assertion that a status is `PASS` and finds `REFUSE`. This matches the seat's report. | Executed. |
| E10 | The same file at `96852358` **with only the two fixture lines changed to R7**: 69 tests, OK, 1 skipped. The same count as main. | Executed. |
| E11 | The three tests, with the same two-line change applied **to main**: 3 tests, OK. | Executed. |
| E12 | On the re-pointed tree, `tests.test_claim_hold_routes` and `tests.test_claim_hold_census`: 28 tests, OK. | Executed. |
| E13 | The two-line change touches no assertion. Both lines sit inside the dictionaries that the helper functions `write_predecessor_pack` and `make_go_fixture` build. After the change the file contains no occurrence of the bare identifier. | Executed (`git diff`), read. |
| E14 | Between main and `96852358` the lifecycle test file differs by two added lines, which patch the machine-build reader to return `25F84` in one test. That is the amendment §4.5 of the ruling in force permits. | Executed (`git diff`). |

## 3. Question 1 — is refusing the bare identifier correct?

**Ruling: yes. The refusal is the design working. The bare identifier must not be given a build.**

### 3.1 The forcing problem

The ruling in force changed the question the code asks. It used to ask "is this name on a list?" It now asks "what build does this file judge, and is that build held?" The second question has an answer only for a name that stands for a file, because the build is a fact written inside the file. The bare identifier stands for no file (E5, and §1). So for it the second question has no answer, and the ruling in force says what to do then: "a build that cannot be read is treated as held" (its §3.2, the text of `UNKNOWN_BUILD_HOLD`).

### 3.2 The mechanism, with three worked examples

The admission list applies three checks, in this order, to what the pack's acceptance policy declares.

```
   the identifiers the policy declares, under any of three keys:
   "issued", "issued_acceptance.acceptance_id", "issued_artifact_id"
            |
   [A]  is there exactly one distinct identifier?        no --> not admitted
            |  yes
   [B]  is it a member of the admitted set?              no --> not admitted
            |  yes
   [C]  look the identifier up in the build table
            |
            +-- no entry: build unknown, treated as held --> not admitted   (1)
            +-- entry is a held build                    --> not admitted   (2)
            |
            v  entry is a build that is not held
         admitted                                                           (3)
```

Named elements. **[A]**, **[B]** and **[C]** are the three checks, in the order the code runs them. The three keys on the top line are the three places a policy can write an identifier. The numbers at the right mark where each worked example ends:

| Example | Declared | [A] | [B] | [C] build table says | Result (executed, E1) |
|---|---|---|---|---|---|
| (1) | `d079` | one identifier | member | no entry | not admitted |
| (2) | `d079_calibration_acceptance_v2_n12_25g83_r1` | one identifier | member | `25G83`, held | not admitted |
| (3) | `d079_calibration_acceptance_v2_n17_r7` | one identifier | member | `25F84`, not held | admitted |

On main only [B] existed, so example (1) was admitted (E2).

### 3.3 Why the bare identifier cannot be registered with a build

1. **There are no bytes to copy a build from.** The ruling in force defines each entry of the build table as a value "copied from that file's `identity_epoch.os_build`", and its check C-7 compares each entry with the file. The bare identifier has no file. An entry for it would be the only entry in the table that nothing can check.
2. **What the evidence does say, and its limit.** When the bare identifier was introduced, the admitted set was `{"d079", "d079_calibration_acceptance_v2_n19"}` (E6). The reasonable reading is that the bare form was shorthand for "the issued calibration", and the only one then was `…n19`, whose build is 25F84. That is an inference about what someone meant in August. It is not a property of any bytes. Today eight calibration files are registered, at two builds, one of them held, and the bare form does not say which it means. **So the build of the bare identifier cannot be known, and I do not name one.**
3. **Registering it would reopen what the ruling in force closed.** A pack could then declare a name that is admitted while saying nothing about which file judges it. That is a rule about a name and not about a build.
4. **It would be a production change after round 3,** which §6.2 of the ruling in force forbids.

### 3.4 Does the refusal harm any existing pack?

No. No pack in the repository or in custody declares the bare identifier, and none uses the key `issued` (E4). The refusal changes the outcome of test fixtures only.

## 4. Question 2 — may the fixtures be re-pointed, and is that a fourth round?

**Ruling: the fixtures are re-pointed to R7. The lead makes the change at the bench. It is part of landing fix round 3. It is not a fourth round and it does not use up the one closing pass.**

### 4.1 The change, exactly

In `tests/test_arm_readiness_lifecycle.py`, two lines:

```
line 313   before:             "issued": "d079",
           after:              "issued": "d079_calibration_acceptance_v2_n17_r7",

line 475   before:  "acceptance_policy": {"selection": "issued_d116_artifact_only", "issued": "d079"},
           after:   "acceptance_policy": {"selection": "issued_d116_artifact_only", "issued": "d079_calibration_acceptance_v2_n17_r7"},
```

Indentation is unchanged. No other line of that file changes. The patch I tested is kept at `/tmp/cg-d079-d528efb2/repoint.diff`, SHA-256 `309494207080efd7d29da83d452f8480fc7ec9ba6f46cdf25fb4a2f00a82f89d`. Scratch does not last, so the text above is the authority.

### 4.2 Why R7

- It is registered, its build is 25F84, and that build is not held (E1).
- It is the default, and the ruling in force makes the code refuse to import if the default is ever a held-build file. It is therefore the registered identifier least likely to become held without anyone noticing.
- The ruling in force already lists "a policy naming R7 under one key" as a control that must be admitted (its test E-5c). The fixtures then declare a case that has its own test.
- Executed: with R7 the whole file passes, 69 tests, the count main has (E10).

Any registered 25F84 identifier would be admitted. I tested R7 and rule R7, so that the bench change equals the change that was run.

### 4.3 Why this weakens no assertion from main

The ruling in force stops the transaction if "an assertion from main [is] weakened". Three observations say none is.

1. No assertion line changes (E13).
2. The three tests pass on **main** with the re-pointed fixtures (E11). So what they assert never depended on the bare form. Their subject is what their names say: one launch capability spent once, a reboot voiding a verification, a chain of freeze receipts. The fixture's job is to be "a pack that declares an already issued calibration", and it still is.
3. One thing main covered by accident does go away: that the bare form is admitted. The ruling in force reverses that behaviour on purpose. A reversed behaviour left untested can return unnoticed, so §4.4 adds a test that states the new behaviour.

### 4.4 Two tests to add, both in files already in the seat's scope

**E-12, in `tests/test_claim_hold_routes.py`.** Input: a policy with selection `issued_d116_artifact_only` and `issued` set to `d079`. Required: `_issued_d079` returns `False`, and `claim_hold_for_acceptance_id("d079")` returns the unknown-build hold. RED by assertion at main `9eab16f8`, where the first value is `True` (E2). GREEN at the fix head (E1). Control: with `"d079": "25F84"` planted in memory in the build table, the first value is `True` (E3), which shows the test passes because of the missing build and for no other reason. The test follows that file's existing rule for RED: it imports only names that exist at the old commit and reaches newer functions through the file's fallback helper.

**C-8, in `tests/test_claim_hold_census.py`.** For every member of the admitted set: if the admission list admits it, it is a key of `ISSUED_ACCEPTANCE_REGISTRY`. Today seven members are admitted and all seven are registered; the one member that is not registered is `d079`, and it is refused (executed). Proof that C-8 can see: plant `"d079": "25F84"` in the build table in memory, and C-8 must turn RED.

I ran the behaviour both tests state, as probes. I did not write the tests. The lead writes them and records their RED and GREEN runs.

### 4.5 The scope amendment

§4.5 of the ruling in force lets the lead amend the scope "with test files only, and only to patch the machine-build reader". This addendum adds, and adds only:

```
tests/test_arm_readiness_lifecycle.py     the two lines of §4.1
tests/test_claim_hold_routes.py           test E-12
tests/test_claim_hold_census.py           test C-8
```

### 4.6 The stop rule

The ruling in force says: "Fix round 3 is the last round that changes production logic for the hold."

- **This change is not a round.** A round changes production logic. This change touches three test files and no file under `joulewise/`, `scripts/` or `configs/`.
- **It does not use the closing pass.** The closing pass is what may follow findings made at the merge gates. Those gates have not run. The seat stopped and reported the path, as §4.5 told it to; this finishes the round-3 head so that the whole-suite gate can be run at all.
- **The round count does not move.** If a refuter later finds a route, or a cure needs production logic, the transaction still stops for good.

### 4.7 Conditions, checked by the lead at the bench and recorded with output

1. The change is one commit on top of `96852358`. `git diff --stat 96852358 HEAD` lists the three test files of §4.5 and nothing else.
2. The lifecycle file's difference is the two lines of §4.1, exactly.
3. `tests.test_arm_readiness_lifecycle`: 69 tests, OK, 1 skipped.
4. E-12: RED at `9eab16f8` by assertion, GREEN at the new head, control as stated.
5. C-8: GREEN, and RED under the planted entry.
6. **If any test needs an assertion changed to pass, or condition 1 cannot be met, stop** under the last row of §6.2 of the ruling in force.
7. The contract refuter's charge (gate 7 of the ruling in force: "that no test from main was weakened") names this commit and this addendum. The re-audit of the difference (gate 9) includes it.

## 5. Question 3 — should the bare identifier leave the admitted set?

**Ruling: not in this transaction.**

- **It is inert.** Check [C] refuses it on every call (E1). For every possible input the admission list returns the same answer whether the member is present or deleted, so long as the build table has no entry for it. C-8 fails if such an entry ever appears.
- **Deleting it edits `joulewise/arm_readiness.py`.** After round 3 the ruling in force permits changes to tests, comments and record wording only. A deletion that changes no behaviour is still a change to a production file, and it would have to pass the re-audit and the refuters as one. I also did not search whether anything pins that file's digest. The gain is tidiness. The cost is a production edit inside a transaction whose stop rule exists to prevent production edits.
- **The record must not mislead.** A reader who sees `"d079"` in the set will think it is admitted. The issuing record and the decision-log entry carry this sentence: *"The bare identifier `d079` remains listed in the admitted set and is refused, because it names no registered calibration file and so has no build; no pack in the repository or in custody declares it."*

**Later, outside this transaction,** as an ordinary reviewed change after the merge: delete the line `    "d079",` from `_ISSUED_D079_IDS` (`joulewise/arm_readiness.py:6194` at `96852358`). E-12 and C-8 pass before and after, because the bare form is then refused at check [B] and no longer at check [C].

## 6. Limits of this ruling

- **I ran three test files, not the whole suite:** the lifecycle file (at main, at the fix head, re-pointed) and the route and census files (re-pointed). The whole-suite gate remains the lead's.
- **E-12 and C-8 are specified, not written.** I ran what they assert as probes.
- **The custody search** covered `plan_tree.json` files under `/Users/edr/night-custody` on this machine. I did not search archives elsewhere or any other machine. If a pack declaring the bare form exists somewhere I did not look, it is refused; that fails closed.
- **The cause of the three failures is shown by experiment, not by reading.** Changing the two lines alone turns them GREEN (E10), and planting a build entry admits the bare form (E3). I did not trace the readiness rows. The reason codes I saw were `readiness_row_registry_mismatch` (two tests) and three dependency codes (one test). The seat reports that the failures name the successor row; I did not confirm that wording.
- **Timing.** Two suites run side by side took 199 s and 267 s; one alone took 94 s to 242 s. I saw no failure that came and went.
- **An earlier run of mine, in a copy without git history,** showed three further failures in `test_committed_v1_freeze_receipts_remain_authentic_historical_records`. They came from the copy having no git history and vanished in the clone. They say nothing about the code.
- I did not read the design ruling, addendum A1, the cap council ruling, or the refuters' reports.

## Summary

1. Refusing the bare identifier `d079` is correct: it names no calibration file, so it has no build, and a name with no build is treated as held. It must not be given one. No pack in the repository or among 108 in custody declares it.
2. The lead changes the two fixture lines to `d079_calibration_acceptance_v2_n17_r7` and adds two tests that pin the refusal. I ran the two-line change: 69 tests pass, as on main, with no assertion touched. It is test-only, so it is not a fourth round.
3. `d079` stays in the admitted set for now, inert and documented as such. Its deletion is an ordinary change after the merge.
