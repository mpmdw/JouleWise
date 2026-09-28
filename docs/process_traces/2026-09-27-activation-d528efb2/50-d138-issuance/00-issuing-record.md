# Issuing record: decision D-185, the issue of calibration file `d079_calibration_acceptance_v2_n12_25g83_r1` for macOS build 25G83 (a D-138 transaction)

- **Owner of this record:** the lead (Opus 5.5 magistrate, activation d528efb2). Drafted on 2026-09-27 by a dictated-fills seat: the lead dictated the facts, and the seat checked each one against the source named beside it. Where the seat re-ran a check itself, the text says "re-run at drafting".
- **What this record must hold:** cold design ruling D138-25G83-DESIGN-01, §7.1 (`docs/process_traces/2026-09-27-activation-d528efb2/11-d138-design/21-coldgate-fable-ruling.md`, sha256 `858e2f4ead753e39f68831913be2a8e343f1443fb18863335f3147f1aa8c04a0`). That section asks for D1 to D8 in full; H1 to H7; bindings B1 to B4 with digests measured before the issue and after the merge; the owner's approval of the name; digest X; and the old-epoch replay of its §10 item 2. Each has its own section below.
- **Words about the process:** a **seat** is one delegated model session, and the **lead** is the session that runs this transaction. A **cold** ruling or pass is written by a judge in a fresh session with none of the working context. **Sol** and **Astra** are OpenAI models; **Fable** and **Opus** are Anthropic models. A seat that cannot finish inside its permitted files returns early with **NEEDS_SCOPE** (it asks for more files) or **NEEDS_RULING** (it asks for a decision). The **records branch** is `docs/2026-09-27-d528efb2`, where the activation's records are committed.
- **Branch and head at drafting:** `feat/2026-09-27-d138-25g83-issuance` at `e14e00bb5e8c0a7c422353ddb20b5275e49bff43`.
- **State at drafting:** the transaction is built and **not merged**. Two items are open. The after-merge measurements (§7.3) are placeholders until the merge. The old-epoch replay (§8) has not been ruled on; it is put to the cold final pass.

## 1. What is being issued, and the words used

The project measures the energy an Apple laptop (hardware model `Mac15,9`) spends running AI inference. It reads the laptop's power sampler (`powermetrics`), which reports power in frames of roughly 100 to 130 ms. To assign a frame's energy to the right piece of work, the project must know when each frame was taken. The error in that timing is measured, not assumed. A **calibration capture** is a recording of a little over three minutes during which the machine runs 59 commanded one-second GPU load pulses. The pulses' commanded start and end times are known, so the pulse edges found in the power frames show how far off the frame timing is.

Every term below is used only in the sense given here.

| Term | Meaning |
|---|---|
| **B** | The one number a capture contributes, in seconds: the largest timing uncertainty of any pulse edge, plus the uncertainty of placing the capture on the wall clock (the machine's time of day, which software may move). |
| **Calibration file** | Short for "calibration acceptance file": a JSON file that holds the B values of chosen captures and three numbers derived from them (S, C and the level screen, below). Later measurements are accepted or refused by comparison with those three numbers. |
| **Member** | A capture whose B enters the calibration file's statistics. The new file has n = 12 members. |
| **S** (bracket screen) | The spread of the members' B values (largest minus smallest), rounded to 1 µs. This is the largest change in B between the calibration capture taken just before a measurement and the one taken just after it that passes without comment. |
| **C** (maximum budgetable drift) | The largest such change that may be budgeted at all. Above C the measurement is refused. It is a 99 % prediction bound for the difference between two independent draws of B: t(0.995, n − 1) × (sample standard deviation) × √2. |
| **Level screen** | The largest member B. A calibration capture with a larger B than this stops a window before it starts. |
| **Bracket** | One workload measurement with a calibration capture before it and one after it. If the capture before it is invalid, the bracket is abandoned and the measurement is not used. |
| **Epoch** | The machine state a calibration file is valid for. It has six fields: operating-system build, hardware model, power policy, sampling interval, estimator revision and pulse protocol. The old epoch is macOS build **25F84**. The new epoch is build **25G83**. The other five fields are the same in both (`identity_epoch` of both files, re-read at drafting). |
| **Stale** | When a measurement is evaluated, its epoch is compared with the epoch the loaded calibration file covers. If any field differs, the calibration is "stale" for it and the evaluation refuses with `calibration_acceptance_bound_stale` (`joulewise/calibration_bracketing.py`, the freshness check). "Fresh" is the opposite. |
| **Generation** | One issued calibration file in the project's chain of them. Each file names its predecessor. **R7** is the generation in force before this one: `d079_calibration_acceptance_v2_n17_r7`, 17 members, epoch 25F84, file sha256 `9c3a29f61a6f72bbe5efdfb0eddd1caa14557595522b2abb093b414380b9fe16`. The file issued here is the first generation for 25G83. |
| **Loader** | `load_calibration_acceptance_bound` in `joulewise/calibration_bracketing.py`, the only way production code reads a calibration file. It accepts a file only if (a) the sha256 of the file's bytes equals a digest written in the code, and (b) the file's content passes the validator `_valid_acceptance_bound`. |
| **Pin** | A digest or identifier written into code or into another file, so that any change to the pinned thing is detected. |
| **Default** | The calibration file the loader reads when the caller names none (`DEFAULT_ACCEPTANCE_BOUND_PATH`). Before this transaction it was R7. |
| **Candidate** | A calibration file written by the preparation tool and marked "not issued". The loader refuses it. **Issuing** means turning the candidate into issued form, pinning the new file's digest in the loader, and making it the default. |
| **Seal** | A digest stored inside the calibration file over part of its own content. The **input seal** (`derivation_input_sha256`) covers only the inputs of the arithmetic: the identifier, the epoch, the ledger cutoff, the 12 member values, the statistics, the rounding, the quantile proof, the operative numbers and four fields of the registered row. Labels and prose fall outside it, so issuing must leave it unchanged. The **whole-file seal** (`derivation_sha256`) covers every key except itself, so it changes when labels or notes change. |
| **Digest X** | The sha256 of the issued file's bytes. It is the pin written into the loader. |
| **Ledger** | The append-only list of every calibration capture ever taken, valid or not, with a committed pin on its head (`configs/calibration/calibration_ledger_head.json`: sequence 276, head digest `476e2ae857d4d6279bfa3c59c39bb5bc6f983d282948ce0abb95e3df62d49737`). |
| **Prior set** | The calibration file's own copy of the ledger rows that existed when it was derived: 86 rows here (53 valid, 31 ordinary-invalid, 2 systematic-invalid). Both invalid kinds are captures that yield no B. A capture stopped by the cap or by a clock check is recorded `ordinary-invalid`. |
| **Registration** | The sealed document, written before the captures, that fixes which captures become members and which are excluded: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, Revision 5, sha256 `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`. It registers two capture windows, **W1** and **W2**, on 2026-09-27. Each took 12 captures, one every 600 s. A capture is named by window and slot, so "W1-d08" is slot 8 of W1. |
| **Disposed row** | A ledger row that a written decision has set aside as diagnostic, never a member. Eleven valid 25G83 rows of 2026-09-19 (sessions `…-n1-20260919` and `…-n2-20260919`) were set aside by decision `D-126-disposition-25G83-v3-2026-09-25`, because they were captured under a launch setting that stretched the sampler's frames. They are listed in `configs/calibration/observation_dispositions.json` ("the disposition file", sha256 `ba1ba3fc596c9ef7f4014131e5cbc2012559f72bab41cafb89e004056790a63c`). |
| **Window, claim-bearing, arming, pack** | A **window** is one scheduled measurement session. It is **claim-bearing** if its results may be reported as findings. **Arming** is the step that authorises a window to start. A **pack** is the frozen set of plans and pins that a claim-bearing window runs from. |
| **Hold** | A written condition that stops something from happening until a named ruling lifts it. H1 to H7 below are the holds and conditions on later windows. |
| **Estimator** and **the cap** | The **estimator** is the code that turns a capture's raw bytes into B. It lives in four files (§7). A **cell** is one unit of the estimator's search work. **The cap** is the limit of 165,000 cells per capture (`DETECTION_PROJECTION_CELL_BUDGET`). A capture that needs more is stopped and yields no B. |

**The three numbers, worked from the file.** The 12 member B values run from 0.024377093921897318 s (W1-d10) to 0.03807857930294817 s (W2-d10). The spread is 0.013701485381050852 s, which rounds to **S = 0.013701 s**. The sample standard deviation is 0.004330477884879059 s. With n − 1 = 11 degrees of freedom, t(0.995, 11) = 3.10580651553928100710, and 3.10580651553928100710 × 0.004330477884879059 × √2, evaluated in binary64 floating point as the file's rule states, gives **C = 0.01902064410651988 s**. The rule in force for this registration (the D-125 addendum of 2026-09-25) takes C as the largest of R7's C (0.010164834757777545 s), this bound, and S. The bound is the largest. The largest member B, rounded to 1e-15 s, is **level screen = 0.038078579302948 s**. All values are copied from `decimal_derivation` in the issued file.

**What S and C do to a measurement.** This illustration uses the file's own rules: `allowance_rule` = max(observed drift, S), and `operative_bound_rule` = max(pre B, post B) + allowance. Suppose the capture before a measurement gives B = 0.030 s and the capture after it gives 0.036 s. The change (the drift) is 0.006 s, below S, so the allowance is S and the measurement's timing bound is 0.036 + 0.013701 = 0.049701 s. With a drift of 0.016 s (between S and C), the allowance is 0.016 s. With a drift of 0.020 s (above C), the measurement is refused.

## 2. Identity of the issued file

| Field | Value | Checked by |
|---|---|---|
| Identifier | `d079_calibration_acceptance_v2_n12_25g83_r1` | read from the file at drafting |
| Path | `configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json` | present at `e14e00bb` |
| **Digest X** (sha256 of the file's bytes) | `80c2303611268b6b94626e001fb5df0e783719744145c9f6a31d4061ddee351b` | `shasum -a 256`, re-run at drafting; equals `EPOCH_25G83_R1_ACCEPTANCE_BOUND_SHA256` in `joulewise/calibration_bracketing.py` |
| Input seal (`derivation_input_sha256`) | `e7363bdd83af94cad15f0554043d35b646168e005125d3d770e7ba91dc9fb011`, **unchanged from the candidate** | read from both files at drafting |
| Whole-file seal (`derivation_sha256`) | `8477d8ce3cde8d3e6c90f2f10a15024db060235dfba3342b64c5c64c3f3ecc2c` (the candidate's was `fac6e6f89e764dc4b00516d9a35f5d1c1eaca9821e76725f5f1fb66b5b206073`) | read from both files at drafting |
| Source candidate | `docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json`, sha256 `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2` | re-hashed at drafting, in the worktree and on `origin/main` |
| Role and issuance block | `artifact_role: "issued"`; `issuance: {status: "issued", claim_eligible: true, reason: …}` | read at drafting |
| Epoch | `os_build 25G83`, `Mac15,9`, `ac_high_power`, 100 ms, `joint_loss_sublevel_interval_branch_v2`, `powermetrics_pulse_fiducial_v3` | read at drafting |
| n | 12 (`derivation_corpus.n`; members from sessions `d079-epoch-25g83-derivation-w1-20260927` and `…-w2-20260927`) | read at drafting |
| S | `0.013701` s | `decimal_derivation.ratified_operatives.bracket_screen_s` |
| C | `0.01902064410651988` s | `…maximum_budgetable_drift_s` |
| Level screen | `0.038078579302948` s | `…preflight_level_screen_s` |
| Ledger cutoff | sequence 276, `476e2ae8…` | equals the committed head pin |
| Predecessor | `d079_calibration_acceptance_v2_n17_r7` | `registered_generation_row.predecessor_acceptance_id` |
| Notes added at issue | `derivation_notes.network_time_provenance` and `derivation_notes.issuance_record`, each equal to the issuance text | compared at drafting: both equal `docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance/10-issuance-text.json` (sha256 `3c1fa2126b750ec49207ad39afac712b42d516773513a216901ed288d92a4516`) |

The science rulings the file cites, by the sha256 of the copies on `origin/main` (re-hashed at drafting): SCI-25G83-CANDIDATE-01 `f9de51b7bf78307ca9239e6750bb13f30f67004483070544fee57c395331f4a4`; addendum A1 `be13ccbae89d67fd7de55231cfbba9ac1d3ff289700fae77910389690fab9d3d`; addendum A2 `b35d072bb58f25eda711b6a0db1bbfc480781dd139cb144faa877d906391ba9c`; addendum A3 `365caf0a8f6362fdc6a891a555ecf5d0dcc5fdd72a35b7ddc97389a6e1a8a3e1`.

## 3. The owner's approval of the name

Recorded as item 17 of the activation record `docs/process_traces/2026-09-27-activation-d528efb2/00-activation-record.md` (on branch `origin/docs/2026-09-27-d528efb2`): Gmail message `1a0e584941690672`, thread `1a0e57e8d473f8eb`, 17:57 PDT on 2026-09-27. The owner's reply, verbatim: "Yes re name , go ahead". It answers the request of activation item 9, which recommended the identifier `d079_calibration_acceptance_v2_n12_25g83_r1`. The record reads "go ahead" as the request's option "yes": publish once every gate has passed.

## 4. What the transaction changes, and why

### 4.1 The loader repair: skip exactly the eleven disposed rows

**Forcing problem.** A calibration derived from live captures must account for every valid capture of its own registered sessions: each must be a member or a named exclusion. Otherwise members could be chosen after their values were seen. The validator enforces this. It also refuses any valid new-epoch row from a session outside the registration. The eleven disposed rows of 2026-09-19 are exactly such rows. The preparation tool knew the disposing decision and kept the rows in the prior set, which is honest because they happened. The validator did not know the decision, so it refused the issued form (ruling §2 V1 to V3).

**Worked example.** The prior set has 86 rows, 53 of them valid. The valid rows are 30 rows of earlier epochs, the 12 valid rows of W1 and W2, which are exactly the 12 members, and the 11 disposed rows. W1 and W2's other 12 rows are recorded `ordinary-invalid`. The file names no exclusion among valid rows (`derivation_notes.excluded_members` is empty). Design ruling §4.1 says one valid row is a named exclusion. The counts here are read from the issued file at drafting. Before the repair, the validator's loop reached the first disposed row, saw session `d079-epoch-25g83-derivation-n1-20260919` (not W1 or W2) and refused. After the repair it skips that row because the row's content identifier is in the decision's list. It then requires, as before, that members plus named exclusions equal the valid rows of W1 and W2: here 12 = 12 + 0.

**Mechanism.** A new module, `joulewise/calibration_dispositions.py`, holds the decision as a reviewed table written in code: decision id → the exact mechanism sentence and the frozen set of eleven content identifiers. It also holds the disposition file's sha256 pin. The loader does **not** read the disposition file when it loads. The table is tied to the file by an equality check (`parse_disposition_registry`), which the preparation tool runs every time it reads the file and `tests/test_calibration_dispositions.py::DispositionTests::test_d1_registry_and_table_agree` runs on every suite run. The issued file declares the decision in `prior_observation_set.disposing_decision_ids = ["D-126-disposition-25G83-v3-2026-09-25"]`. The validator refuses, in order, if: the declaration is malformed; the declaration is not exactly the set of decisions that dispose rows present in the prior set; a disposed row is missing from the prior set; a disposed row belongs to a registered session or is a member; or a disposed row is also a named exclusion. The seven older generations use a different prior-set mode and never reach this code (design ruling §4.4 test L9, `test_l9_old_files_load_without_registry_io`, asserts that the disposition file is not opened for them).

### 4.2 The issued bytes: a re-runnable tool, not a hand edit

`scripts/promote_calibration_candidate.py` is a pure function of two files: the candidate (refused unless its sha256 is `dbad7cc7…b5b2`) and the lead-written issuance text. It deletes `candidate_not_issued`, sets `artifact_role` to `issued`, replaces the `issuance` block, marks `backfill_candidate` issued, appends the two note blocks, recomputes both seals with the production functions, and refuses unless the input seal comes out `e7363bdd…`. `--check <path>` exits non-zero unless the file at that path equals the bytes the tool would write. The candidate was **not** re-prepared: binding B3 forbids curing anything by re-preparation, and the science rulings judged the bytes `dbad7cc7`.

### 4.3 The default moves; R7 stays

`ACTIVE_ACCEPTANCE_ID` and `DEFAULT_ACCEPTANCE_BOUND_PATH` now name the new file. R7's file, its registry entry and its pin are unchanged. The loader picks the pin by the file's own identifier, so R7 still loads when named by path and still covers epoch 25F84. This was re-run at drafting: the default loads as `d079_calibration_acceptance_v2_n12_25g83_r1`, and R7 loads by path. Three tools that mean "R7" but used to read "the default" now name R7 explicitly (ruling §6.3): the preparation tool's predecessor check and its `--predecessor-acceptance` default, `scripts/epoch_equivalence_check.py --acceptance`, and `scripts/sim_acc_25g83_rev5.py`. The pinset schema `scripts/floor_mint_pinsets/schema_v2.json` gains a list for the new identifier that forces its screen value to `0.013701`. Before this change, an identifier in no list had an unchecked screen value.

### 4.4 Hold H1 is enforced in code

**Forcing problem.** Until this merge, no claim-bearing window could run at 25G83, because no calibration file covered that epoch. The merge removes that obstacle. Windows are armed by an unattended loop, so a hold that existed only as a sentence would be weakest at the moment of merge.

**Mechanism.** `joulewise/arm_readiness.py` lists the issued calibration identifiers that a pack may name (`_ISSUED_D079_IDS`). The new identifier is in that list, and it is also in `_CLAIM_HELD_ACCEPTANCE_IDS = {"d079_calibration_acceptance_v2_n12_25g83_r1": "H1-25G83-CAP-CADENCE (SCI-25G83-CANDIDATE-01-A1 §5.3)"}`. `_issued_d079` admits an identifier only if it is in the first list and not in the second. A pack naming the new file is therefore treated as a "successor" pack. Such a pack cannot arm without a readiness-evidence row, and the code that writes that row always refuses (`_derive_acceptance_successor` in `joulewise/arm_readiness_evidence.py`; design ruling V11). Re-run at drafting: `_issued_d079` returns `False` for a pack policy naming the new identifier and `True` for one naming R7. **Release:** a reviewed change that deletes the entry and cites the written ruling that closes the cap question by route R or route M (H2, H3). There is no flag and no environment variable. **Known cost:** the hold also stops any pack that names the new file for a rehearsal carrying no claim. Windows that run without a pack are not affected.

### 4.5 What `claim_eligible: true` means

Design ruling §7.4, quoted:

> `claim_eligible: true` in the file means: *these bytes are an authentic issued calibration, and its numbers may serve as the timing-uncertainty basis of a reported result.* It is a property of the file. It is not permission to start a window. Permission to start a claim-bearing window is separate; H1 withholds it, and H5 to H7 condition it.

The file carries the same text as `derivation_notes.issuance_record.claim_eligible_meaning`, and `hold_enforcement` reads: "H1 is enforced outside these bytes, at the arm admission list; lifting it changes no byte of this file".

## 5. Disclosures D1 to D8

**How to read them.** The texts are copied verbatim from `issuance_record.disclosures` in `10-issuance-text.json`, which the issued file carries byte for byte. D1 and D3 are in the wording that addenda A2 and A3 give (A2 replaced D1's second sentence; A3 §4.3 gave D3's added sentences). D8 is the text of addendum A3 §4.1, which replaced A2's D8 in full. Section signs (§) inside D3 and D4 cite the first science ruling, `21-science-gate-ruling.md`. Terms they use and that are not built above: **r** is a correlation coefficient between two quantities measured across captures (+1 is perfect agreement, 0 is none); **p** is the probability, under a permutation test, of a correlation at least that large arising by chance; **cadence** is the length of the frames the sampler actually delivers (it is asked for 100 ms and in this epoch delivers 127.6 to 130.2 ms); **network time** and the corrections the time daemon `timed` applies to the wall clock are defined at the start of D8; **the issuing tool** in D5 is the preparation tool; **predecessor-screen count** in D6 is the number of members whose B exceeds R7's level screen (0.032898493715362 s), namely W1-d04 and W2-d10 (`derivation_notes.prior_screen_comparison`); **display state** is whether the screen was on; **battery gauge steps** are jumps in the battery's reported charge while no current flowed; the **registered class** in D3 is `affine_clock_fit_empty` (no straight-line clock fit exists), the only exclusion reason the registration names at that step (addendum A3 §2 E16). D8 also uses these terms: the **monotonic clock** is a counter of elapsed time that nothing moves; a **paired clock reading** is one reading of the wall clock and one of the monotonic clock, taken together; the **clock fit** is the straight line relating the two clocks over a capture.

### D1

> D1. Yield and causes. 12 of 24 captures are members. The 12 others: 8 stopped by the 165,000-cell work cap, and 4 lost to network-time corrections of the wall clock, of which 3 are recorded as a wall-clock movement above 5 ms during capture and 1 as an infeasible clock fit.

### D2

> D2. The cap is mis-sized for this epoch. It was sized at ≈120 ms frames; this epoch runs at 128–130 ms and needs 144,037–170,965 cells. The cap excluded on cadence (r = +0.82), not on B (r = −0.05; p = 0.44). The corpus under-represents the longer-cadence group, 25 % against 45 %. A1.1 Classification of F1 (adds to §2.2, §5 and D2). F1 is not a defect in the code that derives the member list, the statistics, or S, C and the level screen, within the meaning of statement item 7(b), and it is not a ground to reject this candidate. The 165,000-cell cap is a stop rule that was registered on 2026-08-15, frozen at its value on 2026-08-18 and pinned by file digest in the registration sealed on 2026-09-25; on 2026-09-27 it behaved exactly as registered; and it enters no number, because a capture that finishes gives the same B to the last digit whether the cap is 165,000, 206,000 or 5,000,000 cells. A gate that nevertheless rejects the candidate on F1 is invoking item 7(b), and item 4's consequences (a) to (d) follow. F1 is never a ground to re-prepare the candidate with a different cap or a different member list. In §5, "sign of an artifact" is read as: a registered parameter whose sizing assumption, frames of about 120 ms, no longer holds. The owner may overrule this classification in writing under statement item 10.

### D3

> D3. Three exclusions carry an alignment reason other than the registered class. `wall_minus_monotonic_span_exceeded`, spans 52.0, 5.8 and 35.9 ms. They were excluded by the writer as `ordinary-invalid`, under the structural reading ruled in §2.4. The cause of the three movements is known: corrections applied by the time daemon with network time ON (D8). W1-d01, recorded under the registered class, has the same cause. The mechanism was on record in this project from 2026-09-22; it was not newly discovered on 2026-09-27.

### D4

> D4. Eight diagnostic B values exist for excluded captures (§2.3 table), computed by this gate with the cap lifted. Never members; disclosed design inputs for any successor. A1.4 correction: (d) D4: the eight diagnostic B values were computed independently by the judge and by the paired refuter and agree to every printed digit; the addendum judge recomputed one (w2-d02). A successor registration's list of disclosed design inputs names all three seats.

### D5

> D5. Tool repair. The issuing tool was repaired after capture and before any B was read (statement item 6(d) R9).

### D6

> D6. Known conditions. Display state unconstrained and unrecorded; battery gauge steps in both windows with no current flow; n = 12; predecessor-screen count 2.

### D7

> D7. the cap stops a capture according to how much work the estimator needs, and that work rises with the length of the sampler's frames (r = +0.82, about 7,500 cells per millisecond). In a measurement window a stopped calibration capture abandons its bracket, so the measurements that survive are mostly those taken while the machine delivered shorter frames. Whether the workload's energy differs between those machine states has not been measured, and W1 and W2 cannot measure it. This bears on whether a reported energy is true.

### D8

> D8. Network time was ON during both capture windows. "Network time" is the macOS setting "set time automatically". While it is ON, the time daemon `timed` corrects the machine's wall clock from time servers, either at once (a step) or gradually over about two minutes (a slew), and resets the rate at which the clock runs (the standing rate). It was ON throughout W1 and W2 on 2026-09-27. Between 00:00–03:00 and 08:30–11:30 PDT the system log records 42 applied corrections: 8 of millisecond size (1.3 to 53.2 ms; one step and seven slews, 27 to 46 minutes apart) and 34 of microsecond size (under 0.1 ms; eleven groups of three, each following a time reading from Apple's push-notification service, and one that accompanied the step). The eight set the standing rate to values between −7.50 and +7.50 parts per million; from 08:13:39 to 09:00:03 it was −8.68. Captures lost. Four of the 12 excluded captures were lost to these corrections: W1-d08 (+53.2 ms step during the capture), W1-d11 (+4.39 ms slew during the capture), W2-d07 (−35.9 ms slew during the capture), and W1-d01 (a −1.26 ms slew applied 16 s before the capture; 0.47 ms of it arrived during the capture, so that the five paired clock readings the clock fit uses cannot lie on one straight line: the two taken 1.0 and 1.9 s into the capture sit 28 and 48 µs off the line through the other three, and no clock fit exists). Members. Ten of the 12 members had no correction during the capture, and their wall clock followed a straight line against the monotonic clock to within 4 µs. Two were touched: W1-d12 (three slews of +23.5, +34.0 and +39.8 µs applied 28 s into the capture; the clock moved +40.1 µs) and W2-d01 (the tail, −11.6 µs, of a −45.3 µs slew applied 22 s before the capture). Both movements lie inside the 250 µs allowance that the clock method adds in full to every capture, and inside each capture's charged drift term (the clock movement between a capture's first and last readings, which is part of B). Effect on the operative numbers, two sizes. (a) The two movements: S and the level screen are unaffected; C is 8.9 µs (0.05 %) smaller than with the movements removed. (b) The changing standing rate: because `timed` reset the rate between captures, the members' drift terms differ, from 0.74 to 1.54 ms. Had all 12 carried one and the same drift term, of any size, S would be 505 µs (3.7 %) and C 554 µs (2.9 %) larger. The issued S and C are therefore the stricter values. With network time OFF the rate stays fixed through a window: the two nights in custody taken with it OFF (2026-09-22 and 2026-09-23, 24 idle captures of 600 s) ran at about 3.6 and 2.9 parts per million, each constant to 0.003, with no correction applied. The rate differs from one such window to the next, so 505 and 554 µs are the upper end of the effect. What was required. No registered rule required network time OFF for these captures: the registration, the runbook and the capture chain do not mention network time. The clock method's straight-line model nevertheless assumes OFF. Its text requires an authenticated OFF state of claim-bearing captures, calls a capture with network time ON or unknown "validation-only material", and does not exempt calibration captures. The one precedent, the previous calibration, excused historical captures of unknown state; these were new captures. The mechanism had been diagnosed in this project on 2026-09-22 (ruling A267), and the control installed then covered the chain that takes idle measurements and not the chain that takes calibration captures. The words "unknown cause" in the first science ruling were a miss. What the members rest on. Their fitness rests on measurement after the fact (129 paired clock readings per capture, and the log of every correction), not on the OFF control. What is not measured. This calibration was derived with network time ON and will be applied to captures taken with it OFF. That the two states give the same population of B is inferred, and is measured by H7. Evidence: `docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/21-ruling.md` and `31-addendum-ruling.md`; the log itself, which the system deletes after about 29 hours, is preserved in `evidence/` beside them (full pull, sha256 of the plain text `2f9bf739fde57accdce86e27a9494303585c976132e5dc5063a2cd31a5880b5c`).

## 6. Holds H1 to H7

**How to read them.** H1 comes from addendum A1 §7 (A1.3). H5, H6 and H7 are the final texts of addendum A3 §4.4 to §4.6. All four are copied verbatim from `issuance_record.holds` in the issuance text, which the file carries. The file does not carry H2 to H4. They are copied verbatim from addendum A1 §7 (A1.3), and H4 is followed by its rewording in addendum A3 §4.4. **Route R** and **route M**, which H1 names, are defined by H2 and H3. **B4**, which H2 names, is in §7.1: a change to the cap is a separate, later transaction, and it forces a re-issue. **Custody**, in H5, is the directory where a window's raw evidence is kept. H1 is enforced in code (§4.4). H5 and H6 are conditions on every future 25G83 window, and their enforcement in the capture chain must land before the next window of any kind at 25G83 (design ruling §7.4, §10 item 7). None of H1 to H7 is a condition on this issue.

### H1 (addendum A1 §7, A1.3; carried by the file)

> H1. No claim-bearing window is armed at 25G83 until a written ruling closes this question by route R or route M. The hold is written into the issuing transaction's record and into the arm material of every 25G83 window. Windows that carry no claim may run.

### H2 (addendum A1 §7, A1.3)

> H2. Route R: the cap is re-sized in a later transaction under B4, by a rule written before the new value is computed, which states the range of frame lengths it covers and uses cell counts and frame lengths only; and in at least 24 captures taken under the new cap in windows that carry no claim, none stops on the cap.

### H3 (addendum A1 §7, A1.3)

> H3. Route M: the cap stays, and a plan registered before the window fixes that (i) every bracket attempted is recorded, abandoned ones included, with the reason, the median frame length of its calibration captures and the cells used; (ii) the workload's energy is computed for abandoned brackets too, as a diagnostic; (iii) the report states how many brackets were attempted, completed and abandoned on the cap, and the difference in energy and in frame length between completed and abandoned brackets, with its uncertainty; (iv) if that difference is larger than the uncertainty the claim carries, the claim is reported as holding for the short-frame state only.

### H4 (addendum A1 §7, A1.3), as reworded by addendum A3 §4.4

> H4. The three captures lost to a wall-clock step are the same kind of filter. Under either route abandoned brackets are recorded by cause, and the cause of the steps is sought before claim-bearing windows run.

Addendum A3 §4.4, verbatim:

> **H4 of addendum A1 (its last clause is discharged).** "The cause of the steps is sought before claim-bearing windows run": the cause is network-time corrections (D8). The rest of H4 stands, and H5, H6 and H7 now govern.

### H5 (addendum A3 §4.4; carried by the file)

> H5. Network time OFF for every window. "Network time" is the macOS setting "set time automatically"; while it is ON the time daemon `timed` moves the wall clock. For every window at 25G83, claim-bearing or not, network time is set OFF at least 600 s before the first capture's first clock reading, with `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off`. The window starts only if that command exits 0 and prints exactly `setUsingNetworkTime: Off`. The command's arguments, exit status, exact output and the time on both clocks are saved in the window's custody. After the last capture's last clock reading network time is set back ON, and that receipt is saved too. The read form of the command (`-getusingnetworktime`) is not evidence: without administrator rights it prints a refusal and still exits 0. Reasons: the clock method's straight-line model assumes OFF; with it ON, 4 of the 24 captures of W1 and W2 were lost to clock corrections; calibration captures should be taken in the state of the captures they will screen; and captures of unrecorded state cannot later be told apart. Setting the state from the arming session, outside the capture chain, satisfies H5 and changes no pinned file. For a window that takes calibration captures, H5 and H6 are written into the registration the window runs under before it is armed.

### H6 (addendum A3 §4.5; carried by the file)

> H6. Every capture is attested from the `timed` log, by a query that cannot pass on a deleted log.
>
> *Why.* The system deletes log lines oldest first, after about 29 hours on this machine. A query over a deleted period exits 0 and prints the column header and nothing else, which is exactly what a period without corrections prints. An empty answer therefore proves nothing by itself.
>
> *The window query.* Once per window, as soon as the last capture has ended, run `/usr/bin/log show --info --debug --style syslog --predicate 'process == "timed"' --start S --end E`, where S is 3,600 s before the first capture's first paired clock reading and E is 1 s after the last capture's last paired clock reading. Save the arguments, the exit status, the full output, its sha256 and the time the query ran on both clocks.
>
> *The coverage witness.* The output must contain at least one line written by `timed` in the log category `[com.apple.timed:data]` whose timestamp is earlier than 180 s before the first capture's first paired clock reading. Because deletion is oldest first, a log that still holds that line still holds everything `timed` wrote after it, and that includes every capture of the window and the 180 s before each. The witness line's timestamp is saved.
>
> *Markers.* A marker is a line containing `cmd,apply,src,`, `ntp_adjtime` or `settimeofday`. `timed` writes one whenever it moves the clock.
>
> *Verdict for each capture.* The capture is attested clean only if all four hold: (1) the query exited 0; (2) the first line of the output is the syslog column header; (3) the coverage witness is present; (4) no marker lies between 180 s before the capture's first paired clock reading and 1 s after its last, each end taken from both clocks and the wider reading used. If (4) fails, the capture is recorded `network_time_slew_attested`. If (1), (2) or (3) fails, or no query was run, every capture of the window is recorded `network_time_unattested`. A capture with either record is not a calibration member, not a bracket capture and not claim-bearing.
>
> *Sizes.* The 180 s lead exists because a slew keeps moving the clock after its log line, fading by a factor e every 16.5 s: the largest correction on record, 53.2 ms, needs 180 s to fall below 1 µs. One marker of any size excludes because with network time OFF (H5) none is expected: the two OFF nights in custody show none in 24 captures, where the ON state would have produced about 13. A marker therefore means the OFF control failed.
>
> *Scope.* Where a chain also runs its own query right after each capture (the chain that takes idle measurements does, over the capture ±1 s), that query stays exactly as approved, and a capture is clean only if both queries find it clean. The window query may be repeated later, for instance after a crash; a run is valid if it meets the four conditions and no run is valid without the witness. H6 was not applied to W1 and W2, which their sealed registration governs; with network time ON it would have set aside 4 of the 12 members.

### H7 (addendum A3 §4.6; carried by the file)

> H7. First comparison of the two states, and no pooling before a registered rule. For the first window at 25G83 taken with network time OFF, three things are recorded for every capture: its network-time state, with the H5 receipt and the H6 verdict; the standing rate (how fast the wall clock gains or loses against the monotonic clock, in parts per million); and the drift term. The captures' drift term and B are compared with those of the 12 members of this calibration, the number of captures set aside by H6 is stated, and the comparison is reported with the first claim-bearing results. This measures what D8 says is inferred. What the record leads one to expect: with OFF the standing rate is frozen, so every capture of a window carries the same drift term (about 0.6 and 0.7 ms per capture at the rates of the two OFF nights in custody; an earlier record gives 1.4 to 1.5 ms), where the 12 members' drift terms range from 0.74 to 1.54 ms. Every later calibration records each member's network-time state. Members captured with network time ON are combined with members captured with it OFF only under a rule written into a registration that is sealed before the OFF-state captures are taken. Without such a rule they are not combined.

## 7. Bindings B1 to B4 and their measurements

### 7.1 The bindings, verbatim from addendum A1 §7 (A1.2)

> B1. The tree from which the calibration is issued holds the four estimator files at exactly these sha256 digests: `joulewise/powermetrics_fiducial.py` `386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92`; `joulewise/uncertainty_evidence.py` `b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8`; `joulewise/adapters/powermetrics.py` `70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4`; `joulewise/reduce.py` `7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc`. The four digests are computed and recorded immediately before the issue and again on the merged result. The issued file's `estimator_code_sha256` block equals the candidate's character for character.

> B2. The transaction contains no change to any of the four files. It does not change `DETECTION_PROJECTION_CELL_BUDGET`. It merges none of `feat/2026-09-04-instrument-path-pin` (`bda7ffe0`), `feat/2026-09-04-raw-capture-digest` (`aeea07b6`), `feat/2026-09-24-acc-25g83-v4-rev4` (`ea10e3c8`), `impl/p2041` (`5135c1d2`), and no other branch whose difference from main touches one of the four files.

> B3. If B1 or B2 cannot be met, the transaction does not issue and the matter is held for a ruling. It is not cured by re-preparing the candidate under different code.

> B4. A change to the cap, or any other change to the four files, is a separate and later transaction under D-138. It makes the calibration issued here stale and forces a re-issue. Before such a change is staged, the council rules in writing on which captures the re-issue may contain and on the rule by which the new cap value is chosen. That rule uses cell counts and frame lengths only, and no B value. D-138's inheritance corollary applies to that later transaction, not to this one.

### 7.2 Measured before the issue, on head `e14e00bb`

Re-run at drafting in the issuing worktree, at `e14e00bb5e8c0a7c422353ddb20b5275e49bff43`.

| Item | Measured | Required (B1/B2) | Equal |
|---|---|---|---|
| `joulewise/powermetrics_fiducial.py` | `386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92` | same | yes |
| `joulewise/uncertainty_evidence.py` | `b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8` | same | yes |
| `joulewise/adapters/powermetrics.py` | `70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4` | same | yes |
| `joulewise/reduce.py` | `7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc` | same | yes |
| `DETECTION_PROJECTION_CELL_BUDGET` | `165_000` (`joulewise/powermetrics_fiducial.py:88`) | unchanged | yes |
| Issued file's `prospective_rederivation.estimator_code_sha256` block | equal to the candidate's block (parsed comparison) | equal character for character | yes (the file-level check is test P2) |
| B2: `bda7ffe0`, `aeea07b6`, `ea10e3c8`, `5135c1d2` ancestors of the head? | none is (`git merge-base --is-ancestor`) | none | yes |
| B2: files named by `git diff origin/main...HEAD` | 26 paths under `joulewise`, `scripts`, `configs` and `tests`; none of the four estimator files | none of the four | yes |

### 7.3 Measured after the merge: to be filled after merge (ruling §9 step 11)

| Item | Required | Measured on main after merge |
|---|---|---|
| `joulewise/powermetrics_fiducial.py` sha256 | `386e8254…ab92` | *to be filled after merge (ruling §9 step 11)* |
| `joulewise/uncertainty_evidence.py` sha256 | `b583f35a…4ae8` | *to be filled after merge (ruling §9 step 11)* |
| `joulewise/adapters/powermetrics.py` sha256 | `70f47086…e5e4` | *to be filled after merge (ruling §9 step 11)* |
| `joulewise/reduce.py` sha256 | `7b9c0d28…9fcc` | *to be filled after merge (ruling §9 step 11)* |
| `DETECTION_PROJECTION_CELL_BUDGET` | `165_000` | *to be filled after merge (ruling §9 step 11)* |
| Loader reads the default and returns | `d079_calibration_acceptance_v2_n12_25g83_r1` | *to be filled after merge (ruling §9 step 11)* |
| sha256 of the issued file equals the pin | `80c23036…351b` | *to be filled after merge (ruling §9 step 11)* |
| R7 loads by path | loads, `d079_calibration_acceptance_v2_n17_r7` | *to be filled after merge (ruling §9 step 11)* |
| `_issued_d079` on the new identifier | `False` (held) | *to be filled after merge (ruling §9 step 11)* |
| Merge commit on main | — | *to be filled after merge (ruling §9 step 11)* |

## 8. The old-epoch replay (design ruling §10 item 2): not yet disposed

**Why the check exists.** Once the default moves, any recorded 25F84 measurement that is evaluated through the default is compared with a file that covers 25G83 only, and comes back stale. R7's own move never showed this, because R7 kept its predecessor's epoch. The ruling therefore requires one recorded 25F84 analysis to be run at main and at the change's head, with the outputs compared. The ruling, quoted:

> 2. **Old-epoch measurements under the new default: mandatory check before merge.** Opus raised it; I confirm the mechanism from code (V13, V14): after the move, a recorded 25F84 measurement evaluated through the default is compared with a file that judges 25G83 only, and comes back "stale". R7's move never showed this, because R7 kept its predecessor's epoch. The lead runs one recorded 25F84 analysis at main and at the change's head and compares outputs.
>    - Identical: proceed.
>    - A clean refusal naming the stale calibration: proceed. A refusal cannot make a reported number wrong. It does mean old-epoch results can be re-evaluated only from a commit before the move, until a lane gives them a route that names R7. The issuing record says so, and the lane is opened.
>    - **Any number that differs, or any refusal for another reason: stop.**

**Attempt 1 (Sol scout, high effort; activation items 46 and 49).** The seat chose recorded member `sw7bfloor-df-ph-decode-abs-r01` of the passed claim-bearing 25F84 decode-floor window of 2026-07-29 (Qwen2.5 7B). It replayed the production bracket evaluator with the 276-row ledger of the W2 measurement checkout, whose head equals the committed pin. At main `e7c8bcc6`, R7 authenticated as fresh, but the evaluation exited 1 with `instrument_calibration_bracket_missing` and produced no number. At the change's head, the same replay exited 1 with `calibration_acceptance_bound_stale`. With the older 76-row ledger instead (the one in the canonical checkout), main refused with `calibration_ledger_rollback`, and the head refused with `calibration_ledger_baseline_missing` and `calibration_ledger_rollback`, because that ledger is older than the committed 276-row head pin. The seat marked the main-side refusal as blocking ("do not start" for the merge), because that refusal is not a stale-calibration refusal. The lead recorded a different reading (activation item 49): the rule compares main with the head, and a refusal already present on main is no evidence against this change. On that reading the attempt is still not a qualifying comparison, because main does not reproduce the recorded numbers. Attempt 2 was launched to find a step that does.

**Attempt 2 (Sol xhigh).** This seat traced the July production sequence. It was the whole-window verdict followed by `scripts/extract_detection_floors.py` at commit `969a4d6`, and the custodied report records 6.294380135190098 J (absolute floor) and 13.998036715259254 J (comparative floor). R7 did not exist at that commit, so the original analysis never consulted R7. The seat re-ran the bracket replay. Main: R7 fresh, `instrument_calibration_bracket_missing`, no number. Head `e14e00bb`: the new file, stale on `os_build` only, `calibration_acceptance_bound_stale`, no number. **Why main produces no number:** the July calibration captures taken just before and just after the measurement are ledger rows 58 and 60. Both are historical imports (`historical-import-v1-finalization`), and current candidate discovery excludes historical imports (`joulewise/calibration_bracketing.py`, the `observation.is_historical_import` test in candidate discovery; the line was read at drafting). Every later bracket-session row in the 276-row ledger is 25G83, and the archived 76-row ledger is refused as a rollback. So on current main, no recorded 25F84 analysis step passes from recorded inputs. The seat returned the category STOP for this comparison, and said plainly that this is **not** evidence of a changed July number. It also found that an explicit-R7 route exists in later tooling (`epoch_equivalence_check.py --acceptance` defaults to R7 at the head, and the generalized floor mint reads an acceptance path from its input manifest), and that no recorded July production step used an explicit R7 path.

**Against the ruling's three outcomes.** At the head, the replay refuses cleanly with `calibration_acceptance_bound_stale`, which names the stale calibration: that is the ruling's second outcome. No number was produced on either side, so no number differs. The main side has no numeric baseline, and its refusal (`instrument_calibration_bracket_missing`) is for another reason. That refusal exists before the change and is not caused by it. Both seats read that as the letter of the third outcome ("any refusal for another reason: stop"). The lead's reading, recorded above, is that a refusal already present on main is no evidence against this change. Treating the replay as satisfying §10 item 2 would reinterpret a ruled stop condition, and the lead may not do that alone (activation item 50). **Whether this satisfies §10 item 2 is therefore put to the cold final pass** (design ruling §9 step 9). The transaction does not merge before that ruling.

**Consequence, stated as the ruling requires.** After the merge, recorded 25F84 results cannot be re-evaluated through the default. The route named in the ruling, re-evaluation from a commit before the move, gives no number either for the July window tested here, for the reason above. Until a lane gives old-epoch results a route that names R7 explicitly, such re-evaluation is unavailable. That lane is to be opened by the lead.

**Evidence.** Scratch directories `/tmp/oldepoch-d528efb2/` (attempt 1) and `/tmp/oldepoch2-d528efb2/` (attempt 2), copied to the record on branch `docs/2026-09-27-d528efb2` under `docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance-seat/oldepoch-1/` (runner `replay.sh`, `bracket_replay.py`, `compare.py`, the `main/`, `head/`, `l76-main/` and `l76-head/` outputs, and `report.md`) and `…/oldepoch-2/` (`brief.txt`, `main-bracket/`, `head-bracket/`, `report.md`).

## 9. Amendments to the implementation scope (design ruling §8.1)

The ruling fixed the implementation seat's write scope as an exhaustive list. It allowed the lead to amend the list in writing with test files only, and only to re-point expectations about R7. The lead made two such amendments.

1. **Nine test files from a census run.** Before launch, the lead moved the default in memory and ran the suite (ruling §8.2 step 3). The census recorded failing modules and was incomplete: some of the parallel parts of the run did not finish (`50-d138-issuance-seat/00-census-module-fails.txt` and the brief `01-impl-brief.txt` on the records branch). Nine failing modules not in §8.1 were added: `tests/test_arm_readiness_dry_run.py`, `tests/test_axi_controller_events.py`, `tests/test_axi_mock_spec.py`, `tests/test_bracket_binding_cli.py`, `tests/test_calibration_ledger_custody.py`, `tests/test_calibration_live_three_window.py`, `tests/test_collector_analysis_manifest_id.py`, `tests/test_issuer_corpus_root.py`, `tests/test_launch_window.py`. The brief's condition was that each file may be edited only to re-point an expectation that assumed R7 is the default, or that builds a pack or arms on the default (now held by H1), so that it names R7 or expects the new generation, and that no assertion is weakened. Two of the nine were edited on the branch: `tests/test_calibration_live_three_window.py` and `tests/test_issuer_corpus_root.py` (`git diff --stat origin/main...HEAD`).
2. **`tests/test_validate_powermetrics_fiducial_derivation_only.py`**, added after the seat's first round returned NEEDS_SCOPE on it (commit `a7b347d2`). On resume, the seat re-pointed the test's private 25F84 checkout to R7. It then returned NEEDS_RULING on two repository-root preflight tests that needed the same kind of re-point. The lead ruled them inside the amendment rule: the matching epoch becomes the active 25G83, the differing epoch becomes 25F84, and both refusal assertions stay. The delegation wrapper would not resume the seat a second time, so the lead made that two-line change at the bench. Both edits are in commit `e14e00bb`, which records the module as 27 of 27 passing (activation item 46).

Whether each edit is a pure re-point, with no assertion weakened, is for the review steps of design ruling §9 (steps 5, 6 and 8). This record does not certify it.

## 10. Open at drafting

- The disposition of §8 by the cold final pass.
- §7.3, after the merge.
- The lane that gives old-epoch results a route naming R7 (§8).
- Before the next 25G83 window of any kind: enforcement of H5 and H6 in the capture chain, and, for a window that takes calibration captures, H5, H6 and H7's pooling rule entered in the registration by amendment (addendum A3 §3 S6 and §6).
- H1 stays until a written ruling closes the cap question by route R or route M.

## Re-issue before review (lead, 2026-09-27)

The first bytes the tool wrote (sha256 `9e5c735bf7b4d27604bfadd87809750974322258b943fd1afb04d1873e824c06`, whole-file seal `2e0d88b5…`) omitted two passages the science addendum A1 attached to disclosures D2 and D4 (its A1.1 "adds to … D2" and its correction A1.4(d) of D4), and their `issuance.reason` did not name addendum A3. The drafter of this record flagged the gap. The lead amended the issuance text's builder to carry both passages verbatim and to name A3, and re-ran the tool. The input seal stayed `e7363bdd…`, so no input to the arithmetic changed. The file sha256 became `80c2303611268b6b94626e001fb5df0e783719744145c9f6a31d4061ddee351b`, the whole-file seal `8477d8ce3cde8d3e6c90f2f10a15024db060235dfba3342b64c5c64c3f3ecc2c`, and the loader pin was updated. This happened before any refuter or final pass read the bytes.
