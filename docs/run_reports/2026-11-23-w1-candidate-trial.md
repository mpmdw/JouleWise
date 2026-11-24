# W1 candidate TRIAL assembly · 2026-11-23

**TRIAL. Not a candidate and not for promotion.** This is a throwaway full
assembly of every W1 component on the issued pin. It gives one exact tree that
CI can test and an exact readiness ledger, so that the real promotion is right
the first time. The issued W1 pin stays `b2e01464d` (PR #734) until the lead
promotes one reviewed candidate. [RUN_STATE 462](https://github.com/mpmdw/JouleWise/blob/484e220eb/RUN_STATE.md#L3643-L3654) · [RL-193 §3](https://github.com/mpmdw/JouleWise/blob/1850d6930/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L23138-L23158)

| | |
|---|---|
| Draft PR | PR #958, `ops/2026-11-23-w1-candidate-trial` → `ops/2026-11-11-w1-presign` (do not merge) |
| Base | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` (the head of PR #734) |
| Final source head (CI target) | Session 1: `e2baa3003536f8cfdd8a472494b19e4656d290b0` (tree `4455d777a`). Session 2: see §0 |
| Seat | Session 1: `opus-w1-trial-assembly-1123` (Claude Opus 5.5), Mon 23 Nov 19:20–20:57 PST. Session 2: `opus-w1-integration-owner-1123` (§0) |
| Blind status | Blind. Only rulings, code, public pins and synthetic witnesses were used. `r1_slots.json`, `inputs.json` values and the planning release were handled **by hash only**. No custody, energy, power, meter, transcript, slot, hazard, sealed or restricted file was opened. |

**Not done.** Nothing was merged. In session 1 nothing was pushed to a component branch or to the W1 ref. Session 2 pushed by the lead's L1, L2 and L4 to PR #944, the new PR #959 and PR #886, normally, with no rebase and no force; the W1 ref is untouched. `RUN_STATE.md` and `TASK_QUEUE.md` were not edited. No SSH was used, and no chain step 1–6 or WP19 ran on real data. No receipt was signed.

## 0. Session 2: the lead's decisions applied (integration owner)

Seat `opus-w1-integration-owner-1123` (Claude Opus 5.5), Mon 23 Nov 21:46 PST onward. It applies lead decisions L1, L2, L4, L6 and L8 and findings F-6, F-7, F-8 and F-13 (2026-11-23 21:45). It also integrates two items from other lanes. The first is #839's fix. The second is the research lead's rulings RL-203 to RL-213 (Fable seat `fable-w1-rulings-1123`, 21:55), which answer L3, L5, L7, L9 and Q1–Q6. The blind status is unchanged. `inputs.json` values, `r1_slots.json` and the planning release were not opened. The L4 builder was given the same rule.

| Item | Status | Where, and the evidence | Remaining, and who |
|---|---|---|---|
| L1 / F-1: protocol text | **DONE** | PR #944 merged PR #813's branch: `bef3ea87c`, a normal merge with no rebase. `pilot_protocol_v4.md` is `df775656f`, and the line check is on record in the commit. RL-206 accepts the text unreworded. [CI 45336367460](https://github.com/mpmdw/JouleWise/actions/runs/45336367460) green: 21 of 21 jobs at `bef3ea87c`. | none |
| L2: the port as its own PR | **DONE (draft)** | PR #959, `align/2026-11-23-w1-part-c-port` → `ops/2026-11-11-w1-presign`. It starts at D's `7944b5025`. `4633839a4` takes #809's ten Part C paths from `532654cf0`. Its tree equals the trial's 16 port paths byte for byte. [CI 45340247448](https://github.com/mpmdw/JouleWise/actions/runs/45340247448) at `df018026d`: 20/21 jobs green. The only red is `test (3.13, 9)`: `test_rl145_part_c`, 235 failures and 4 errors, which is F-2. The test modules this PR touches pass locally on its head: `test_refusal_allowlist`, `test_host_command_sites`, `test_v4_executed_closure`, `test_v4_registration`, `test_v4_dynamic_closure` and `test_v4_kit` (116 OK). F-2's legacy `test_rl145_part_c` failures are expected here (#809 lane). | Re-refresh if #809 moves: its r3 confirmation audit is still running (#809 lane) |
| L4 / F-3: #886's "R1 pending" tests | **DONE** | #886 `1dbcb4dd5` regenerates the template (F-5; blob `6bfc797bc`, the same bytes as the trial's). `8fc76a0b9` rewrites the tests to assert the filled state: R1 no longer pending, and the committed `--check` stopping first at the R0 binding. It was pushed normally by this seat's L4 builder. On the trial head `348bc1603`, `test_v4_kit`, `test_v4_w1_plan`, `test_w1_kit_r10`, `test_w1_rl122_kit` and `test_v4_prequal` all pass locally. #886's [CI 45340766338](https://github.com/mpmdw/JouleWise/actions/runs/45340766338) is **green, 21/21**, including `quick` and the seven shards that were red in 44631157069 | none (see the L4 note below) |
| L6 / F-7: 24 stale command sites | **DONE** | PR #959 `ca41d5477`. The decision is LEAD-PENDING:328 (2026-11-22 02:49): "the 24 stale historical command-site declarations move to a separate historical inventory file; the active signing inventory equals the exact scan." The active inventory has 338 rows and equals the scan. `tests/host_command_sites_historical.json` holds the 24, and one new test keeps them out of the scan. 3 tests OK | none |
| F-6 and L5: hazard census | **DONE** | PR #959 `b13d6f14b`: 5 sites, 2 guards and 2 scope gaps listed. `fbe696ca1` then applies RL-208 with RL-93's unapplied recategorisation. All 26 smoke-launcher rows are now INTERNAL with RL-93's sentence, and so are RL-93's two `launch` rows. The two Part C modules are `not_scanned` with RL-208's reason. The census is clean, and `test_refusal_allowlist` gives 24 OK | RL-93 C09 has two parts that are not in this change. One is the "R1 rehearsal driver, kit and runtime" reason. The other is the check of `v4_registration.py` (`alignment_workload` or `v4_desk`). Both are the lead's |
| F-8 and RL-211: receipt file list | **DONE** | PR #959 `83786c965` adds `scripts/align_r1_part_c_evidence.py` to `EXECUTED_CLOSURE` and the receipt template. `df018026d` adds `r1_planning_release.json` to `_NAMED_ARTIFACTS` and the template (RL-211). `test_v4_executed_closure` 6 OK | The lead fills both rows at the STRICT signature |
| F-13 and L9: raw frozen suite in ordinary shards | **DONE** (the engineering half) | PR #959 `2b7620b9a` declares the module in `scripts/test_timings.json` `exclusive_modules`, with `runs_in` set to the 16-shard workflow. The ordinary shards and the quick tier skip it, as on main. RL-209 calls this "engineering" | RL-209: the signing result must be v3.2, run directly, not through the shim. Waiting on Astra's v3.2 issue and #809 adopting it |
| L7: `rank_deficient_design` | **DONE in trial** | RL-212 confirms the lead's preference. Trial `e2cf3ca00` is its own commit after #813 and #944. It places RLD:23212's sentence verbatim in P4's S-score bullet, in AMENDMENT-R1-DRAFT and in E2's fixture block. `test_rl182_registration` and `test_protocol_v4_doc` give 12 OK. P4 is now `687badfd8` | Repeat this one commit on the real integration branch |
| L8 / F-9: final-step order | **DONE** | §9 below. RL-210 confirms it | none |
| L3 / F-4b: thermal-policy shape | **RULED** (RL-207) | Complete the policy in `inputs.json` with four keys: `heavy: true`, `per_turn: true`, `sensors.fan_keys` (equal to `r1_runtime.json`'s list) and `sensors.r0_sha256` (equal to `R0.record_sha256`). No code change | The lead, at §9 step 1. The authorized R0 digest is a missing fact (RL-207) |
| F-11 / L10: #839's zsh `PATH` | **DONE** (#839 lane) | #839 `a37a3462b` (Sol seat `sol-839-fix-1123`), [CI 45335845504](https://github.com/mpmdw/JouleWise/actions/runs/45335845504) green. It returns 0, 1 and 2 under zsh, bash and sh. Merged into the trial at `a2ae37e3c` | The lead confirms the fix (RL-205) |
| F-12: #826's TERM test | RULED (RL-204) | It does not hold the fold | The lead records one line on the cause before signing |
| RL-209: frozen shard 2 lost | **Investigated, not closed** | On the trial tree, shard 2 was lost twice: run 45320845394 attempt 1 (03:50–04:39Z, 49 min) and run 45329958383 (05:04–05:52Z, 48 min). Neither left a step conclusion or a log blob (`BlobNotFound`). On #809's own tree, shard 2 passed in 17 min (run 45320110153), and every other trial shard takes 8–15 min. Attempt 2 of 45320845394 was cancelled by the concurrency group when `e08638fa6` was pushed. It was not lost. In session 2, shard 2 passed in 10 min on the trial at `10e809c1f` (run 45338335655). On PR #959 at `2b7620b9a` (run 45338251730), the same shard was still running past 18 min after its other 15 shards had finished. That run was then cancelled at 20 min by the next push, so the comparison there is inconclusive. So the hang is intermittent and not tied to the trial's extra bytes. It is a slow or hanging case in shard 2's partition, which the #809 lane has to find. | #809 lane and the lead: RL-209 holds item 2 until this is explained |

**Trial assembly, continued** (merges only, no rebase; ten blobs 10/10 after every step):

| # | Step | Trial commit | Ten R1 blobs |
|---:|---|---|---|
| 12 | PR #839 at `a37a3462b` (F-11 fix) | `a2ae37e3c` | 10/10 |
| 13 | PR #944 at `bef3ea87c` (carries #813; L1). It changes no file | `83e330e26` | 10/10 |
| 14 | PR #959 at `2b7620b9a` (L2; F-6, L6, F-8, F-13) | `10e809c1f` | 10/10 |
| 15 | RL-212 `rank_deficient_design` clause (L7) | `e2cf3ca00` | 10/10 |
| 16 | PR #959 at `df018026d` (RL-208 and RL-93 categories; RL-211) | `a59ef2de4` | 10/10 |
| 17 | PR #886 at `8fc76a0b9` (L4; F-3 and F-5 now on PR #886). The template is unchanged: both sides have blob `6bfc797bc` | `348bc1603` | 10/10 |

**First complete frozen matrix on the trial** (`partc-frozen-differential` run [45338335655](https://github.com/mpmdw/JouleWise/actions/runs/45338335655) at `10e809c1f`):
- All 16 of 16 shards reported. There were **25,300 cases: 1,079 AGREES_PASS, 4,673 OTHER_REFUSAL and 19,548 REFUSED, with 0 FALSE_PASS, 0 WRONG_VERDICT and 0 HARNESS_ERROR.** The suite was v3.1, sha256 `12ca35d3…1588`, with 144 census stand-in points added. I summed the 16 shard logs myself because the run's `totals` job was still queued for a runner.
- This ran through the shim, so under RL-209 it is honest interim evidence and **not signing evidence**. Signing needs v3.2 run directly.
- The evaluator, the evidence module, the suite and the workflow are byte-identical at every later trial head.
- I cancelled PR #959's duplicate frozen run (45340247578), which tests the same Part C bytes, to free hosted runners for the trial's `ci`. It can be re-run.

**Trial CI.**
- At `10e809c1f` (steps 12–14, before #886's fix), `ci` run [45338335723](https://github.com/mpmdw/JouleWise/actions/runs/45338335723) had, at 23:04, `quick` and `test (3.13, 2)` red, 9 jobs green and 10 shards still running. Every red was F-3: `test_v4_kit` (7) and `test_r1_rehearsal` (3 failures, 2 errors). #886's `8fc76a0b9` cures these, and they pass locally at `348bc1603`. That run was superseded by the push of the session-2 head.
- **Session-2 head `122828bdd`** (source `348bc1603`, plus the report):
  - `ci` run [45345268049](https://github.com/mpmdw/JouleWise/actions/runs/45345268049): **20 of 21 jobs green**, `quick` and shards 1–8 and 10–12 included. The **only red is `test (3.13, 9)`: `tests.align.test_rl145_part_c`, 235 failures and 4 errors**, which is F-2 and waits on the #809 lane. Every other session-1 red is gone: F-3, F-6, F-7, F-8 and F-13.
  - `partc-frozen-differential` run [45345268155](https://github.com/mpmdw/JouleWise/actions/runs/45345268155): **green, 17/17**. `totals` gives 16 shards with a clean control and 4/4 bindings. The matrix is 25,300 cases: 1,079 AGREES_PASS, 4,673 OTHER_REFUSAL and 19,548 REFUSED, with 0 FALSE_PASS, 0 WRONG_VERDICT and 0 HARNESS_ERROR. It ran v3.1 with 144 stand-in points, so it is interim evidence and not signing evidence (RL-209).
  - Local checks at `348bc1603`: kit regeneration and template regeneration change no file, and `--check` stops at `R0.record_sha256` (F-4a).
  - This docs-only commit starts its own CI run.
- Note for the lead (L4): six S6 failures came from `r1_runtime.registered_s6()` (one of the ten frozen sources) reading `r1_slots.json` as the S6 registration. After #886's fill, that file is the R1 hardware record, and its `s6_tuning` has no `from_c`/`to_c`. The tests now pin a synthetic S6 registration. No W1 path calls it, but the lead may want one line on record.

## 1. Composition and order

The order is RL-193 §3's confirmed composition: "on PIN, #826, #839, #831,
#813, #886, #904 (replacing #897), then the accepted #809 port". The order
of merges is the lead's, under one condition: every generated or bound
artifact is produced on the final tree after #809. This trial follows the
same order as rehearsal D and its promotion recipe. #886 sits directly after
#813, then #904, then #944, then the Part C port. #944 (option C text)
postdates RL-193. RUN_STATE 532–533 require it on the W1 line before signing.
It goes before the port so the port stays last. [RUN_STATE 532–533](https://github.com/mpmdw/JouleWise/blob/484e220eb/RUN_STATE.md#L2059-L2077) · [Rehearsal D](https://github.com/mpmdw/JouleWise/blob/8ab694995/docs/run_reports/2026-11-22-w1-candidate-rehearsal-d.md)

| # | Component | Head merged | Trial commit | Tree | Ten R1 blobs |
|---:|---|---|---|---|---|
| 1 | PR #826 desk-seal successor | `1fc28324d` | `482812eb5` | | 10/10 |
| 2 | PR #839 step-4 and restore proofs (stacked on #826 `3dfeadc0c`) | `70b795954` | `c64e10bc2` | | 10/10 |
| 3 | PR #831 S-row builder | `b38cef828` | `53bb09b70` | | 10/10 |
| 4 | PR #813 RL-176 Q and decode-only repeat | `82542232d` | `5dbef45ec` | `3652381ee` = rehearsal D's tree | 10/10 |
| 5 | PR #886 R1 fill | `3712de681` | `e046eaaec` | | 10/10 |
| 6 | PR #904 contrast-writer repair (replaces #897) | `a2c6800bc` | `dd755715b` | | 10/10 |
| 7 | PR #944 option C text, **conflict F-1** | `16f10ade2` | `0052d36db` | | 10/10 |
| 8 | PR #809 port, step a: rehearsal D's scoped W1 port | `7944b5025` (scaffold `09b1ddbd5` + #809 at `cea5fb695`) | `3bd828e9c` | | 10/10 |
| 9 | PR #809 port, step b: refresh to #809 `ac551d019` | 7 Part C paths | `e44de7698` | | 10/10 |
| 10 | Regenerate `night_plan.template.json` bindings (F-5) | — | `67f74cbbd` | | 10/10 |
| 11 | PR #809 port, step c: refresh to #809 r3 `532654cf0` (pushed 19:31, during this trial) | 6 Part C paths | `e2baa3003` | `4455d777a` | 10/10 |


**What #809 contributes to the tree.** PR #809 is based on `main` and 1,945
commits ahead of the pin, so merging its head would import main. Only the
port belongs on the W1 line. RL-183 §1.3 sets that port's contract, and
RL-193 §3 places it last. This trial takes the same ten Part C paths byte
for byte from #809's current head. They are the evaluator, the evidence
module, five test and sweep files, the frozen suite, the gate test and the
hosted frozen-suite workflow. The port also carries rehearsal D's W1
scaffold (`ops/2026-11-18-part-c-rl183`). That scaffold holds the follow-up
kit, the smoke launcher, legacy launcher tests and timings, D's 362-row
host-command union and one W1-only fixture. #809's other paths stay out as
main-line operations tooling: `scripts/air/*`, the magistrate watchdog,
`gen_current`, `CANONICAL.md`, `POINTER_RULE.md` and its run reports.
**The port is not final.** #809 is in an active fix round, and its head
moved twice in two days.

**Not in the tree.**
- **PR #824, the R0 sampler.** It is a host tool on its own measurement lane, with base `lane/2026-11-05-align-pilot10-benign`. The W1 tree binds only the authorized R0 record by hash: `R0.record_sha256` = `sensors.r0_sha256` (RL-193 item 6). [Rehearsal D gate table](https://github.com/mpmdw/JouleWise/blob/8ab694995/docs/run_reports/2026-11-22-w1-candidate-rehearsal-d.md#promotion-gates-and-owners)
- **PRs #887, #889, #894 and #896.** They go to C1's re-signed receipt (RL-182 §1.5, RL-193 §3).
- **PR #897.** It is superseded by #904, which carries the byte-identical patch.

## 2. Findings

| ID | Status | Finding | Minimal resolution taken in the trial | Owner |
|---|---|---|---|---|
| F-1 | **DONE (§0, L1; RL-206)** | **Registration-text conflict in `docs/align/pilot_protocol_v4.md`** between #813 and #944. In hunk 1, #813 adds RL-149's descriptive item 9 just above B8, and #944 replaces B8. In hunk 2, the RL-18 interpretation line takes #813's S clause ("on the decoded part of each reference-state row, in gated episodes") and #944's K clause ("a physical positive control is registered (B10)…"). | The union: item 9, then #944's B8 verbatim, then one combined interpretation line. The blob is `df775656f`, byte-identical to rehearsal D's. Line check: every line either PR adds is present except that one combined line, and every line either PR removes is absent. | Lead confirms the text, or #944 is rebased on #813 to carry it. Fable sees it in the cold pass (Q1). |
| F-2 | **blocked-by-PR-#809** (cause pointer in §0) | #809 is not accepted. r3 `532654cf0` landed at 19:31 during this trial, after r2-astra-confirm returned BLOCK with 5 HIGH. RL-193 item 2 needs an accepted head with zero false passes on v3 and the six-column supplement. The supplement case is present at r3. Rehearsal D also flagged two owed items: legacy W1 launcher fixtures (234 failures plus 4 errors in D) and the two protected stored replays (RL-183 §1.3). | Ported r3 byte-equal so that CI tests the newest bytes. | #809 builder, independent executing auditor, lead |
| F-3 | **DONE** (PR #886 `8fc76a0b9`; CI 45340766338 green) | **#886's own CI is red: 8 jobs, about 30 tests.** The tests assert the pre-fill "R1 pending" state, for example `test_v4_kit` `test_placeholders_fail_check…`, `test_sizing_is_only_a_provisional_preview…` and `test_d_has_required_base_controls_and_explicit_pending_slots`; `test_v4_w1_plan` (7); `test_v4_prequal` (4); `test_r1_rehearsal` (5); `test_w1_rl122_kit.test_record_file_is_read_canonically`; `test_r1_turn_counts_export`; `test_w1_prequal` chain; `test_r1_followup`; `test_w1_kit_r10.test_template_has_no_receipt_slot`. The trial CI reproduces the same set, except that F-5 cures 6 of the `test_v4_w1_plan` failures (§5). | None. These are test-expectation or fill-shape decisions for #886's owner. | #886 owner, lead |
| F-4 | **(a) blocked-by-PR-#824; (b) RULED RL-207, lead fills; (c) NEEDS_LEAD** | **`align_v4_kit.py --check` has at least three successive stops on the final tree.** (a) `R0.record_sha256 must bind thermal_policy.sensors.r0_sha256`: R0 is unbound (#824 lane, RL-193 item 6). (b) With a **synthetic** digest in a throwaway export, the next stop is `thermal policy has missing or unknown fields`. #886's `inputs.R1.thermal_policy` (DEC2's values) has no `heavy` or `per_turn` keys and no `sensors.r0_sha256` or `sensors.fan_keys`. The frozen `thermal_gates.validate_gate_policy` requires `heavy` and `per_turn` (`thermal_gates.py:101-106`), and the kit requires both to be true for D (`align_v4_kit.py:1131-1137`). The kit's own fully supplied fixture carries all four (`tests/align/test_v4_kit.py:440-446`). (c) With those four added **synthetically**, the next stop is `sizing_b5.json is not derivable yet`: the lead commits `w1_plan.json` (a filled `night_plan.template.json`), then regenerates. Later stops are unknown. | None. The probes ran only in `/Volumes/JW-EXT/scratch/opus-w1-trial-assembly-1123/probe-r0`; the trial's `inputs.json` is unchanged. | R0 owner and lead for (a). Lead and Fable for (b): RL-189 §2.5 item 2 says `inputs.json` holds DEC2's five `set_inputs` values **unchanged**. Lead for (c). |
| F-5 | **DONE on PR #886** (`1dbcb4dd5`, blob `6bfc797bc` = the trial's `67f74cbbd`); moves again at the R0 binding | **`night_plan.template.json` member bindings were stale.** #886 regenerated the 16 stage files (chain step 7) but not the template, so 14 member `config_sha256` values were stale. `--regenerate-template` on the final tree fixed them: blob `e478d2427`→`6bfc797bc`, sha256 `b1906f37…`→`ff0c4d41…`. | Committed in the trial (`67f74cbbd`). These bindings move again when R0 is bound. | Lead, at final regeneration |
| F-6 | **DONE (PR #959; RL-208)** | **The refusal census fails on the trial tree.** There are 5 unlisted refusal sites and 2 changed guards in `scripts/run_align_r1_smoke.py`: `EvidenceFailure` `verdict_binding`, `evidence_unverifiable` and `source_integrity`; `main` return code 2 (×3); a `soak_child` re-raise; and the guard text of the two `idle soak` ValueErrors. There are also 2 scope gaps: `align_r1_part_c.py` and `align_r1_part_c_evidence.py` are neither scanned nor listed as `not_scanned`. Every one of them comes from the Part C port scaffold. | None. `configs/gates/hazard_refusals.json` needs a reviewed disposition (Ed's rule: physics refuses, everything else is a flag). | #809 port owner, lead |
| F-7 | **DONE (PR #959, L6)** | **Host-command inventory.** The lead decided on 2026-11-22 at 02:49 that the 24 stale historical declarations move to a separate historical inventory, so that the active signing inventory equals the exact scan. No branch implements this yet. `tests.test_host_command_sites` fails on the trial with exactly 24 stale rows and 0 missing, the same as rehearsal D. | None | #809 port owner, lead |
| F-8 | **DONE (PR #959; plus RL-211)** | **Executed and dynamic closure.** `test_v4_executed_closure.test_every_executed_module_and_script_is_in_the_receipt_artifact_set` fails: `scripts/align_r1_part_c_evidence.py` is executed but is not in the receipt artifact set (`v4_registration.py` closure). The regenerated dynamic trace (§3) adds that path plus #813's two and #831's `s_rows.py`. | None. The closure inventory is reviewed code, and the trace is regenerated after F-3/F-4. | Lead |
| F-9 | **DONE as runbook (§9, L8; RL-210)**; MBP-step | **Step 4 must follow the final kit regeneration.** The RL-184 §4 three-blob comparison includes `collection_plan.json`. #886 already changed it (`d2219230f`→`fbd357c45`), and binding R0 changes it again: the probe regenerated it together with `inputs.json`, `identity_pins.json`, `plan_tree.json` and 16 stage files. Any step-4 export run before the R0 binding therefore has to be rerun. #839 proved the checker only in an invented repository; no real `STEP4_CHECKOUT` is recorded. | None | Lead and magistrate |
| F-11 | **DONE (#839 `a37a3462b`)** | **#839 is FIX-FIRST** (Fable seat `fable-w1-813-826-1123`, 19:32). In the W1-BLOCKERS step-4 checker, `for path in` (WB:136) overwrites zsh's `PATH`, so the block exits 2 in zsh in every case. It fails closed, but it never gives a usable comparison. The trial carries #839 at `70b795954` unfixed. | None | #839 owner: rename `path` at WB:136, 141, 142 and 146; rebase onto `1fc28324d`; add one sentence about the report's `3dfeadc0c` pin |
| F-12 | **RULED RL-204; NEEDS_LEAD line** | **#826's intermittent TERM test.** `test_r1_runtime_e2e.test_term_reaches_the_runtime_which_closes_its_custody_before_exit` (`'reading' != 'session_end'`) failed at `3dfeadc0c` and passed at `1fc28324d` with the test and the ten sources unchanged. Fable ruled it does not hold the fold. | None | Lead records one line on the cause before the signing commit, and records any red on the candidate head with its re-run (Fable seat ruling) |
| F-13 | **DONE engineering (PR #959); v3.2 waiting (RL-209)** | **The raw frozen suite fails in the W1 line's ordinary CI shards.** On main, ordinary discovery never collects `tests/align`, so #809 runs `test_partc_frozen_differential.py` only through its `partc_suite_census.py` shim (16-shard workflow). The W1 line's shard runner **does** collect it, and in the trial's `test (3.13, 10)` the v3.1 clean control fails against the r3 evaluator: `Disagreement: clean control: other_failure`. Through the shim, the same file gives 23,712 cases on 15 shards with **0 FALSE_PASS, 0 WRONG_VERDICT and 0 HARNESS_ERROR**, plus 135 census stand-in points added. | None | Lead: adopt v3.2 (a fixture that carries the census points), or exclude the raw file from W1-line ordinary shards in favour of the workflow. Fable: Q4 |
| F-10 | Process note | **Tooling hazard, fixed and isolated.** This seat could not read the shared gitdir under `air-home`, so the trial used a scratch blobless clone. With `GIT_DIR`/`GIT_WORK_TREE` exported, `align_v4_dynamic_trace.py`'s fixture child committed into that clone (`6f539e610 "fixture"`). It swept up the template change. The commit was local only and was soft-reset and recommitted before any push; nothing reached origin. **For promotion: never run the trace, kit or tests with `GIT_DIR` or `GIT_WORK_TREE` exported.** Separately, one stopped trace run kept running in the background. From 19:37 to 19:59, two trace processes ran beside 3 test workers. That is 5 processes against the 4-worker budget; I name the overrun. | The worktree `.git` was pointed at the scratch clone for the rest of the run. The original `gitdir:` line was restored at the end. | Integration owner |

## 3. Invariants on the final tree

**Ten frozen R1 sources (RL-183 §1.1, RL-193 item 7).** All ten blob IDs are
equal to `b2e01464d`'s after every one of the 11 steps and at the final head.
The list is `R1_EXECUTED_SOURCES`, `v4_registration.py:489-495` at the pin.

| Blob at PIN = trial | Path |
|---|---|
| `33c6876e6a98` | `scripts/align_r1_rehearsal.py` |
| `96b249a6eb44` | `scripts/align_r1_runtime.py` |
| `261761f1a5e3` | `joulewise/align/apple/r1_runtime.py` |
| `1ef822bee6d3` | `joulewise/align/apple/r1_runtime_contract.py` |
| `8a1a96dcb10e` | `joulewise/align/apple/smc_enumeration.py` |
| `b46769d70df0` | `joulewise/align/apple/thermal_gates.py` |
| `bf8479b26774` | `configs/align/v4/r1_runtime.json` |
| `e412bb4389aa` | `joulewise/align/apple/r1_phase_table.py` |
| `ff30c29178ad` | `joulewise/align/apple/workload.py` |
| `e7cbd6808c5a` | `joulewise/align/apple/thermal.py` |

**Accepted diffs (RL-193 item 7, second half).** `tools/accepted.py` gave
these results at the final source head:
- 110 paths changed against the pin, all attributed to a component and 0 unattributed.
- 106 are byte-equal to their single owner's head. The Part C paths are compared with #809 `532654cf0`.
- Two shared paths (`docs/align/v4/DEVIATIONS.md` and `joulewise/align/apple/v4_desk_seal.py`) keep every owner's hunks intact by reverse-apply.
- One shared path is F-1's line-verified union.
- One path, the regenerated template (F-5), is written by the trial itself.

The scaffold and union paths of the #809 port (§1) have **no PR of their
own**. Their "accepted diff" is rehearsal D's commit `7944b5025`, which no
reviewer has admitted (NEEDS_LEAD L2).

**Kit regeneration (RL-193 §3; chain step 7).** `python3.13 -B scripts/align_v4_kit.py` on the final tree exits 0 and changes **no file**. #886's regenerated kit is byte-stable on the assembled tree. `--check` refuses at R0 (F-4).

**Dynamic closure trace.** Regenerated in the seat with `scripts/align_v4_dynamic_trace.py --out <scratch>` (about 22 min). **Not committed**, because three traced scenarios are `ok: false` on this tree: `arm_install_session`, `r1_synthetic_arm` and `r1_to_w1_chain`. Their traced tests fail on F-3/F-4, and committing the trace would bake those failures in. Against the committed trace (blob `635437524`, unchanged since the pin), the regenerated one (blob `e3459fa2e`, sha256 `7f3681a5af13eca1…`) adds four opened paths: `joulewise/align/apple/rl176.py`, `rl176_phases.py` (#813), `s_rows.py` (#831) and `scripts/align_r1_part_c_evidence.py` (#809 port). It also adds 3 and 2 tests to two scenarios. Caveat: a stopped earlier trace process kept running and wrote this file. It started at 19:35, before the r3 refresh at 19:37, so it read mixed r2/r3 Part C bytes. Path sets do not depend on those bytes. Regenerate once more on the promoted head after F-3/F-4/F-8.

**Reader census (RL-193 item 5; RL-183 §2.3).** The census module from
`/Volumes/JW-EXT/scratch/d-w1-signing-reader-census/run_census.py`, run
with `--signing-head` on `e44de7698` (tree `b3c41447f`), **PASSES**. It
finds 1,588 tracked and 298 bound Python paths, 0 production reader sites
and 0 test-origin reader sites, and the W1 intersection is `[]`. All 14
mutation controls pass. This was the head before r3. The census reads
Python, and r3 changed only Part C files, which the census reported as
non-readers at `e44de7698`. Rerun at the signing head. The module still has
to be bound into the final receipt (lead).

**R0.** Not bound. `inputs.json` has `R0.reasoning_effort` only. RL-193 item 6 is open (F-4a).

**U3 and step 4.** Against the pin, the exporter changed (#826,
`ab9b9e52a`→`b35c94801`), the selection is unchanged (`729e8667d`), and the
collection plan changed (#886, `d2219230f`→`fbd357c45`). The U3 bar and
gate need real pilot data and were not run here (F-9).

**WP19.** Not run. `align_v4_wp19.py` requires the real R1 X-G `align_turns.jsonl` (a transcript), so it is an MBP or lead step.

**Receipt.** `registration_receipt.json` is the unsigned template. #813 adds two `null` artifact rows (`rl176.py`, `rl176_phases.py`). The lead signs at the final pin.

**RL-189 §2.5.**
- Item 1: `r1_planning_release.json` sha256 is `171b2a3bd28ada24f832e1deafc5d526bd47ff60d55388859220a12ddd5ddf6a`, which matches `171b2a3b…df6a`.
- Item 2: `r1_slots.json` sha256 is `f156239e…9b94`. Not opened; whether it is the backfilled record is #886's claim.
- Items 3 and 4: the anti-hindsight list is a lead record for the packet (RL-183 §2.7). It is not committed anywhere, and the 488 s cap line and the two-session line are not yet written.

## 4. Hash ledger: what changed and who re-signs

Blob IDs are abbreviated. A changed bound artifact is re-signed by the
lead's STRICT receipt on the final pin (RL-193 §3) and confirmed in Fable's
cold pass (RL-193 item 9).

| Path | PIN | #886 | Trial final | Changes again at R0 binding? | Re-sign step |
|---|---|---|---|---|---|
| `configs/b6/executing_reviews.json` | `f39c852e6` | `f39c852e6` | `5d0a17c60` | no | #813 review record; RL-193 item 3 |
| `configs/campaigns/align_v4/collection_plan.json` | `d2219230f` | `fbd357c45` | `fbd357c45` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/night_plan.template.json` | `e478d2427` | `e478d2427` | `6bfc797bc` | yes (bindings) | F-5; final regeneration |
| `configs/campaigns/align_v4/plan_tree.json` | `e2f3a225d` | `29ab796b7` | `29ab796b7` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/registration/identity_pins.json` | `f77ea3fbd` | `7d1c5503c` | `7d1c5503c` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/registration/inputs.json` | `8399ccc9a` | `3becfed63` | `3becfed63` | yes | Receipt; F-4 (R0, policy); RL-189 §2.5 item 2 |
| `configs/campaigns/align_v4/registration/r1_planning_release.json` | `absent` | `daeb4708a` | `daeb4708a` | no | RL-189 §2.5 items 1–2; receipt; item 8 list |
| `configs/campaigns/align_v4/registration/r1_slots.json` | `696db570f` | `b6056ef6f` | `b6056ef6f` | no | RL-189 §2.5 items 1–2; receipt; item 8 list |
| `configs/campaigns/align_v4/registration/registration_receipt.json` | `6cac7ac4d` | `6cac7ac4d` | `1a670909a` | no | Lead STRICT signature at final pin |
| `configs/campaigns/align_v4/stages/episodes-a/align-v4-episodes-a-e05.json` | `6fd6bec4b` | `40f9ecdde` | `40f9ecdde` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-a/align-v4-episodes-a-e06.json` | `56eec88ed` | `2005423c9` | `2005423c9` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-a/align-v4-episodes-a-e07.json` | `eae3a60c3` | `b205a7336` | `b205a7336` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-a/align-v4-episodes-a-e08.json` | `b9d3f2db7` | `444e0d21c` | `444e0d21c` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-a/align-v4-episodes-a-e09.json` | `c6fdf6640` | `5d428e1d7` | `5d428e1d7` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-a/order_manifest.json` | `ef14c00d6` | `82a98d933` | `82a98d933` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-b/align-v4-episodes-b-e10.json` | `8d7adcaab` | `cb8e1ef5d` | `cb8e1ef5d` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-b/align-v4-episodes-b-e11.json` | `bcc330e7b` | `c41c39992` | `c41c39992` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-b/align-v4-episodes-b-e12.json` | `103ca5289` | `071271a65` | `071271a65` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-b/align-v4-episodes-b-e13.json` | `1d3753894` | `1960ff1d7` | `1960ff1d7` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-b/align-v4-episodes-b-e14.json` | `7df2f1b7c` | `496883993` | `496883993` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-b/align-v4-episodes-b-e15.json` | `09d576d28` | `9115ee44b` | `9115ee44b` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-b/align-v4-episodes-b-e16.json` | `462a2b94d` | `4d4093813` | `4d4093813` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-b/align-v4-episodes-b-e17.json` | `58f1f18ca` | `923c3f3dc` | `923c3f3dc` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-b/align-v4-episodes-b-e18.json` | `254f2de25` | `336b2b2a2` | `336b2b2a2` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `configs/campaigns/align_v4/stages/episodes-b/order_manifest.json` | `be4e866f6` | `5db5ad771` | `5db5ad771` | yes | Kit regeneration on final tree (RL-193 §3); receipt; item 8 list |
| `tests/host_command_sites.json` | `4f35a92a7` | `4f35a92a7` | `37287d796` | no | F-7 inventory decision; #809 port |

R0-binding forecast: with a synthetic digest, regeneration rewrote
`inputs.json`, `identity_pins.json`, `plan_tree.json`, `collection_plan.json`
and the 16 stage files. Every kit hash #886 carries, and the template
bindings, move once more at the real binding. That is why RL-193 §3
requires regeneration on the final tree only.

## 5. Tests

**Local, focused.** The standing test budget of 2026-11-22 limits local
runs to touched modules plus named regressions, at most 4 workers. This
run used 34 modules on 3 workers, plus the trace job; the full suites run in
hosted CI. Modules: the 28 test modules the assembly touches (minus the
frozen differential, which runs in hosted CI), plus `test_v4_kit`,
`test_v4_executed_closure`, `test_v4_dynamic_closure`,
`test_host_command_sites`, `hazards.test_refusal_allowlist`,
`test_w1_kit_r10` and `test_thermal_gate`.

27 of 34 modules pass. 1,039+ tests ran. Six modules fail, and each maps to a finding or to the seat environment. One timed out locally and passes in CI:

| Module | rc | Wall | Result | Note |
|---|---:|---:|---|---|
| `tests.align.test_apple_endpoint` | 0 | 47s | Ran 10 tests in 43.295s OK |  |
| `tests.align.test_harvest_off` | 0 | 153s | Ran 52 tests in 151.516s OK | Passed on re-run. The first run failed only because this seat committed mid-run (HEAD stamp moved) |
| `tests.align.test_harvest_off_review_sol1` | 0 | 242s | Ran 17 tests in 238.032s OK |  |
| `tests.align.test_harvest_off_review_sol2` | 0 | 169s | Ran 22 tests in 165.998s OK |  |
| `tests.align.test_hoff_delta2_sol1` | 0 | 6s | Ran 9 tests in 6.220s OK |  |
| `tests.align.test_hoff_delta2_sol2` | 0 | 6s | Ran 11 tests in 5.157s OK |  |
| `tests.align.test_hoff_delta_sol1` | 0 | 34s | Ran 17 tests in 32.586s OK (expected failures=1) |  |
| `tests.align.test_measurement_core_boundary` | 0 | 2s | Ran 7 tests in 1.110s OK |  |
| `tests.align.test_merge_c84_sol` | 0 | 26s | Ran 3 tests in 22.946s OK |  |
| `tests.align.test_pr777_attack_repros` | 0 | 3s | Ran 15 tests in 0.571s OK |  |
| `tests.align.test_protocol_v4_doc` | 0 | 1s | Ran 8 tests in 0.985s OK |  |
| `tests.align.test_r1_to_w1_chain` | 0 | 5s | Ran 15 tests in 2.843s OK |  |
| `tests.align.test_rl145_part_c` | 1 | 296s | Ran 90 tests in 293.175s FAILED (failures=235, errors=4) | F-2: legacy W1 launcher fixtures against the new evaluator (rehearsal D: 234 + 4) |
| `tests.align.test_rl176` | 0 | 6s | Ran 28 tests in 4.267s OK |  |
| `tests.align.test_rl182_registration` | 0 | 0s | Ran 4 tests in 0.531s OK |  |
| `tests.align.test_s_rows` | 0 | 20s | Ran 67 tests in 18.618s OK (skipped=4) |  |
| `tests.align.test_smoke_delta3_sol1` | 0 | 25s | Ran 16 tests in 25.018s OK |  |
| `tests.align.test_smoke_delta3_sol2` | 124 | 900s | timeout | Hit this seat's 900 s per-module cap under load 15+. **Passes in hosted CI** (15 tests, 90 s) |
| `tests.align.test_thermal_gate` | 0 | 76s | Ran 44 tests in 73.557s OK |  |
| `tests.align.test_v4_desk_real_harvest` | 0 | 141s | Ran 9 tests in 131.120s OK |  |
| `tests.align.test_v4_desk_release_guard` | 0 | 99s | Ran 63 tests in 93.775s OK |  |
| `tests.align.test_v4_dynamic_closure` | 0 | 66s | Ran 10 tests in 65.269s OK |  |
| `tests.align.test_v4_executed_closure` | 1 | 23s | Ran 6 tests in 21.850s FAILED (failures=1) | F-8: `scripts/align_r1_part_c_evidence.py` is not in the receipt artifact set |
| `tests.align.test_v4_kit` | 1 | 28s | Ran 116 tests in 23.783s FAILED (failures=7) | F-3/F-4: "R1 pending" expectations; R0 unbound |
| `tests.align.test_v4_next_arm_packet` | 0 | 540s | Ran 49 tests in 535.506s OK |  |
| `tests.align.test_v4_registration` | 0 | 88s | Ran 25 tests in 82.844s OK |  |
| `tests.align.test_v4_w1_blockers` | 0 | 42s | Ran 18 tests in 41.481s OK |  |
| `tests.align.test_w1_kit_r10` | 0 | 8s | Ran 23 tests in 4.747s OK |  |
| `tests.hazards.test_refusal_allowlist` | 1 | 65s | Ran 24 tests in 65.320s FAILED (failures=2, skipped=1) | F-6 |
| `tests.test_host_command_sites` | 1 | 11s | Ran 2 tests in 10.284s FAILED (failures=1) | F-7: 24 stale, 0 missing |
| `tests.test_mlx_runtime` | 0 | 2s | Ran 44 tests in 1.326s OK |  |
| `tests.test_offload_window` | 1 | 21s | Ran 105 tests in 21.169s FAILED (errors=1) | Seat fence: `PermissionError` creating a synthetic `restricted` dir (also on issued W1 in D). Environment, not code |
| `tests.test_part_c_evidence_ledger` | 0 | 309s | Ran 89 tests in 308.548s OK | Passed after prefetching 3 pinned blobs the blobless seat clone lacked (first run: 14 `git cat-file … bad file`) |
| `tests.test_part_c_gate_evidence` | 0 | 7s | Ran 21 tests in 6.309s OK |  |

**Hosted, exact tree.** PR #958 at `e2baa3003`. Pushed 19:37 PST; foreground-waited until 20:57.

**`ci` run [45320845308](https://github.com/mpmdw/JouleWise/actions/runs/45320845308): FAILURE.** `build`, `changes`, `fences`, `gen-current-py314` and the docs or mock jobs pass. Test shards 1, 3, 7 and 11 pass. `quick` and shards 2, 4, 5, 6, 8, 9, 10 and 12 fail. Every failing test maps to a finding; none is new to this assembly except F-13:

| Failing tests in CI | Shard(s) | Finding |
|---|---|---|
| `test_v4_kit`: 7 "R1 pending" and R0 expectations | quick, 10 | F-3, F-4a |
| `test_r1_rehearsal`: 3 failures and 2 errors (kit evidence binding, S6 tuning, Step D G0 retries) | quick, 9 | F-3 |
| `test_v4_w1_plan.test_values_must_equal_the_inputs_the_kit_installs` (1; #886 alone had 7, and F-5's template regeneration cured 6) | 4 | F-3 |
| `test_v4_prequal.test_kit_check_r0_passes_w1_needs_ready` | 5 | F-3, F-4a |
| `test_w1_rl122_kit.test_record_file_is_read_canonically` | 10 | F-3 |
| `test_r1_turn_counts_export` (1 error) and `test_w1_prequal` chain (1 error) | 2, 6 | F-3 |
| `test_r1_followup.test_order_cuts_timeout_candidates_and_receipt_preservation`: `KeyError: 'to_c'` (#886's `s6_tuning` shape) | 8 | F-3 |
| `test_v4_executed_closure`: `align_r1_part_c_evidence.py` not in the receipt set | 2 | F-8 |
| `test_rl145_part_c`: 235 failures and 4 errors (legacy W1 launcher fixtures) | 6 | F-2 |
| `test_host_command_sites`: 24 stale | 6 | F-7 |
| `hazards.test_refusal_allowlist`: 2 | 12 | F-6 |
| `test_partc_frozen_differential` raw: clean control `other_failure` | 10 | F-13 |

**`partc-frozen-differential` run [45320845394](https://github.com/mpmdw/JouleWise/actions/runs/45320845394): FAILURE on attempt 1, and the cause is infrastructure.** Shards 0, 1 and 3–15 pass. Shard 2's suite step ran 49 min and ended with no step conclusion and no log blob (`BlobNotFound`), which is a lost runner. `totals` then refused with `['shard 2: no log']`. Over the 15 shards that reported: **23,712 cases, 1,022 agree-pass, 4,380 other-refusal and 18,310 refused, with 0 FALSE_PASS, 0 WRONG_VERDICT and 0 HARNESS_ERROR**, plus 135 census stand-in points added. #809's own r3 run of this workflow ([45320110153](https://github.com/mpmdw/JouleWise/actions/runs/45320110153)) passed all 16 shards. I re-ran the failed jobs (attempt 2, started 20:47 PST); the result was pending when this report was written. Check the PR.

**`gate-ledger`:** skipped (draft).

## 6. Readiness ledger

Status words: DONE · blocked-by-PR-N · NEEDS_FABLE · NEEDS_LEAD · MBP-step.

### 6.1 RL-193 §3 signing list

| # | Item | Status | Evidence | Smallest next action |
|---|---|---|---|---|
| 1 | #734 is in PIN's history | **DONE** | PIN `b2e01464d` **is** PR #734's head (`gh pr view 734`: head `ops/2026-11-11-w1-presign@b2e01464d`) | Lead records that #734 is the base itself, which answers RL-193's "add it to the list" |
| 2 | #809 accepted head: zero false passes on v3 plus the six-column supplement, and the two open findings closed | **blocked-by-PR-809** | F-2. r3 `532654cf0`: hosted frozen suite gave 0 false passes on 15 of 16 shards (shard 2 runner lost; re-run pending) in PR #958. Supplement case present (`test_partc_frozen_differential.py:1592`, `test_part_c_evidence_ledger.py:2292`) | Independent executing re-audit of r3 (or later), then lead acceptance and the v3.2 disposition |
| 3 | #813: E1–E17, CI green, the lead's diff against that list, Astra's audit closed | **RULED RL-203; NEEDS_LEAD** (record only) | Fable seat `fable-w1-813-826-1123` (19:32): **FOLD-INTO-W1** at `82542232d`. E1–E17 found once each (`tests/align/test_rl182_registration.py:20-88`). Astra's BLOCK rows are correctly superseded by RL-182b. CI 21 green. Ruling: "condition 1 is met at `82542232d` … No round 8" | Lead commits that ruling as an RL-182b addendum and attaches the E1–E17 diff list to the packet |
| 4 | RL-189 §2.5's four items | **Partial: 1 DONE, 2 blocked-by-PR-886, 3–4 NEEDS_LEAD** | §3 above | Lead writes the anti-hindsight list with the 488 s cap line and the two-session line |
| 5 | Final receipt binds the reader-census module and its evidence | **NEEDS_LEAD** | Census PASS on the trial head (§3) | Commit the census test into the tree or bind it by hash, and rerun it at the signing head |
| 6 | R0 binding and U3, WP19, receipt and gate steps pass `--check` at the final head | **blocked-by-PR-824 + NEEDS_LEAD + MBP-step** | F-4 (three stops), F-9, WP19 not runnable here | Admit #824, bind the R0 record, resolve F-4b, commit `w1_plan.json`, then regenerate, run step 4, run WP19, and run `--check` |
| 7 | Byte-equality proof: ten R1 sources equal PIN, and accepted diffs | **DONE in trial** (re-run on the signing head) | §3: 10/10 at every step; accepted-diff summary; `tools/accepted.py` | Re-run both on the promoted head. Admit or replace the #809 scaffold (L2) |
| 8 | Published file list, `r1_slots.json` included | **NEEDS_LEAD** | §4 lists every bound artifact the trial changes | Lead publishes the list. Fable confirms it in the cold pass |
| 9 | Fable's W1 cold pass on the promoted candidate | **NEEDS_FABLE** (after 2–8) | Packet: head, item 7 proof, v3 result, #813 diff list, item 8 list | Send once, after promotion. Q1–Q6 below can be answered now |

### 6.2 Other signing-adjacent obligations

| Source | Item | Status | Evidence / next action |
|---|---|---|---|
| RL-184 §4 line 1 | Step-4 check compares three blobs | **Checker DONE** (#839 `a37a3462b`); the run itself is §9 step 2 | The text is in `W1-BLOCKERS-merged.md:136-139`, but the block exits 2 under zsh. Fix: rename `path` |
| RL-184 §4 line 2 | One synthetic run of the MBP-only path before W1 arms | **DONE** | Fable seat ruling (19:32): "'MBP-only' names the same-root path, not the host, so the Air run counts" (#839 report:80-90) |
| RL-184 #826 pass | #826's verdict carries to `1fc28324d` | **DONE** | Fable seat: the delta is three test files; RL-184's twelve-green-shards condition is first met at `1fc28324d` |
| Fable seat ruling | One line on the cause of the intermittent TERM test before the signing commit | **NEEDS_LEAD** (F-12) | `joulewise/align/apple/r1_runtime.py:1236`, `thermal.py:193` |
| RL-183 §1.3 | Two protected stored replays (counted Part C, RUN_STATE 328; F0 run 11, item 426): verdict word and failing check names | **MBP-step** | Magistrate or an authorized seat, after #809 is accepted |
| RL-193 §1 | Six-column zero-row supplement green at #809's accepted head | **blocked-by-PR-809** | Case present. Green only once #809 is accepted |
| RL-193 §7 | `rank_deficient_design` registration clause (RL-212: E2 as amended, on the candidate now) | **DONE in trial** (`e2cf3ca00`) | Repeat the commit on the integration branch |
| RL-198a / item 533 | Option C text on the W1 line before signing | **DONE** (#944 `bef3ea87c` carries #813; RL-206) | `pilot_protocol_v4.md` B8, B9, B10 |
| D 11-22 decision | 24 stale host-command rows go to a historical inventory | **DONE** (PR #959 `ca41d5477`) | none |
| RL-183 §2.7 | Anti-hindsight list to Fable | **NEEDS_LEAD** | Not written |
| Exact-tree CI | All suites green on the promoted head | **20/21 green** at `122828bdd` (ci 45345268049). The only red is F-2 (#809 lane). Frozen run 45345268155 is green, 17/17 (v3.1 through the shim; v3.2 is owed, RL-209). `--check` still stops at R0 (F-4a, #824) | PR #958, §0 |

### 6.3 RL-193 §2: the install-only rehearsal (gates the smoke through PREQUAL, not the signature)

| # | Condition | Status |
|---|---|---|
| 1 | Its own typed RUN_STATE item before install | NEEDS_LEAD (after promotion) |
| 2 | Unmodified code at the promoted head; production installer, exit 0 | MBP-step (after promotion) |
| 3 | No hand-made member. If `session.json` can only be written behind the arm gates, stop and return to Fable | MBP-step |
| 4 | Absent before and after; plist copied before uninstall | MBP-step |
| 5 | The job cannot fire; magistrate records that no `run_night` process ran | MBP-step |
| 6 | Burned id | MBP-step |
| 7 | Lead attests applicability; repeat if the head moves through kit, plan, sizing or installer paths | NEEDS_LEAD |

### 6.4 W1 READY checklist (draft at `1850d6930`)

Every row is UNFILLED today and owned after promotion. [READY draft:16–97](https://github.com/mpmdw/JouleWise/blob/1850d6930/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/w1-prearm/W1-READY-DRAFT.md#L16-L97)

| Group | Rows | Status | Blocked by |
|---|---|---|---|
| Lead fills: typed header, issuing lead and authority, validity and deadline | 3 | NEEDS_LEAD | promotion |
| Signer identity and independent signing record; STRICT receipt commitment; probe commitments | 3 | NEEDS_LEAD | §6.1 items 2–9 |
| Immutable receipt commit, runtime checkout and clean proof, receipt-to-runtime link | 3 | NEEDS_LEAD | promotion |
| Exact W1 kit, plan and seal commitments | 1 | NEEDS_LEAD | F-4 (R0, policy, `w1_plan.json`), F-5, F-9 |
| Authorized `HAZARD_PACK` route | 1 | NEEDS_LEAD | F-6 refusal census |
| One-shot Part C with automatic PASS and independent first-pin read | 1 | MBP-step (about 2 h) | §6.1 item 2, RL-183 §1.3 replays |
| Ordinary and W1-mode off-Mac PREQUAL, and PREQUAL digest verification | 3 | MBP-step / NEEDS_LEAD | E3 rehearsal (§6.3), signed inputs |
| Registered native W1 smoke (about 37–42 min) | 1 | MBP-step | PREQUAL |
| Effective condition, qualification boundary, plan ID and schedule, Ed notice and veto | 4 | NEEDS_LEAD | READY |
| Magistrate fills before install (13 rows: READY readback, notice and veto, qual-03 close, predecessor close, fresh SHA, census, stops, physical, battery, disk and meter, link, decision) | 13 | MBP-step | READY |
| Outcome (3 rows) | 3 | MBP-step | install |

## 7. FOR-FABLE: questions for one call

Context for the seat: the trial tree is PR #958 at `e2baa3003536f8cfdd8a472494b19e4656d290b0` (tree `4455d777a`); this report is committed on top as docs only, base
`b2e01464d`. Each question can be answered blind from rulings and code.

1. **F-1 protocol union.** #813 and #944 both edit `docs/align/pilot_protocol_v4.md`. The trial keeps #813's descriptive item 9 (RL-149) immediately above #944's B8, verbatim. It writes the RL-18 interpretation line as: "K: calibrated sensitivity to a known log omission by count withholding; a physical positive control is registered (B10) and is reported with its own word. S: a randomized comparison of the sabotage instruction at logged counts, on the decoded part of each reference-state row, in gated episodes; it is a statement about the instruction, not about successful sabotage, intent or free-running agents." Is this union acceptable registration text, or does either clause need rewording?
2. **F-4b thermal-policy shape.** #886's `inputs.R1.thermal_policy` holds DEC2's values and keys only. The frozen `validate_gate_policy` and the kit need `heavy: true` and `per_turn: true` for D, and `sensors.r0_sha256` equal to `R0.record_sha256`. The kit fixture also carries `sensors.fan_keys`. Under RL-189 §2.5 item 2 ("`inputs.json` then holds DEC2's five `set_inputs` values unchanged"), may the lead add these fixed D controls and the R0 digest to `thermal_policy` as a shape completion? Or must they come from an engineering change, for example `gate_policy_fields` supplying `heavy` and `per_turn`, so that DEC2's object stays byte-unchanged?
3. **F-6 Part C refusals in the hazard census.** The ported smoke launcher refuses with `EvidenceFailure` (`verdict_binding`, `evidence_unverifiable`, `source_integrity`) and exit 2. Under RL-183 §1.2 ("a fail-closed evaluator fails closed"), should these be listed in `hazard_refusals.json` as refusals protecting evidence integrity, rather than turned into flags under Ed's 2026-10-05 rule? And should `align_r1_part_c*.py` be scanned rather than listed as `not_scanned`?
4. **#809's frozen suite in CI.** #809's hosted workflow runs v3.1's file byte for byte through `partc_suite_census.py`. That shim adds the census points frozen `Segment.run` writes, which the v3.1 clean fixture lacks; it adds none on the lead's v3.2 fixture. On the trial tree the shim run gives 23,712 cases on 15 of 16 shards with 0 false passes and 135 census points added. Run raw, the same file's clean control returns `other_failure` (F-13). For RL-193 item 2, does "zero false passes on v3" admit a result obtained through this shim, or must v3.2 be frozen and used first?
5. **Step-4 timing.** Every kit regeneration rewrites `collection_plan.json`, one of RL-184 §4's three step-4 blobs, and binding R0 regenerates the kit. Confirm that step 4 runs once, after the final regeneration, at or blob-equal to the signing commit, and that no earlier step-4 export is reused.
6. **Publication list shape (RL-193 item 8).** The trial changes these bound artifacts: the registration files `inputs.json`, `identity_pins.json`, `r1_slots.json`, `r1_planning_release.json` and `registration_receipt.json`; `plan_tree.json`, `collection_plan.json` and the 16 episode stage files with their 2 order manifests; and `night_plan.template.json`. `w1_plan.json` and the derived `sizing_b5.json` will be added. Is anything beyond these, plus the existing registration set, owed on the published list?

## 8. NEEDS_LEAD decisions

- **L1 (F-1).** DONE: #944 merged #813 (`bef3ea87c`); RL-206 accepts the text.
- **L2 (§3).** DONE: PR #959. Originally: give the #809 W1 port a PR of its own (scaffold `09b1ddbd5`, the host-command union and the W1-only fixture, plus the Part C paths at the accepted head). Without one, "each PR's accepted diff" has nothing to compare against for those paths.
- **L3 (F-4b).** RULED RL-207 (complete the policy; the lead fills it at §9 step 1). Originally: choose how `heavy`, `per_turn`, `sensors.r0_sha256` and `fan_keys` enter: an `inputs.json` completion or a code change. Q2 goes to Fable first.
- **L4 (F-3).** DONE on PR #886 (`1dbcb4dd5`, `8fc76a0b9`). CI 45340766338 is green, 21/21.
- **L5 (F-6).** DONE per RL-208 (PR #959 `fbe696ca1`). Originally: dispose the 5 refusal sites, 2 guards and 2 scope gaps in `hazard_refusals.json`.
- **L6 (F-7).** DONE: PR #959 `ca41d5477`.
- **L7 (RL-193 §7).** DONE in trial per RL-212 (`e2cf3ca00`).
- **L8 (F-9).** DONE: §9 (RL-210 confirms).
- **L9 (F-13).** RULED RL-209 (v3.2, run direct); the ordinary-shard half is DONE in PR #959 `2b7620b9a`. Originally: choose how the frozen suite runs on the W1 line: the v3.2 fixture, or the raw file excluded from ordinary shards with the 16-shard workflow as the gate.
- **L10 (F-11, F-12).** #839's fix DONE (`a37a3462b`). Record the cause of #826's TERM test.

## 9. Promotion runbook: the final steps, in order (lead L8)

Lead decision L8 (2026-11-23 21:45) fixes the order of the last four steps:
**final regeneration (including the R0 binding) → step 4 (three-blob check) →
receipt → signing.** The reason is F-9. Every kit regeneration rewrites
`collection_plan.json`, one of the three step-4 blobs, and binding R0
regenerates the kit (with a synthetic digest, the probe rewrote 20 kit files).
So step 4 can only be valid after the last regeneration. A step-4 export made
earlier is never reused. RL-210 confirms this. Step 4 runs after the last regeneration that can move
`collection_plan.json`: after the R0 binding, after RL-207's completion and after the committed `w1_plan.json`. Step 5 uses
the same exporter and follows the same rule. `selection.json` stays the blob committed before any energy was
read.

**Before step 1.** Every component is accepted at a named head:
- #826, #839 (`a37a3462b`) and #831;
- #944, which now carries #813 (`bef3ea87c`, L1);
- #886 (L4), #904, and the port PR #959 (L2, PR #809's accepted head).

Assemble on the PIN by merges in RL-193 §3 order, the port last, exactly as
this trial does. After every merge, the ten-blob check must give 10/10
(`tools/ten.sh`). RL-207 to RL-212 have ruled L3, L5, L7 and L9. Still open before step 1:
- #809's accepted head, with the port refreshed to it;
- v3.2 issued and adopted, with zero FALSE_PASS, WRONG_VERDICT and HARNESS_ERROR on v3.2 run directly, every shard reporting (RL-209);
- #824 admitted and the authorized R0 digest named (RL-207's missing fact);
- RL-212's clause commit repeated after #813 and #944.

1. **Final regeneration, including the R0 binding (lead).** On the assembled
   tree, run every step below in one go and commit the result as the
   candidate head. Run nothing with `GIT_DIR` or `GIT_WORK_TREE` exported
   (F-10).
   1. Bind `R0.record_sha256` to the authorized R0 record's digest, equal to
      `thermal_policy.sensors.r0_sha256` (RL-193 item 6).
   2. Complete `thermal_policy` per RL-207: `heavy: true`, `per_turn: true`,
      `sensors.fan_keys` equal to `r1_runtime.json`'s list, and
      `sensors.r0_sha256` equal to `R0.record_sha256`. DEC2's five leaves stay
      unchanged.
   3. Commit `w1_plan.json`, the filled `night_plan.template.json`.
   4. Regenerate:
      - the kit: `python3.13 -B scripts/align_v4_kit.py` writes `inputs.json`'s derived files, `identity_pins.json`, `plan_tree.json`, `collection_plan.json`, the 16 stage files with their 2 order manifests, and `sizing_b5.json`;
      - the template bindings: `python3.13 -B scripts/validate_align_v4_w1_plan.py --regenerate-template`;
      - the dynamic closure trace: `python3.13 -B scripts/align_v4_dynamic_trace.py`, committed only if every scenario is `ok: true`.
   5. Run the refusal census and the reader census. Both must pass at this
      head.
   6. `python3.13 -B scripts/align_v4_kit.py --check` must exit 0.
   7. Exact-tree CI on this head, all suites, including the 16-shard
      `partc-frozen-differential` workflow.
2. **Step 4: the RL-184 §4 three-blob check (lead and magistrate).** Run it
   once, at the candidate head or at a commit blob-equal to it on the three
   blobs: the exporter, the selection and `collection_plan.json`. Use #839's
   fixed W1-BLOCKERS block (`a37a3462b`). If any blob differs from the
   signing commit, go back to step 1. The MBP steps that need the final kit
   run on this same head: U3, WP19 and the two protected Part C replays
   (§6.2).
3. **Receipt (lead).** On the candidate head, fill
   `registration_receipt.json`'s STRICT artifact digests. These include the
   rows added since the pin: `rl176.py` and `rl176_phases.py` (#813), and
   `scripts/align_r1_part_c_evidence.py` (F-8, PR #959). Bind the
   reader-census module and its evidence (RL-193 item 5). Attach the ten-blob
   and accepted-diff proof (item 7) and the published file list (item 8).
   The file list follows RL-211: the trial's files plus its five groups, one
   row per file with key names only. `r1_planning_release.json` is now in
   `ARTIFACTS` (PR #959 `df018026d`).
   The receipt is the only file that changes after step 1. Any other change
   sends the run back to step 1.
4. **Signing.** The lead signs the receipt STRICT at the final pin. Then
   comes Fable's W1 cold pass on the promoted candidate (RL-193 item 9).
   E3's install-only rehearsal follows promotion (§6.3).

## 10. Reproduce

The seat directory is `/Volumes/JW-EXT/scratch/opus-w1-trial-assembly-1123/`:
- `merge-log.tsv`: each step's commit, tree and ten-blob result.
- `tools/ten.sh <rev>`: the ten-blob comparison.
- `tools/accepted.py <rev> [trial-written paths]`: the accepted-diff proof.
- `regen/`: kit, probe, template, census, trace and test outputs.

Run from a checkout whose git metadata is reachable, **without** `GIT_DIR` exported (F-10):

```sh
python3.13 -B scripts/align_v4_kit.py && git status --short        # expect no change
python3.13 -B scripts/align_v4_kit.py --check                      # expect the R0 refusal (F-4a)
python3.13 -B scripts/validate_align_v4_w1_plan.py --regenerate-template && git status --short
python3.13 -B -m tests.hazards.refusal_census                      # F-6
python3.13 -B /Volumes/JW-EXT/scratch/d-w1-signing-reader-census/run_census.py --repo . --rev "$(git rev-parse HEAD)" --signing-head
```
