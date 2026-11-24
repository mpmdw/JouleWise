# cl-ctl-01 issue path — 2026-11-22

**Current authority.** RL-197b admits the kit-v1.1 route. The final section below supersedes the earlier main-only plan and its pre-ruling assessment.

**Status:** ready for cold review as a data draft. Issue awaits the landed runner and queue-authority guard pin, the independent cold kit PASS and the lead's standing-ladder item. The MBP work belongs to the magistrate in a quiet session. This seat used public code, rulings, metadata and synthetic inputs only.

Mission M0 selected the lead's explicit [AGENT] task. The audit checkout started clean at RL-197, `1de85b0c1`, with no remote issue-path branch or PR. It fast-forwarded through RL-197a at `75526ed44` to RL-198 at `0a4d9d3cf`. The audit pointer was item 513 and the main pointer was item 531 when checked. Both kernels had no active stop card. Main items 532–533 authorize option C before W1. RL-198 §0 and §3.3 place it in separate P windows and preserve RL-197's ctl-01 kit, issue order and look. Main item 365 records dev-02 complete, satisfying RL-149 §2.5's predecessor.

## Merge plan for the lead

Snapshot against `main@82b93c157`. The common ancestor with `align/2026-11-14-kit-v1-1@6e9d42f1d` is `d842f697f`. Main is 1,831 commits ahead and the kit line is 1,634 commits ahead on its side. The kit line includes PR #812 (the qualification/t0 guard) at `6e9d42f1d`, but it contains neither ctl PR. PR #808's head `1f8541e4b` is 12 commits past that base. PR #900's head `9bb03a741` is another three commits on top. Both PRs are draft with 21 passing substantive checks each on those heads and are reported MERGE_READY on their present bases. Main has none of `joulewise/cadence/`, `scripts/cadence_legs_runner.py` or `scripts/launch_cadence_span.py`, and lacks the pinned ALIGN R1 runtime, endpoint and registration inputs. A direct retarget of PR #808 currently shows 3,559 files relative to its merge base with main.

1. First land a scoped cadence prerequisite PR **into `main`**, based on current main. Bring the RL-145 ALIGN runtime/registration and host integration needed by the cadence runner, then the campaign runner from PR #775 (`8bd31ae5a`), kit v1.1/span-reference layer from PR #788 (`9cbb365a6` before the qualification merge), and the qualification/recorded-t0 fixes already integrated by PR #812. Use `6e9d42f1d` as the comparison baseline for the combined closure. PR #775 currently targets `align/2026-11-13-rl145-build` and PR #788 targets `align/2026-11-14-campaign-runner`. Integrating a narrow prerequisite PR avoids promoting the divergent ALIGN tree or its unrelated W1 changes. Check the import and frozen-path closure and compatibility with current main, then get the integrated tree through the full suite. This port remains lead work.
2. Rebase **PR #808** from old base `6e9d42f1d` onto the main commit containing the prerequisite, retarget it to **`main`**, and land it first. Review the new diff against the original ctl delta and re-run the required full-tier checks and the independent executing gate on the final main-bound head. The queue-authority follow-up refreshes the old instrument-read wording in the runner instructions and draft refusal.
3. Rebase **PR #900** from its old base `1f8541e4b` onto main **after PR #808 lands**, retarget it to **`main`**, and land it second. Keep the old #808 head available until the #900 rebase and verify that the new #900 diff contains only its failed-envelope follow-up. Retaking the three-commit delta works even if #808 is squashed. Use fresh main gate ledgers for both PRs with the six Impact answers and five evidence rows. Keep the reviewed heads tied to their CI and executing audit evidence.
4. After PR #900, rebase the queue-authority delta in [PR #946](https://github.com/mpmdw/JouleWise/pull/946) from `9bb03a741` onto main, retarget it to **`main`**, and land it after its executing audit and final-head gates. Pin the kit to the **actual main commit containing all three**. `043b972f9` was the review pin before the RL-197b projection below. Earlier stacked heads lack at least one required delta. At the selected main pin, regenerate frozen digests with `scripts/cadence_legs_runner.py pin-kit KIT --commit MAIN_SHA --write`, verify the frozen bytes with `scripts/cadence_queue.py validate-kit KIT --repo RUNNER_CHECKOUT --batch-window 02:00-02:35`, and take new kit, index and queue hashes. Compare the pinned payload to the cold-reviewed draft. After the independent cold seat passes on the layout, capture/consumer balance and bytes, the lead sets `status: issued` and `ruling.authorizes_spans: true` in the final kit. Validate those final bytes before hashing and binding them in the index and authorized queues.

**Measurement dependencies on PR #795:** none. The look depends on #795 through freeze 2 and the instrument read. There is no #795 dependency in the ctl runner/kit stack.

PR metadata: [#775](https://github.com/mpmdw/JouleWise/pull/775), [#788](https://github.com/mpmdw/JouleWise/pull/788), [#812](https://github.com/mpmdw/JouleWise/pull/812), [#808](https://github.com/mpmdw/JouleWise/pull/808), [#900](https://github.com/mpmdw/JouleWise/pull/900).

## Kit and queues

The [review kit](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/ctl-01/kits/cl-ctl-01.draft.json) uses the runner's `ctl.generate_legs` and `pin-kit` tooling. The [KITS.json row](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/ctl-01/KITS.json), [pilot queue](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/ctl-01/queues/ctl-01-s01.draft.json) and [span 2 queue](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/ctl-01/queues/ctl-01-s02.draft.json) name the same draft bytes. The current review kit and its hash are in the RL-197b section below. The kit is `draft` with `authorizes_spans: false`. Each queue is halted with a review-only date and expiry and contains just one span. The lead sets the actual finite expiry, earliest local date and standing notice at issue. For the active span 2 queue, the lead also sets `pilot_pass_sha256` on its selected row after the hand-read. Separate queues keep the generic queue reader from chaining through the hand gate.

The master seed is `2026111601` with `sha256-scripts-v1`, band q0 and free t0. Each leg has a 2,000-token prefill setting and 600 s sampled recovery. Hidden decoding follows G0 and precedes the visible call. CPU legs use one core between the two visible calls. The split has two 60 s gaps. Its matched plain leg has the same prompt, seed, total count and span reference. Native calls may end at different context depths.

| Leg | Script | Visible caps | Leg seed | Reference |
| --- | --- | --- | ---: | --- |
| L001 | Extra turn | 1,024 + 1,024 | 2492371355 | Capture |
| L002 | Hidden 512 | 1,024 | 3901590846 | L001 |
| L003 | CPU 30 s | 512 + 512 | 4008811407 | L001 |
| L004 | CPU 90 s | 512 + 512 | 1386543436 | Capture |
| L005 | Hidden 128 | 1,024 | 92817822 | L004 |
| L006 | Split | 342 + 341 + 341 | 603567892 | L004 |
| L007 | Matched plain | 1,024 | 603567892 | L004 |
| L008 | Hidden 256 | 1,024 | 3928512548 | L004 |
| L009 | Hidden 512 | 1,024 | 800711026 | L004 |
| L010 | CPU 10 s | 512 + 512 | 2927643913 | L004 |
| L011 | Hidden 256 | 1,024 | 3745194143 | L004 |
| L012 | Hidden 128 | 1,024 | 807871911 | L004 |

The seed law places a capture-capable script first in each span. The runner assigns that first leg the capture role. L003 and L010 are CPU consumers under the actual positional rule. The cold seat should check that layout explicitly. [`ctl.py:114`](https://github.com/mpmdw/JouleWise/blob/9bb03a74147831d427007560a98af6ef9673700d/joulewise/cadence/ctl.py#L114-L135), [`legs.py:221`](https://github.com/mpmdw/JouleWise/blob/9bb03a74147831d427007560a98af6ef9673700d/joulewise/cadence/legs.py#L221-L236).

- **Gap and recovery.** The plan forwards each kit leg's `script`. `CtlSegment.run_member` installs it for the child. `script_steps` reads `gap_s` between turns and `recovery_s` after the last turn. The endpoint executes both as in-member timed intervals. [`legs.py:233`](https://github.com/mpmdw/JouleWise/blob/9bb03a74147831d427007560a98af6ef9673700d/joulewise/cadence/legs.py#L233-L236), [`cadence_ctl.py:184`](https://github.com/mpmdw/JouleWise/blob/9bb03a74147831d427007560a98af6ef9673700d/joulewise/align/apple/cadence_ctl.py#L184-L190), [`ctl.py:38`](https://github.com/mpmdw/JouleWise/blob/9bb03a74147831d427007560a98af6ef9673700d/joulewise/cadence/ctl.py#L38-L47), [`cadence_ctl.py:76`](https://github.com/mpmdw/JouleWise/blob/9bb03a74147831d427007560a98af6ef9673700d/joulewise/align/apple/cadence_ctl.py#L76-L93), [`cadence_ctl.py:115`](https://github.com/mpmdw/JouleWise/blob/9bb03a74147831d427007560a98af6ef9673700d/joulewise/align/apple/cadence_ctl.py#L115-L132).
- **Prefill.** The generator copies `leg_defaults.prefill_tokens` into each leg. The plan maps that setting to the existing StepTask character budget (4,111 for 2,000). The member passes the budget into the task factory. The realized tokenizer count is recorded by the endpoint. [`ctl.py:133`](https://github.com/mpmdw/JouleWise/blob/9bb03a74147831d427007560a98af6ef9673700d/joulewise/cadence/ctl.py#L133-L135), [`legs.py:108`](https://github.com/mpmdw/JouleWise/blob/9bb03a74147831d427007560a98af6ef9673700d/joulewise/cadence/legs.py#L108-L110), [`legs.py:221`](https://github.com/mpmdw/JouleWise/blob/9bb03a74147831d427007560a98af6ef9673700d/joulewise/cadence/legs.py#L221-L229), [`cadence_leg.py:176`](https://github.com/mpmdw/JouleWise/blob/9bb03a74147831d427007560a98af6ef9673700d/joulewise/align/apple/cadence_leg.py#L176-L194), [`r1_runtime.py:820`](https://github.com/mpmdw/JouleWise/blob/9bb03a74147831d427007560a98af6ef9673700d/joulewise/align/apple/r1_runtime.py#L820-L827).

## Drafts for typed RUN_STATE items

Use the three RL-197c typed drafts in the final section. They supersede the original span drafts here. The independent hand-read item and shared start-check below apply to those updated items. Fill in angle-bracket values and post through `scripts/run_state_add.py add`. Supply each pointer as its own file after substituting the exact record, item, and offset-bearing deadline. Keep the arm record and operational details in the authorized lead/magistrate channels.

### 1. Issue the counted pilot L001–L003

**Heading** — MAGISTRATE — cl-ctl-01 counted pilot L001–L003, RL-197, cq-ctl-01-s01-a1

**Typed fields** — owner `magistrate`, status `ISSUED`, expiry `<finite issue expiry>`.

```text
owner: magistrate
wait: result_json_exists
deadline: <follow-up deadline at or after the planned launch fence>
on_early_or_refused: Read the verdict first. On refusal, fault or unproven close, hold cl-ctl-01 and notify the lead. On missing receipt at deadline, notify the lead and infer no success. Continue the standing ladder at the next eligible clean close.
next_observable: <exact runner_receipt.json location> for cq-ctl-01-s01-a1 and the clean-close check under item {{self}}.
```

> Run only L001,L002,L003 on `<main runner SHA>`, using `<issued kit path, full SHA-256>` and `<pilot queue path, full SHA-256, expiry>` at standing rank `<lead-assigned rank>`. Runner review and final main CI are `<references>`. Independent kit cold PASS is `<reference>`. Dev-02 is closed (item 365). This is the registered counted pilot and first native run of the pin under F-11. Use a fresh soak. L001 captures and L002–L003 consume. Run the shared start-check. Launch once as the final act of a quiet activation. At close verify the receipt, restore and stop evidence, accounting, first consumer release and the automatic desk. Make the authorized copy and record its proof. Hold cl-ctl-01 span 2 for the independent pilot hand-read. If the launch record has no LAUNCH_RC, treat the attempt as unspent and rerun start-check before reissue.

### 2. Assign the independent pilot hand-read

**Heading** — Independent F-3(c) and RL-197 hand-read of cl-ctl-01 pilot L001–L003

**Typed fields** — owner `lead`, status `ISSUED`, expiry `<hand-read deadline>`.

```text
owner: lead
wait: ruling_recorded
deadline: <hand-read deadline>
on_early_or_refused: Record the failed or missing check, hold span 2 and return any failed view check to the research lead. Other eligible rungs remain available at a clean close.
next_observable: <independent signed PASS or HOLD record> for cq-ctl-01-s01-a1 and the pilot close of item <pilot item>.
```

> Assign an independent seat after the ledger bootstrap ruling, the issued pilot's proven close and automatic desk PASS. Run the usual F-3(c) hand table and Q1 checks from the authorized template. Bind the read to that pilot's actual attempt ID, issued kit digest and immutable receipt digest. Verify the close-bound source and use the allowlisted projection. For every admitted pilot leg L001–L003, take the visible calls from the bound script record plus the one logged envelope and episode/G0 bounds. This addition reads stamps and counts only.
>
> 1. The sums of visible delivered tokens and visible starting context tokens agree with the envelope's respective decode and total prompt counts. Compare the full prompt total with the logged cached-plus-fresh total if represented separately. Hidden calls contribute zero to the envelope sums.
> 2. The first visible start and first-token stamps equal the envelope's two stamps exactly. A 1 ns difference is `envelope_stamps`.
> 3. Scripted steps occur in the planned order, do not overlap and fit within the episode after G0. A first step may begin at the G0 end (RL-197a §5).
> 4. The recovery end is at or before the episode end.
>
> Keep a PASS/HOLD row and reason for each check on each of L001, L002 and L003, with the source digests, seat and signature. For PASS, the independent seat prepares the private `joulewise.cadence_ctl_pilot_pass.v1` record with `status: PASS`, `reviewer`, `kit_sha256`, `pilot_plan_id` and `pilot_receipt_sha256`. The lead authenticates the reviewer and binds the PASS bytes in the issued span 2 queue. An intervening span can be the latest predecessor. The PASS must still bind the latest pilot for the issued kit. An absent or non-evaluable pilot leg cannot establish PASS. A failed check holds span 2, is never repaired, and returns to the research lead. Keep readings and per-leg evidence in the authorized records. The lead posts the gate disposition and reference.

### 3. Issue span 2 L004–L012

**Heading** — MAGISTRATE — cl-ctl-01 span 2 L004–L012 after counted-pilot hand PASS, cq-ctl-01-s02-a1

**Typed fields** — owner `magistrate`, status `ISSUED`, expiry `<finite issue expiry>`.

```text
owner: magistrate
wait: result_json_exists
deadline: <follow-up deadline at or after the planned launch fence>
on_early_or_refused: Read the verdict first. On refusal, fault or unproven close, hold cl-ctl-01 and notify the lead. On missing receipt at deadline, notify the lead and infer no success. Continue the standing ladder at the next eligible clean close.
next_observable: <exact runner_receipt.json location> for cq-ctl-01-s02-a1 and the clean-close check under item {{self}}.
```

> Pilot close, automatic desk and independent F-3(c)/RL-197 hand-read are PASS at `<record links>`. Keep the same `<main runner SHA and issued kit SHA-256>`. Select `<span 2 queue path, full SHA-256, expiry>` at `<lead-assigned rank>`. Run only L004 through L012 with a fresh soak and L004 capture. Keep L006/L007 adjacent under this reference. Run the shared start-check and launch once as the final act of a quiet activation. At close verify the receipt, restore/stop and desk, make the authorized copy and record its proof, and account for all twelve scheduled legs. The independent first-split hand-read is owed on L006 before the look and holds no other span. Once the last span closes and the block's close accounting is recorded, the lead enters the blind deviation sentence before the look. Use RL-190 §3.7 as amended by RL-198: it begins “The ctl-01 block was run.” and retains the rest of the disclosure. The series' K disclosure follows RL-198 §4.1.

### Shared Start and check

1. Verify RL-197 values, the full commit admitted under RL-197b after PRs #808, #900 and #946 land, the kit cold PASS for the issued digest, issued authorization and full frozen digests. Verify the finite queue SHA-256, the selected row's exact kit SHA-256 and roster, attempt, actual t0, expiry and standing rank. For span 2, bind the signed PASS digest in `pilot_pass_sha256`. Verify its kit, pilot plan and clean-close digest. Use the same elapsed, calendar and deadline policy as the standing ladder.
2. Prove the latest actual predecessor from `launch_cadence_span.py close-proof --attempt-ledger <shared ledger>`. Verify latest receipt, restoration readback, stopped feeds, absent process groups and no foreign process. In the magistrate lane supply `HOST_RESTORE_OK`, `FEEDS_STOPPED`, `GROUPS_ABSENT`, `FOREIGN_PROCESSES_ABSENT` and `CLOSE_PROOF_RECEIPT` per the runner's published contract. Record the proof's exact nanosecond bound. RL-179 row 4 starts after proven close. The span-2 launch uses the true latest predecessor even if a different authorized rung ran after the pilot.
3. On the actual t0, run the kit checklist with the validated queue's `--kit-sha256` and verify host and launch observations. Check no stop card, halt, veto, orphaned workload, conflicting agent or launch fence. Prove fit before the next higher rank and any applicable blackout. Include the full idle-soak interval against 02:00–02:35 under item 507 and apply the batch argument required at actual t0. If it does not fit, cede without spending. Supply `--queue`, `--queue-sha256`, `--queue-kits-root`, the exact queue plan ID as `--span-id`, the selected roster as `--legs`, and the selected kit digest as `--kit-sha256`. Include `--attempt-ledger`, `--previous-close-receipt` and `--t0-not-before-ns`. Supply `--pilot-hand-read` for span 2. The launcher re-proves the latest close and rechecks queue authority under lock. Before recording the attempt, it verifies the actual `--repo` is the checkout root at the kit's frozen HEAD, with a clean tree and matching frozen files. The agent-free child checks the published attempt before production setup. Both `next` and launch treat expiry as exclusive. Allow enough time through agent-free startup.
4. **Look reservation check, separate from the two measurement items.** The kit eligibility test ends with its measurement gates. For the one `lm-ctl-01` look, require the instrument read, both matched `hold.json` and `edges.json` hashes, the bytes ruling, and release prerequisites below. A `ctl01_withheld` row refuses the reservation and returns to the research lead. Use the first applicable reason in order `no_dc_in_floor`, `no_prefill_size`, `dose_under_floor_at_k2`. The row has no `value` key. The V2 `issue` callback denotes reservation eligibility. If the roster has qualified sizes but lacks 2,000, use the ruled `prefill_unmatched` caption. If the later read would raise the doses, record that disposition, keep the twelve legs as measured and return any proposed additional legs to the research lead.

## Remaining look gates

- **Print PR #853** needs the frozen V2 suite at 837/837 (brief baseline 422/837), its approved additions under RL-197a, the executing independent audit and merge. Ordinary PR CI is distinct from V2. [Print PR](https://github.com/mpmdw/JouleWise/pull/853)
- **Hand vectors** are the independent Opus oracle's nine vectors. RL-197a requires four edits by Opus or the lead, then verifier re-run and three file hashes. The print builder reproduces the final vectors, with any disagreement sent to the research lead.
- **`lm-inst-01`** waits for freeze 2 through PR #795 and the executor under PR #868. The research lead records the counterfactual sizing result and the two input hashes. [PR #795](https://github.com/mpmdw/JouleWise/pull/795) · [PR #868](https://github.com/mpmdw/JouleWise/pull/868)
- **Route and manifest** need `lm-ctl-01`, both schemas, and the closed `controls` route row in one PR under RL-187. The research lead's bytes ruling then binds the manifest, code/schema/route and hand-vector evidence plus both instrument hashes. Final close, blind disclosure and first-split read precede one Stage 1/reservation/run on the bound host.

## Verification and NEEDS_SPEC

- Draft kit regenerated from the original kit with `ctl.generate_legs` and `pin_kit`. `validate-kit --repo --batch-window 02:00-02:35` passed at `043b972f9`, including frozen-file hashes.
- Both one-span `validate-queue --kits-root` checks passed. `next` returned `halt` for each. Both exact rosters passed the runner's static plan with the 02:00–02:35 window. Pilot expected / worst-case 8,382 / 16,350 s. Span 2 expected / worst-case 19,481 / 36,150 s. These are estimates. At issue use the actual t0, runner-emitted launch deadline and the standing ladder.
- Both exact-kit CLI mocks closed with exit 0, 3 and 9 legs respectively, and zero stops. They used fake legs.
- The exact-kit assertions checked the index hash, seed law, span holds, capture assignment and split pair. Changing the three inputs independently in an in-memory fixture propagated to the planned intervals and prompt budget. All three typed pointer templates parsed with synthetic witnesses and deadlines.
- The read-only fixture orphan census could not run because this session's `ps` invocation was denied. No native launch was attempted.
- The change is review-only kit data and documentation on the audit branch. The full suite for the integrated main runtime remains part of the lead's merge gate. Native behavior remains PROVISIONAL pending the counted pilot and hand-read.
- **NEEDS_SPEC:** none for RL-197 kit inputs or issue order. A failed pilot view check, any withheld reservation, or the read's counterfactual dose raise returns to the research lead as RL-197 directs.

## Audit round 1 disposition

The executing audit reproduced one HIGH with three paths to bootstrap on `0ac451c17`: absent pilot PASS, a plan ID paired with another span's roster, and expiry between selection and launch. PR #946 at `5766e346c` binds the approved queue to the exact launcher invocation and published attempt. The lock-time guard checks the queue again before recording the attempt. The independent PASS is pinned by the lead and binds the current kit and its latest pilot receipt. The child rechecks the same queue and pilot evidence before production setup.

| Reproduction | Executable regression | Result |
| --- | --- | --- |
| Active span 2 with missing or invalid pilot PASS | `test_ctl_span_two_requires_exact_pilot_pass_and_accepts_valid_proof_after_intervening_span` | PASS |
| Pilot ID with the nine-leg roster, or span 2 ID with the three-leg roster | `test_ctl_rejects_both_roster_swaps_before_recording_attempt` | PASS |
| Queue expired at launch, including after selection while proving the previous close | `test_ctl_rejects_expired_queue_at_selection_and_after_close` | PASS |

The same tests reject substituted queue and PASS files at the child. The 27-test focused launcher and queue suite passed. The two LOW observations confirmed the kit and merge plan. The regenerated draft preserves doses, durations, prompt size, seed and order and pins the guard candidate. The authenticated PASS record and actual close receipts belong in authorized operational storage.

## Audit round 2 disposition

Runner PR #946 at `fae29cf50` closes L1 and L2. A passing checklist can describe the right checkout while the launch command names a stale one. Under the desk lock the launcher now verifies the actual `--repo` before writing a ledger-backed attempt or publishing a fence. It compares HEAD with the kit pin, hashes every frozen file in that checkout and checks Git status for staged, unstaged and untracked changes. The same check runs for qualification and ctl launches that record attempts. The queue's shared expiry predicate treats the instant of `expires_at` as expired in both `next` and the launcher.

| Case | Regression | Result |
| --- | --- | --- |
| Passing checklist followed by a stale `--repo` | `test_audit_round_two_wrong_checkout_refuses_after_passing_checklist` | PASS |
| Different HEAD with identical frozen files | `test_ctl_refuses_wrong_head_with_identical_frozen_files` | PASS |
| Dirty checkout with unchanged frozen files | `test_ctl_refuses_dirty_tree_with_unchanged_frozen_files` | PASS |
| Changed frozen file hidden from Git status | `test_ctl_refuses_changed_frozen_file_even_when_git_status_is_clean` | PASS |
| Exact expiry instant | `test_next_and_ctl_launch_agree_at_exclusive_expiry` | PASS |

Each checkout refusal preserved the original attempt ledger and left the prior close provable. The 54 focused tests passed, including the qualification launch gate and the prior ctl authority regressions.

## Audit round 3 disposition

PR #946 at `043b972f9` re-reads and hashes both the kit and the queue under the desk lock immediately before recording the attempt. Both must match their approved digests. The named regression `test_audit_round_three_kit_and_queue_changes_refuse_before_recording_attempt` passed for the audit's reformatted kit while launch waited for the lock, a kit change after checkout verification, and a queue change after its earlier lock-time read. All three refusals preserved the ledger byte for byte, left the prior close provable, and reached neither fence publication nor bootstrap. All 55 focused tests passed.

## Fast-route assessment — same-line merge and MBP pin

Sources are `RESEARCH-LEAD-DECISIONS.md` on `origin/audit/2026-11-10-fable@4bd044268` and `RUN_STATE.md` on `origin/main@9c782c6ed`. Runner line numbers are at PR #946 head `043b972f9` unless a different pin is named.

### 1. Which rule requires main?

**RL-197 specifically requires the ctl-01 runner on main before issue.** Its heading says the kit may issue once the runner is on main and the cold seat passes. Section 1 step 1 names #808 and #900 on main, and step 5 explicitly waits on step 1 and the cold seat. The §1 dependency resolves any ambiguity in the heading. RL-198 preserves RL-197's order while amending the disclosure and option-C language. Publishing the reviewed runner on main is the issue gate. RL-197 predates #946, whose guard is part of the corrected runner's executed path. The MBP can still check out a detached exact SHA. [RL-197 heading](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L23816) · [RL-197 §1, steps 1 and 5](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L23847-L23860) · [RL-198 amendments](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L24367-L24372)

General pin admission permits a reviewed lane pin. RL-144 terms 2–3 distinguish lane merges from event gates: the event needs a green full suite on the named commit or an identical full tree. RL-149 §2.8 lines 1–2 require the independent kit review, frozen-commit validation and a green full suite. RL-179 F-6 and register rows 4–10 work from admitted pin, kit and queue identities, clean close, native smoke and hand-read. Row 11 reserves Part C for W1-line pin changes. RL-145 §5–6 governs the R1 follow-up and W1 signing/smoke chain. It imposes no general main gate for campaign runner code. The executing independent top-tier seat for this ctl runner is RL-174 B.4 as amended by RL-186 §2.6. [RL-144 terms 2–3](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L10232-L10236) · [RL-145 §5–6](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L10529-L10578) · [RL-149 §2.8](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L12639-L12659) · [RL-179 F-6](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18774-L18777) · [RL-179 rows 4–11](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18911-L18918) · [RL-186 §2.6](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21391-L21396)

Pin B is a real precedent for admission off main. RL-183 §2.8 accepts qualification on its own branch and §2.9 names its first native smoke. RUN_STATE item 434 admits #812's merge `6e9d42f1d` on kit-v1.1 with 38 reviewed frozen paths and green CI. Item 444 records the first native hand-read PASS. Items 463–464 distinguish pin A (`2d347f721`, kits 01–14) and pin B (`6e9d42f1d`, kits 15–16), and item 536 keeps those pins in service. RL-200 §3 and item 536 put ctl-01 ahead of rank-4 stability **once admitted and ready**, leaving its admission gate in force. [RL-183 §2.8–2.9](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20274-L20292) · [RUN_STATE 434](https://github.com/mpmdw/JouleWise/blob/9c782c6eda0661247ef1c98268a4afd775e2e6dc/RUN_STATE.md#L3527-L3548) · [RUN_STATE 444](https://github.com/mpmdw/JouleWise/blob/9c782c6eda0661247ef1c98268a4afd775e2e6dc/RUN_STATE.md#L3301-L3305) · [RUN_STATE 463–464](https://github.com/mpmdw/JouleWise/blob/9c782c6eda0661247ef1c98268a4afd775e2e6dc/RUN_STATE.md#L2833-L2853) · [RL-200 §3](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L24629-L24637) · [RUN_STATE 536](https://github.com/mpmdw/JouleWise/blob/9c782c6eda0661247ef1c98268a4afd775e2e6dc/RUN_STATE.md#L1131-L1156)

### 2. Would the lane commit pass the validators and recorded-t0 guards?

**The checkout location is technically viable. The current candidate is ineligible for pin admission because its full CI is red.** The actual ancestry is `6e9d42f1d → 1f8541e4b (#808) → 9bb03a741 (#900) → 043b972f9 (#946)`. With stable heads and merge commits that preserve that ancestry, the staged lane merges can yield the same tree as the final reviewed #946 head. Compare full tree hashes after merging. Any different tree needs its own full run and review of the delta.

- **Kit and queue checks passed on the existing lane candidate.** The read-only `validate-kit --repo` verified all 40 frozen paths for the draft at `043b972f9`. Both queue validators passed. The same CLI validated the three `cl-qual-01..03` kits against their unchanged pin B. `validate-kit` checks Git objects at the kit SHA, and production independently checks the actual checkout root, HEAD, working-tree digests and cleanliness. Re-pin the kit and re-hash both queues to the actual final merge SHA even if its tree is identical. Keep existing pin-A and pin-B kits at their own named SHAs. [`cadence_queue.py:47`](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/scripts/cadence_queue.py#L47-L57) · [`kit.py:417`](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/joulewise/cadence/kit.py#L417) · [`cadence_legs_runner.py:331`](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/scripts/cadence_legs_runner.py#L331-L364)
- **The qualification branch and its clock checks are still present.** `qual_roster_problems` checks the qualification law and type-L pairs. The runner retains the date, earliest start, exclusive cutoff and sleep-inclusive anchor for qualification. Ctl-01 instead has the ruled free t0 and requires the exact predecessor close in nanoseconds plus the launcher's clock anchor. The same start predicate checks the wall reading and both ends of the projected interval. The launcher also binds the queue, selected attempt, roster, kit and, for span 2, the pilot PASS. [RL-186 §2.5](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21383-L21389) · [`cadence_queue.py:113`](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/scripts/cadence_queue.py#L113-L147) · [`cadence_legs_runner.py:439`](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/scripts/cadence_legs_runner.py#L439-L484) · [`launch_cadence_span.py:459`](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/scripts/launch_cadence_span.py#L459-L489)
- **A generic hosted launch test still fails on #946.** CI shows 20 successful substantive checks and one failing shard. `test_launch_ledger_records_attempt_even_if_bootstrap_fails` uses `launch_files`, which mocks the shared `subprocess.run` with the synthetic bootstrap failure. The new checkout verification hits that failure on `git rev-parse` before bootstrap. The fixture also needs an actual matching checkout for its kit. Repair the fixture, then obtain the full green suite for the final tree. The focused passes do not satisfy line 2. [`test_legs_runner.py:911`](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/tests/cadence/test_legs_runner.py#L911-L970) · [Failed shard](https://github.com/mpmdw/JouleWise/actions/runs/45002648202/job/137147512134)
- **The latest predecessor needs a compatible native receipt.** `proven_close` requires the receipt's embedded `span_id` to match the latest ledger attempt, plus restore and shutdown proof and an exact close bound. Pin A's runner does not emit `span_id`. Pin B emits it when supplied. RUN_STATE item 539 records the current ladder on pin A, so a direct handoff from an ordinary pin-A close refuses, whichever branch the new runner is on. RL-200a's seven-part identity fallback applies to stability Stage 1. It does not change the launcher. The lead must arrange a genuinely latest, compatible close with an authoritative ledger entry, or get a reviewed compatibility rule and implementation. Keep the receipts immutable. [`launch_cadence_span.py:220`](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/scripts/launch_cadence_span.py#L220-L258) · [Pin A receipt writer](https://github.com/mpmdw/JouleWise/blob/2d347f721552fe03bdd19f113e7bad7a7c24908e/scripts/cadence_legs_runner.py#L550-L563) · [Pin B receipt identity](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L448-L455) · [RL-200a §2](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L24681-L24698) · [RUN_STATE 539](https://github.com/mpmdw/JouleWise/blob/9c782c6eda0661247ef1c98268a4afd775e2e6dc/RUN_STATE.md#L1055)

### 3. Which executable dependencies are only on main?

**None found.** The candidate is a descendant of #812. The base already contains the R1 runtime, endpoint, registration inputs, LaunchAgent wrapper and close/host helpers. The launcher and runtime imports resolve within that tree. The launcher constructs the child invocation from `args.repo / RUNNER`; the child dispatches to the lane's cadence runtime. The audit kit and queue are separately staged inputs. Main's typed issue and standing ladder provide operational authority. PR #795 is a dependency of `lm-inst-01` through freeze 2 and thus of the look, as RL-197 §1 distinguishes. [`launch_cadence_span.py:47`](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/scripts/launch_cadence_span.py#L47) · [`launch_cadence_span.py:356`](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/scripts/launch_cadence_span.py#L356-L379) · [`cadence_legs_runner.py:367`](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/scripts/cadence_legs_runner.py#L367) · [`cadence_leg_runtime.py:25`](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/scripts/cadence_leg_runtime.py#L25) · [RL-197 §1](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L23847-L23876)

### 4. Conditional sequence and gates

**No ctl-01 issue or arm on the fast route under the current ruling.** The decision needed from the research lead is whether an admitted final kit-v1.1 merge SHA containing #808, #900 and #946 may satisfy RL-197 §1 step 1. If granted, the lead can use this sequence after fixing the separate CI gate. The branch and all three heads were still at the stated stack when checked.

1. Confirm the expected base and head for each PR. Preserve the ancestry by using merge commits, with each PR made ready by the lead after its applicable review and merge gates. Retarget #900 only after #808 lands, and #946 only after #900 lands. The three `gh pr merge` invocations below are conditional lead commands. Set `reviewed_946` to the final reviewed, full-suite-green #946 head after the CI repair.

   ```sh
   set -e
   base=align/2026-11-14-kit-v1-1
   gh pr merge 808 --merge --match-head-commit 1f8541e4be45ce33f0fca1b9c9e25fc73c24cc35
   gh pr edit 900 --base "$base"
   gh pr merge 900 --merge --match-head-commit 9bb03a74147831d427007560a98af6ef9673700d
   gh pr edit 946 --base "$base"
   gh pr merge 946 --merge --match-head-commit "$reviewed_946"
   git fetch origin "refs/heads/$base:refs/remotes/origin/$base"
   pin=$(git rev-parse "refs/remotes/origin/$base")
   test "$(git rev-parse "$pin^{tree}")" = "$(git rev-parse "$reviewed_946^{tree}")"
   ```

2. Record the independent executing runner audit, clean finding dispositions, full green uncached suite on the final tree, and full synthetic launch-to-close CI required by F-11. Admit the new pin explicitly. Stage a clean detached checkout at `$pin`. There, run `python3.13 -B scripts/cadence_legs_runner.py pin-kit "$KIT" --commit "$pin" --write` and `python3.13 -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$CHECKOUT" --batch-window 02:00-02:35` on the final kit. Obtain the independent cold kit PASS and bind the final issued kit digest in the index and pilot queue. Run `python3.13 -B scripts/cadence_queue.py validate-queue "$QUEUE" --kits-root "$KIT_ROOT"`. Record the exact pin, kit and queue hashes, attempt, compatible predecessor, and ladder rank through the lead's typed issue. [RL-179 F-11](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18836-L18849) · [RUN_STATE 536 priority](https://github.com/mpmdw/JouleWise/blob/9c782c6eda0661247ef1c98268a4afd775e2e6dc/RUN_STATE.md#L1140-L1149)
3. In the quiet magistrate lane, use the **Shared Start and check** above. From the detached `$CHECKOUT`, run `cadence_queue.py next`, the kit `checklist`, `launch_cadence_span.py close-proof --attempt-ledger "$LEDGER"`, and `cadence_legs_runner.py plan --kit "$KIT" --legs "$LEGS" --batch-window 02:00-02:35 --t0 "$T0"` with the actual t0. Use the plan's launch deadline plus the lead's approved slack and the current ladder's time-fit protections. A passing next decision is advisory. Issue only if the roster fits before higher ranks and the soak clears the batch under item 507. Item 463's omitted-window instruction is for the named pin-B filler kits. Then run the checked checkout's `launch_cadence_span.py launch` with that repo, interpreter, output, host paths and deadline, the exact kit and queue digests and selected plan/roster, the shared ledger, predecessor receipt and its `--t0-not-before-ns`. At the pilot close require automatic desk PASS and the independent F-3(c) plus RL-197 four-view PASS. Only then issue the nine-leg queue with `pilot_pass_sha256` and pass its signed record as `--pilot-hand-read`. [RUN_STATE 439 deadline](https://github.com/mpmdw/JouleWise/blob/9c782c6eda0661247ef1c98268a4afd775e2e6dc/RUN_STATE.md#L3411) · [RUN_STATE 463 pin B](https://github.com/mpmdw/JouleWise/blob/9c782c6eda0661247ef1c98268a4afd775e2e6dc/RUN_STATE.md#L2852) · [RUN_STATE 507](https://github.com/mpmdw/JouleWise/blob/9c782c6eda0661247ef1c98268a4afd775e2e6dc/RUN_STATE.md#L1858-L1874) · [RL-197 pilot and span 2](https://github.com/mpmdw/JouleWise/blob/4bd044268212bbd44fd09a0c25cb66c320667f4d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L23855-L23860)

## RL-197b — kit-v1.1 merge preparation and issue drafts

RL-197b amends the main-only reading above. The lead can admit the reviewed result of PRs #808, #900 and #946 on the kit-v1.1 line. Main integration follows separately. This preparation uses the preferred no-code predecessor route. The lead owns each merge, the permanent ref and final admission. [RL-197b](https://github.com/mpmdw/JouleWise/blob/375d2b6ebc360138c3d55a42a3c2b799d3cecd4b/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L25140-L25185)

### Merged stack and tree verification

| PR | Reviewed head | Landed first-parent commit | Tree |
| --- | --- | --- | --- |
| #808 | `1f8541e4be45ce33f0fca1b9c9e25fc73c24cc35` | `79038a57d59e9259ab0f2d1b7d62658a2a0e399e` | `0fd2be59ce11f4e28ea64248b47771832b934015` |
| #900 | `9bb03a74147831d427007560a98af6ef9673700d` | `048267ba62aa1bba5d8787775277e97677a34eed` | `f6eb6f623bd03cadd17c0e5dd4fee98702654394` |
| #946 | `b8e1fb362af5ed8cd3a8f8b48b265ada36f8c081` | `f45e22e4efa6b48dd05f099f39eb62246e324177` | `3cbb765c118b0370b038d697943ce74c54b0e718` |

The first-parent history confirms all three PRs landed in order on `align/2026-11-14-kit-v1-1`. Its tip is `f45e22e4efa6b48dd05f099f39eb62246e324177`. Its tree hash and the empty diff against final #946 confirm the exact tested tree. [Landed merge](https://github.com/mpmdw/JouleWise/commit/f45e22e4efa6b48dd05f099f39eb62246e324177)

The prior local preview `99b672142d31e683986813f75d48e4168abd862c` is reproducible below. Tree equality carries the test evidence under RL-144 term 3. The kit now records the landed commit and its own digest.

```sh
set -eu
export GIT_AUTHOR_NAME=Codex GIT_COMMITTER_NAME=Codex
export GIT_AUTHOR_EMAIL=noreply@openai.com GIT_COMMITTER_EMAIL=noreply@openai.com
export GIT_AUTHOR_DATE=2026-11-22T14:00:00Z GIT_COMMITTER_DATE=2026-11-22T14:00:00Z
preview() {
    tree=$(git merge-tree --write-tree "$1" "$2")
    test "$tree" = "$(git rev-parse "$2^{tree}")"
    git -c commit.gpgsign=false commit-tree "$tree" -p "$1" -p "$2" -m "RL-197b preview: PR #$3" -m "Co-Authored-By: Sol 6.2 <noreply@openai.com>"
}
p808=$(preview 6e9d42f1dd3d308bc9239143d0d634ab965e50e1 1f8541e4be45ce33f0fca1b9c9e25fc73c24cc35 808)
p900=$(preview "$p808" 9bb03a74147831d427007560a98af6ef9673700d 900)
p946=$(preview "$p900" b8e1fb362af5ed8cd3a8f8b48b265ada36f8c081 946)
test "$p946" = 99b672142d31e683986813f75d48e4168abd862c
git diff --exit-code "$p946" b8e1fb362af5ed8cd3a8f8b48b265ada36f8c081
```

### Admission evidence on the landed tree

| Gate | Result |
| --- | --- |
| Hosted red fix and scope | PASS. `tests/cadence/test_legs_runner.py` is the only path changed from `043b972f9` to `b8e1fb362`. The ledger/bootstrap fixture stages a real matching Git checkout and mocks bootstrap separately from Git. All six launcher tests passed locally. `test_launch_ledger_records_attempt_even_if_bootstrap_fails` and all 61 module tests passed in [hosted shard 8](https://github.com/mpmdw/JouleWise/actions/runs/45027639795/job/137224154987). Runtime, config, workflow and all 40 frozen path bytes compare equal. |
| Independent executing review | Audit round 5 returned MERGE on final #946 head `b8e1fb362` and its projected tree. It recorded 56 focused tests and both F-11 synthetic rosters closed with zero stops. |
| Full uncached suite on the expected tree | **PASS, 21 of 21 jobs** in hosted run [45027639795](https://github.com/mpmdw/JouleWise/actions/runs/45027639795) for `b8e1fb362`. GitHub's PR test merge `cde8f9a26d4c1813f7258debd58e71881c22eae7` has the same tree `3cbb765c118b0370b038d697943ce74c54b0e718`. |
| F-11 synthetic launch-to-close | `tests.cadence.test_ctl.RuntimeTests.test_span_driver_runs_real_scripts_to_close_and_desk` and `LaunchAuthorityTests` on the same tree. **PASS, 22 focused tests**. The scripted runtime completes both spans through close and desk, and the launcher fixtures cover the queue-bound launch, predecessor proof and hands-off startup. The runtime test passed with the exact re-pinned review kit on the projected checkout and in [hosted shard 6](https://github.com/mpmdw/JouleWise/actions/runs/45027639795/job/137224154886), where all 50 module tests passed. Record these results and the full CI run at admission. |
| Preserve and validate pin A and pin B | Pin A `2d347f721552fe03bdd19f113e7bad7a7c24908e` remains for kits 01–14. Pin B `6e9d42f1dd3d308bc9239143d0d634ab965e50e1` remains for kits 15–16 and `cl-qual-01..03`. The landed validators passed all three approved qualification kits at pin B and all three queues covering six spans. The pin-B filler kits and their original and W2 queues passed on the identical projected tree. |
| Ctl-01 review kit and queues | The landed generator reproduced the reviewed kit byte for byte before re-pin. `pin-kit` changed only `frozen.commit`, and all 40 frozen digests matched. The index runner pin and the three kit digest references were regenerated. Both halted queues passed. The clean detached checkout check matched HEAD and all 40 working-tree files in a read-only fixture. The signed-off design remains 128/256/512 hidden tokens twice each, 10/30/90 s CPU legs, 600 s recovery, 60 s split gaps, 2,000 prefill, 3 + 9, seed `2026111601`. |

For the qualification recheck, use `item-drafts-1118/kits/cl-qual-0[123].v1.1.json` and `item-drafts-1118/queues/cl-qual-0[123].queue.json` from audit commit `375d2b6ebc360138c3d55a42a3c2b799d3cecd4b`. Stage the unchanged kit copies under `docs/process/cadence/kits/` inside a separate staging root. From the landed runner checkout, use `cadence_queue.py validate-kit --repo <landed checkout> --batch-window 02:00-02:35` on each staged kit and `cadence_queue.py validate-queue --kits-root <staging root>` on each matching queue. [Audited qualification kit and queue sources](https://github.com/mpmdw/JouleWise/tree/375d2b6ebc360138c3d55a42a3c2b799d3cecd4b/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-1118)

| Landed review artifact | SHA-256 |
| --- | --- |
| `cl-ctl-01.draft.json` | `7636dd298508eb02ae4e71aa7ab172e31a23d9c8e356e41223601972930b3545` |
| `ctl-01-s01.draft.json` | `9f3dc87e72e70cacc0290fb30e70005b8077bf45461e5ce2b1cb44c6f834a012` |
| `ctl-01-s02.draft.json` | `0a03c225f418d8d93a9be8277cd731ea96016261d573ce987bd734e6bcb932ea` |
| `KITS.json` | `6ce19e9ecaed85d08546c4b345ccdafd35c15ec7c9b4cdc5c8b903b4d4179ecc` |

The re-pin uses targeted validators for the review JSON and typed drafts. The green full suite above covers the identical landed runner tree.

The two review queues remain halted and bind the review kit. At issue, the lead supplies separate finite queues bound to the issued kit digest. The pilot draft's inert halt message still mentions main. RL-197b governs the issued queue.

The independent cold check passed the landed review digests above. The landed `pin-kit` command resolved the permanent tag named in the admission item to the full landed SHA and reproduced the reviewed kit bytes.

**Issued kit** — SHA-256 `1d7d6f5fe8531b74401fb8d6e60b8fa17f068849e59ec3c241caaa6f523ff2bf`. The landed generator and tag-based pin command reproduced the reviewed payload. The landed kit validator and the clean-checkout guard passed at `f45e22e4efa6b48dd05f099f39eb62246e324177`, including all 40 frozen files. The lead authorized these two substitutions. Every other byte matched. RUN_STATE 543 records the independent cold PASS on the issued digest and admits the pin. [Issued kit](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/ctl-01/kits/cl-ctl-01.issued.json)

```diff
--- cl-ctl-01.draft.json
+++ cl-ctl-01.issued.json
@@ -7 +7 @@
-  "authorizes_spans": false
+  "authorizes_spans": true
@@ -534 +534 @@
- "status": "draft",
+ "status": "issued",
```

### Posted admission and RL-197c dispatch

RUN_STATE 543 admitted ctl-01 at `f45e22e4efa6b48dd05f099f39eb62246e324177` under `refs/tags/pin/cl-ctl-01-runner` and records independent cold PASS on the issued kit digest. RL-197c resolves the earlier first-row authority hold. The only bootstrap is the reviewed initializer from PR #955, checked out at its actual full merge commit on main. Fill that value after the lead merges and verifies the review and CI gates. The PR head is the CLI reference for these drafts. Item 1 may be issued before the initializer merges. Item 2 waits for both the merge and the inaugural verified close. [RUN_STATE 543](https://github.com/mpmdw/JouleWise/blob/83f296a8e71a13ce655acdf67fa1c8909cd1253d/RUN_STATE.md#L1055-L1064) · [RL-197c](https://github.com/mpmdw/JouleWise/blob/17aecf346311503e4d618323b196a25cbb0927f3/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L25411) · [Initializer CLI](https://github.com/mpmdw/JouleWise/blob/c178149ac3175d51f28ecd6513a0a6101c12380b/scripts/init_attempt_ledger.py#L84-L99)

The lead posts each item with `scripts/run_state_add.py add` at its gate, with the actual issue epoch, finite expiry and offset-bearing follow-up deadline. Replace angle-bracket placeholders before posting. Supply the shell variables from that issue and the magistrate's authorized session. The blocks use Bash and canonical absolute paths. The only public values below are the review inputs. The real close evidence and host paths belong in the authorized handoff.

#### 1. ISSUE — inaugural pin-B leg

**Heading** — MAGISTRATE — ISSUE f2-stab-15 L007 on pin B, inaugural RL-197c span, cq-f2-stab-15-l007-a1

**Typed header** — owner `magistrate`, status `ISSUED`, issued `<actual issue time>`, expiry `<finite issue expiry>`.

```text
owner: magistrate
wait: result_json_exists
deadline: <offset-bearing follow-up deadline at or after the launch fence>
on_early_or_refused: Read the verdict first. A refusal or missing or unproven close holds initialization and the ctl pilot. Report to the lead. An unstarted stability position stays unrun.
next_observable: <absolute B_OUTPUT>/runner_receipt.json for cq-f2-stab-15-l007-a1, followed by its verified close and Check
```

> Issue exactly L007 of f2-stab-15 on pin B `6e9d42f1dd3d308bc9239143d0d634ab965e50e1`, directly ahead of the ctl pilot under RL-197c §3. The W2 ladder selects the lowest eligible kit and its next unrun position. Item 519 closed L006. Recheck that L007 is still unrun and eligible at actual issue and launch. If it has been spent or fails eligibility, hold and return to the lead for a new selection. Use the item 463 pin-B filler dispatch and item 507 soak check. The only leg is cold under RL-200 §2.
>
> Arm with `--span-id cq-f2-stab-15-l007-a1` equal to the typed attempt ID and without `--attempt-ledger` under RL-197c. The create-once output directory basename equals that attempt ID. This is the last armed span before the counted pilot. After its close, arm nothing else until the pilot. Stability pauses. Run the ordinary close and Check. Verify the receipt's embedded ID, canonical absolute path, full SHA-256, exact close ns, restore, feeds stopped, groups absent and foreign-process absence. Hand those facts to the lead for item 2. Hold items 2 and 3 until this close is verified.

- **Kit path** — `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/qual-pin/f2-stab-15.v1.1.json`, SHA-256 `8dceffc2e1a10a03d25c6c06487756fe37f8f5a1c57d52e242a64faabcbc36a1`.
- **Queue path** — `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/fillers-w2/queues-1leg/f2-stab-15.json`, SHA-256 `1adf8673916f1f7675478665b7fcb80cf56d3647d298fb16032a864d613ca8a2`. Queue `cq-f2-stab-15`, seq `7`, span `f2-stab-15-l007`, roster `L007`, attempt `1`, not before `2026-11-17`, exclusive expiry `2026-12-08T12:35:29-08:00`. [W2 queue manifest](https://github.com/mpmdw/JouleWise/blob/17aecf346311503e4d618323b196a25cbb0927f3/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/fillers-w2/README.md) · [Standing ladder and typed dispatch](https://github.com/mpmdw/JouleWise/blob/83f296a8e71a13ce655acdf67fa1c8909cd1253d/RUN_STATE.md#L1239-L1324) · [Items 464 and 463](https://github.com/mpmdw/JouleWise/blob/83f296a8e71a13ce655acdf67fa1c8909cd1253d/RUN_STATE.md#L2941-L2966)

Add the following dispatch record to the item body. Substitute the actual integer issue epoch for `<ISSUED_EPOCH_S>`. It must match the typed header.

```json
{
  "schema": "joulewise.cadence_span_dispatch.v1",
  "attempt_id": "cq-f2-stab-15-l007-a1",
  "campaign_id": "f2-stab-15",
  "kit_sha256": "8dceffc2e1a10a03d25c6c06487756fe37f8f5a1c57d52e242a64faabcbc36a1",
  "frozen_pin": "6e9d42f1dd3d308bc9239143d0d634ab965e50e1",
  "roster": ["L007"],
  "kit_positions": [7],
  "issued_epoch_s": <ISSUED_EPOCH_S>,
  "arg": null,
  "batch_windows": []
}
```

**Run block** — Bind `PIN_B_CHECKOUT`, `PIN_B_PYTHON`, `AUDIT_EVIDENCE_ROOT`, `B_OUTPUT`, `DISK_PATH`, `CUSTODY_ROOT` and `MAGISTRATE_PID` from the issue. `AUDIT_EVIDENCE_ROOT` is the root containing the full kit and queue paths above. Check the standing pin-B eligibility and the item 507 soak condition at actual t0. Item 463 omits the window argument and uses the actual-t0 plan deadline plus 900 seconds. Launch once as the last act.

```bash
(
  set -euo pipefail
  : "${PIN_B_CHECKOUT:?}" "${PIN_B_PYTHON:?}" "${AUDIT_EVIDENCE_ROOT:?}" "${B_OUTPUT:?}"
  : "${DISK_PATH:?}" "${CUSTODY_ROOT:?}" "${MAGISTRATE_PID:?}"
  b_attempt=cq-f2-stab-15-l007-a1
  b_base="$AUDIT_EVIDENCE_ROOT/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign"
  b_kit="$b_base/f2-stab/qual-pin/f2-stab-15.v1.1.json"
  b_queue="$b_base/fillers-w2/queues-1leg/f2-stab-15.json"
  test "$(git -C "$PIN_B_CHECKOUT" rev-parse HEAD)" = 6e9d42f1dd3d308bc9239143d0d634ab965e50e1
  b_status=$(git --no-optional-locks -C "$PIN_B_CHECKOUT" status --porcelain)
  test -z "$b_status"
  test "${B_OUTPUT##*/}" = "$b_attempt"
  test ! -e "$B_OUTPUT"
  test ! -L "$B_OUTPUT"
  b_kit_sha=$(shasum -a 256 "$b_kit")
  b_queue_sha=$(shasum -a 256 "$b_queue")
  test "${b_kit_sha%% *}" = 8dceffc2e1a10a03d25c6c06487756fe37f8f5a1c57d52e242a64faabcbc36a1
  test "${b_queue_sha%% *}" = 1adf8673916f1f7675478665b7fcb80cf56d3647d298fb16032a864d613ca8a2
  "$PIN_B_PYTHON" -I -B "$PIN_B_CHECKOUT/scripts/cadence_queue.py" validate-kit "$b_kit" --repo "$PIN_B_CHECKOUT"
  "$PIN_B_PYTHON" -I -B "$PIN_B_CHECKOUT/scripts/cadence_queue.py" validate-queue "$b_queue" --kits-root "$AUDIT_EVIDENCE_ROOT"
  "$PIN_B_PYTHON" -I -B -c '
import json, sys
from datetime import datetime
from zoneinfo import ZoneInfo
with open(sys.argv[1]) as source:
    queue = json.load(source)
now = datetime.now(ZoneInfo("America/Los_Angeles"))
if now.date().isoformat() < "2026-11-17" or now >= datetime.fromisoformat(queue["expires_at"]):
    raise SystemExit("pin-B queue is outside its authorized dates")
' "$b_queue"
  b_plan=$("$PIN_B_PYTHON" -I -B "$PIN_B_CHECKOUT/scripts/cadence_legs_runner.py" plan \
    --kit "$b_kit" --legs L007 --t0 "$(date +%s)")
  b_deadline=$(printf '%s\n' "$b_plan" | "$PIN_B_PYTHON" -I -B -c '
import json, sys
plan = json.load(sys.stdin)
if not plan["blackout_clear"] or plan["batch_windows"] != []:
    raise SystemExit("pin-B actual-t0 plan did not clear")
print(plan["launch_deadline_epoch_s"] + 900)
')
  "$PIN_B_PYTHON" -I -B "$PIN_B_CHECKOUT/scripts/launch_cadence_span.py" launch \
    --repo "$PIN_B_CHECKOUT" --python-bin "$PIN_B_PYTHON" --kit "$b_kit" --legs L007 \
    --output "$B_OUTPUT" --disk-path "$DISK_PATH" --custody-root "$CUSTODY_ROOT" \
    --magistrate-pid "$MAGISTRATE_PID" --deadline "$b_deadline" --span-id "$b_attempt"
)
```

#### 2. ISSUE — initialize ledger sequence 1

**Heading** — MAGISTRATE — ISSUE RL-197c first attempt-ledger row from verified cq-f2-stab-15-l007-a1 close

**Typed header** — owner `magistrate`, status `ISSUED`, issued `<actual issue time after the verified Check>`, expiry `<finite issue expiry>`.

```text
owner: magistrate
wait: result_json_exists
deadline: <offset-bearing initializer follow-up deadline>
on_early_or_refused: Hold the pilot and span 2. Report the refusal or partial output to the lead for RL-197c section 3 disposition. A close-proof refusal spends no ctl leg. Preserve existing files.
next_observable: <absolute ATTEMPT_LEDGER>.first-row.json plus the ledger and sidecar SHA-256s for this issue
```

> This item is conditional on the verified close of inaugural dispatch `<INAUGURAL_DISPATCH_ITEM>`, attempt `cq-f2-stab-15-l007-a1`. This attempt is the last armed span on the host. Bind its unchanged absolute receipt path `<CLOSE_RECEIPT>`, full receipt SHA-256 `<RECEIPT_SHA256>` and exact close ns `<CLOSE_NS>`. Run the reviewed initializer at `<initializer merge commit>` in its own clean checkout, in this or the next magistrate activation after the verified close. Use the same desk lock as the inaugural launch. Carry the four receipt-bound attestations from the verified Check. The initializer's `--run-state-item` is this item's number, `{{self}}`. The inaugural dispatch number remains a separate binding in this issue.
>
> Record the published ledger SHA-256, sidecar absolute path and sidecar SHA-256 in the Check for this item. The first row is sequence 1. If another span armed, hold and return to the lead. If close-proof refuses, no ctl leg is spent. Hold initialization and the pilot, preserve any outputs, and return to the lead. The lead routes a proof refusal without a real close fault, a refused ledger state or an interrupted publication to the research lead under RL-197c. Initialization is a one-time action.

**Run block** — Bind `INIT_ITEM` to this typed issue number and `INIT_COMMIT` to the full PR #955 merge commit on main. The script captures that checkout's HEAD in the sidecar. Bind `INIT_CHECKOUT`, `CTL_CHECKOUT`, `PYTHON_BIN`, `ATTEMPT_LEDGER` and `CUSTODY_ROOT` to the exact issue paths. Bind `LAST_ARMED_SPAN_ID`, `CLOSE_RECEIPT`, `RECEIPT_SHA256` and `CLOSE_NS` from the issue and verified Check. Supply `CLOSE_PROOF_RECEIPT` and the four true attestation variables only after checking that receipt and the host. The block checks and passes them through.

```bash
(
  set -euo pipefail
  : "${INIT_ITEM:?}" "${INIT_COMMIT:?}" "${INIT_CHECKOUT:?}" "${CTL_CHECKOUT:?}" "${PYTHON_BIN:?}"
  : "${ATTEMPT_LEDGER:?}" "${CUSTODY_ROOT:?}" "${LAST_ARMED_SPAN_ID:?}"
  : "${CLOSE_RECEIPT:?}" "${RECEIPT_SHA256:?}" "${CLOSE_NS:?}"
  span_id=cq-f2-stab-15-l007-a1
  test "$LAST_ARMED_SPAN_ID" = "$span_id"
  test "$(git -C "$INIT_CHECKOUT" rev-parse HEAD)" = "$INIT_COMMIT"
  init_status=$(git --no-optional-locks -C "$INIT_CHECKOUT" status --porcelain)
  test -z "$init_status"
  test "$(git -C "$CTL_CHECKOUT" rev-parse HEAD)" = f45e22e4efa6b48dd05f099f39eb62246e324177
  test "${CLOSE_PROOF_RECEIPT:?}" = "$CLOSE_RECEIPT"
  test "${HOST_RESTORE_OK:?}" = 1
  test "${FEEDS_STOPPED:?}" = 1
  test "${GROUPS_ABSENT:?}" = 1
  test "${FOREIGN_PROCESSES_ABSENT:?}" = 1
  export CLOSE_PROOF_RECEIPT HOST_RESTORE_OK FEEDS_STOPPED GROUPS_ABSENT FOREIGN_PROCESSES_ABSENT
  ledger_sha=$("$PYTHON_BIN" -I -B "$INIT_CHECKOUT/scripts/init_attempt_ledger.py" \
    --ledger "$ATTEMPT_LEDGER" --custody-root "$CUSTODY_ROOT" --span-id "$span_id" \
    --close-receipt "$CLOSE_RECEIPT" --receipt-sha256 "$RECEIPT_SHA256" --close-ns "$CLOSE_NS" \
    --ctl-checkout "$CTL_CHECKOUT" --python-bin "$PYTHON_BIN" --run-state-item "$INIT_ITEM")
  published_sha=$(shasum -a 256 "$ATTEMPT_LEDGER")
  test "$ledger_sha" = "${published_sha%% *}"
  printf '%s\n' "$published_sha"
  shasum -a 256 "$ATTEMPT_LEDGER.first-row.json"
)
```

#### 3. ISSUE — counted ctl-01 pilot L001–L003

**Heading** — MAGISTRATE — ISSUE cl-ctl-01 counted pilot L001–L003 on f45e22e4e, cq-ctl-01-s01-a1, RL-197c sequence 2

**Typed header** — owner `magistrate`, status `ISSUED`, issued `<actual issue time after item 2 Check>`, expiry `<finite pilot queue and issue expiry>`.

```text
owner: magistrate
wait: result_json_exists
deadline: <offset-bearing pilot follow-up deadline at or after the launch fence>
on_early_or_refused: Read the verdict first. A refusal before any leg spends no ctl leg. Hold for the lead if the close proof fails or if an attempt was appended with no receipt. Preserve the ledger and return the unresolved state through RL-197c.
next_observable: <absolute CTL_PILOT_OUTPUT>/runner_receipt.json for cq-ctl-01-s01-a1, then verified close, automatic desk PASS and signed independent pilot hand-read
```

> Issue only L001–L003 as the first native run at admitted pin `f45e22e4efa6b48dd05f099f39eb62246e324177` in the separate clean detached checkout. Item 1's verified close and item 2's successful Check are prerequisites. The immediate predecessor is `cq-f2-stab-15-l007-a1` from dispatch `<INAUGURAL_DISPATCH_ITEM>`. Its unchanged absolute receipt is `<CLOSE_RECEIPT>`, SHA-256 `<RECEIPT_SHA256>`, exact close `<CLOSE_NS>` ns. No other span has armed since that close. The authorized shared ledger `<ATTEMPT_LEDGER>` has that predecessor as sequence 1 and SHA-256 `<LEDGER_SHA256>`. The first-row sidecar has SHA-256 `<SIDECAR_SHA256>`.
>
> Use the issued kit SHA-256 `1d7d6f5fe8531b74401fb8d6e60b8fa17f068849e59ec3c241caaa6f523ff2bf`, finite pilot queue `<CTL_PILOT_QUEUE and full SHA-256>` and `<standing rank from the issue>`. Apply **Shared Start and check**, the actual-t0 plan and item 507 soak check. The ctl launcher re-proves the predecessor under the desk lock, binds the exact receipt and nanosecond lower bound, and appends the pilot as sequence 2 before bootstrap. Launch once as the last act.
>
> After the pilot's proven close and automatic desk PASS, assign the independent F-3(c) and RL-197 four-view hand-read of stamps and counts. Hold span 2 for the signed PASS bound to this issued kit and pilot receipt. Arm no intervening span in this sequence-2 then sequence-3 issue plan. After PASS, the lead separately issues L004–L012 with the signed PASS digest in its finite queue row and the same shared ledger. The pilot is the predecessor and the ctl launcher appends span 2 as sequence 3. Keep L006 and L007 together.

**Run block** — Bind `CTL_KIT` to the issued kit at `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/ctl-01/kits/cl-ctl-01.issued.json`. Bind `CTL_PILOT_QUEUE`, `CTL_PILOT_QUEUE_SHA256` and `QUEUE_KITS_ROOT` to the lead's finite one-span pilot queue and kit root. It must authorize `cq-ctl-01-s01-a1`, L001–L003 and the issued digest, with the real earliest date, expiry and standing rank. The halted review queue remains a review artifact. Supply `CTL_PILOT_OUTPUT`, `CTL_PILOT_DEADLINE` from the actual-t0 plan and authorized slack, `DISK_PATH`, `MAGISTRATE_PID` and the same `CTL_CHECKOUT`, `PYTHON_BIN`, `CUSTODY_ROOT`, `ATTEMPT_LEDGER` and close quantities as above. Supply the checked `LEDGER_SHA256` and `SIDECAR_SHA256` from item 2. Recheck the genuine receipt-bound attestations on the current activation before running.

```bash
(
  set -euo pipefail
  : "${CTL_CHECKOUT:?}" "${PYTHON_BIN:?}" "${CTL_KIT:?}" "${CTL_PILOT_QUEUE:?}"
  : "${CTL_PILOT_QUEUE_SHA256:?}" "${QUEUE_KITS_ROOT:?}" "${CTL_PILOT_OUTPUT:?}" "${CTL_PILOT_DEADLINE:?}"
  : "${DISK_PATH:?}" "${CUSTODY_ROOT:?}" "${MAGISTRATE_PID:?}" "${ATTEMPT_LEDGER:?}"
  : "${CLOSE_RECEIPT:?}" "${RECEIPT_SHA256:?}" "${CLOSE_NS:?}" "${LEDGER_SHA256:?}" "${SIDECAR_SHA256:?}"
  ctl_pin=f45e22e4efa6b48dd05f099f39eb62246e324177
  ctl_kit_sha=1d7d6f5fe8531b74401fb8d6e60b8fa17f068849e59ec3c241caaa6f523ff2bf
  predecessor=cq-f2-stab-15-l007-a1
  test "$(git -C "$CTL_CHECKOUT" rev-parse HEAD)" = "$ctl_pin"
  ctl_status=$(git --no-optional-locks -C "$CTL_CHECKOUT" status --porcelain)
  test -z "$ctl_status"
  test "${CLOSE_PROOF_RECEIPT:?}" = "$CLOSE_RECEIPT"
  test "${HOST_RESTORE_OK:?}" = 1
  test "${FEEDS_STOPPED:?}" = 1
  test "${GROUPS_ABSENT:?}" = 1
  test "${FOREIGN_PROCESSES_ABSENT:?}" = 1
  export CLOSE_PROOF_RECEIPT HOST_RESTORE_OK FEEDS_STOPPED GROUPS_ABSENT FOREIGN_PROCESSES_ABSENT
  receipt_hash=$(shasum -a 256 "$CLOSE_RECEIPT")
  ledger_hash=$(shasum -a 256 "$ATTEMPT_LEDGER")
  sidecar_hash=$(shasum -a 256 "$ATTEMPT_LEDGER.first-row.json")
  test "${receipt_hash%% *}" = "$RECEIPT_SHA256"
  test "${ledger_hash%% *}" = "$LEDGER_SHA256"
  test "${sidecar_hash%% *}" = "$SIDECAR_SHA256"
  "$PYTHON_BIN" -I -B "$CTL_CHECKOUT/scripts/cadence_queue.py" validate-queue "$CTL_PILOT_QUEUE" --kits-root "$QUEUE_KITS_ROOT"
  proof=$("$PYTHON_BIN" -I -B "$CTL_CHECKOUT/scripts/launch_cadence_span.py" close-proof --attempt-ledger "$ATTEMPT_LEDGER")
  test "$proof" = "$(printf '%s\n%s\n%s' "$predecessor" "$CLOSE_NS" "$CLOSE_RECEIPT")"
  "$PYTHON_BIN" -I -B "$CTL_CHECKOUT/scripts/launch_cadence_span.py" launch \
    --repo "$CTL_CHECKOUT" --python-bin "$PYTHON_BIN" --kit "$CTL_KIT" --kit-sha256 "$ctl_kit_sha" \
    --queue "$CTL_PILOT_QUEUE" --queue-sha256 "$CTL_PILOT_QUEUE_SHA256" --queue-kits-root "$QUEUE_KITS_ROOT" \
    --legs L001,L002,L003 --batch-window 02:00-02:35 --output "$CTL_PILOT_OUTPUT" \
    --disk-path "$DISK_PATH" --custody-root "$CUSTODY_ROOT" --magistrate-pid "$MAGISTRATE_PID" \
    --deadline "$CTL_PILOT_DEADLINE" --span-id cq-ctl-01-s01-a1 --attempt-ledger "$ATTEMPT_LEDGER" \
    --previous-close-receipt "$CLOSE_RECEIPT" --t0-not-before-ns "$CLOSE_NS"
)
```

**Span 2 handoff** — The lead posts separate span-2 authority only after the pilot PASS. Bind the actual pilot attempt `cq-ctl-01-s01-a1`, absolute receipt path, full receipt SHA-256 and exact close ns, the latest ledger SHA-256 and the signed pilot PASS SHA-256. The sidecar still binds initialization. Bind `pilot_pass_sha256` in the finite span-2 queue before hashing and posting it. The latest row must be the pilot at sequence 2. Retain the same admitted kit and shared ledger. RL-198 close accounting and the independent first-split hand-read remain due before the look.

For that future issue, bind `CLOSE_RECEIPT`, `RECEIPT_SHA256`, `CLOSE_NS` and the genuine attestations to the pilot close. Bind `LEDGER_SHA256` to the post-pilot ledger, `SIDECAR_SHA256` to item 2's sidecar, `PILOT_HAND_READ` and `PILOT_PASS_SHA256` to the signed PASS, and `CTL_SPAN2_QUEUE`, `CTL_SPAN2_QUEUE_SHA256`, `CTL_SPAN2_OUTPUT` and `CTL_SPAN2_DEADLINE` to the new issue and actual-t0 plan. Run the shared start checks before this block.

```bash
(
  set -euo pipefail
  : "${CTL_CHECKOUT:?}" "${PYTHON_BIN:?}" "${CTL_KIT:?}" "${CTL_SPAN2_QUEUE:?}"
  : "${CTL_SPAN2_QUEUE_SHA256:?}" "${QUEUE_KITS_ROOT:?}" "${CTL_SPAN2_OUTPUT:?}" "${CTL_SPAN2_DEADLINE:?}"
  : "${DISK_PATH:?}" "${CUSTODY_ROOT:?}" "${MAGISTRATE_PID:?}" "${ATTEMPT_LEDGER:?}"
  : "${CLOSE_RECEIPT:?}" "${RECEIPT_SHA256:?}" "${CLOSE_NS:?}" "${LEDGER_SHA256:?}" "${SIDECAR_SHA256:?}"
  : "${PILOT_HAND_READ:?}" "${PILOT_PASS_SHA256:?}"
  ctl_pin=f45e22e4efa6b48dd05f099f39eb62246e324177
  ctl_kit_sha=1d7d6f5fe8531b74401fb8d6e60b8fa17f068849e59ec3c241caaa6f523ff2bf
  test "$(git -C "$CTL_CHECKOUT" rev-parse HEAD)" = "$ctl_pin"
  ctl_status=$(git --no-optional-locks -C "$CTL_CHECKOUT" status --porcelain)
  test -z "$ctl_status"
  test "${CLOSE_PROOF_RECEIPT:?}" = "$CLOSE_RECEIPT"
  test "${HOST_RESTORE_OK:?}" = 1
  test "${FEEDS_STOPPED:?}" = 1
  test "${GROUPS_ABSENT:?}" = 1
  test "${FOREIGN_PROCESSES_ABSENT:?}" = 1
  export CLOSE_PROOF_RECEIPT HOST_RESTORE_OK FEEDS_STOPPED GROUPS_ABSENT FOREIGN_PROCESSES_ABSENT
  receipt_hash=$(shasum -a 256 "$CLOSE_RECEIPT")
  ledger_hash=$(shasum -a 256 "$ATTEMPT_LEDGER")
  sidecar_hash=$(shasum -a 256 "$ATTEMPT_LEDGER.first-row.json")
  pass_hash=$(shasum -a 256 "$PILOT_HAND_READ")
  test "${receipt_hash%% *}" = "$RECEIPT_SHA256"
  test "${ledger_hash%% *}" = "$LEDGER_SHA256"
  test "${sidecar_hash%% *}" = "$SIDECAR_SHA256"
  test "${pass_hash%% *}" = "$PILOT_PASS_SHA256"
  "$PYTHON_BIN" -I -B "$CTL_CHECKOUT/scripts/cadence_queue.py" validate-queue "$CTL_SPAN2_QUEUE" --kits-root "$QUEUE_KITS_ROOT"
  proof=$("$PYTHON_BIN" -I -B "$CTL_CHECKOUT/scripts/launch_cadence_span.py" close-proof --attempt-ledger "$ATTEMPT_LEDGER")
  test "$proof" = "$(printf '%s\n%s\n%s' cq-ctl-01-s01-a1 "$CLOSE_NS" "$CLOSE_RECEIPT")"
  "$PYTHON_BIN" -I -B "$CTL_CHECKOUT/scripts/launch_cadence_span.py" launch \
    --repo "$CTL_CHECKOUT" --python-bin "$PYTHON_BIN" --kit "$CTL_KIT" --kit-sha256 "$ctl_kit_sha" \
    --queue "$CTL_SPAN2_QUEUE" --queue-sha256 "$CTL_SPAN2_QUEUE_SHA256" --queue-kits-root "$QUEUE_KITS_ROOT" \
    --legs L004,L005,L006,L007,L008,L009,L010,L011,L012 --batch-window 02:00-02:35 --output "$CTL_SPAN2_OUTPUT" \
    --disk-path "$DISK_PATH" --custody-root "$CUSTODY_ROOT" --magistrate-pid "$MAGISTRATE_PID" \
    --deadline "$CTL_SPAN2_DEADLINE" --span-id cq-ctl-01-s02-a1 --attempt-ledger "$ATTEMPT_LEDGER" \
    --previous-close-receipt "$CLOSE_RECEIPT" --t0-not-before-ns "$CLOSE_NS" --pilot-hand-read "$PILOT_HAND_READ"
)
```
