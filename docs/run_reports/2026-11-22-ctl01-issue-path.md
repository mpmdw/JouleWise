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

The lead fills in angle-bracket values and posts these through `scripts/run_state_add.py add`. Supply each pointer as its own file after substituting the exact record, item, and offset-bearing deadline. The start-check below applies to both span items. Keep the arm record and operational details in the authorized lead/magistrate channels.

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

> Assign an independent seat to run the usual F-3(c) hand table and Q1 checks from the authorized template after the pilot's clean close and automatic desk PASS. Verify the close-bound source and use the allowlisted projection. For every admitted pilot leg L001–L003, take the visible calls from the bound script record plus the one logged envelope and episode/G0 bounds. This addition reads stamps and counts only.
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

1. Verify RL-197 values, integrated PRs #808, #900 and #946 pin on main, kit cold PASS, issued authorization and full frozen digests. Verify the finite queue SHA-256, the selected row's exact kit SHA-256 and roster, attempt, actual t0, expiry and standing rank. For span 2, bind the signed PASS digest in `pilot_pass_sha256`. Verify its kit, pilot plan and clean-close digest. Use the same elapsed, calendar and deadline policy as the standing ladder.
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

### Exact stack and projection

| PR | Current reviewed base branch | Head used for projection | Projected tree |
| --- | --- | --- | --- |
| #808 | `align/2026-11-14-kit-v1-1` at `6e9d42f1dd3d308bc9239143d0d634ab965e50e1` | `1f8541e4be45ce33f0fca1b9c9e25fc73c24cc35` | `0fd2be59ce11f4e28ea64248b47771832b934015` |
| #900 | `cadence/2026-11-16-ctl01-runner` | `9bb03a74147831d427007560a98af6ef9673700d` | `f6eb6f623bd03cadd17c0e5dd4fee98702654394` |
| #946 | `cadence/2026-11-20-ctl01-failed-envelope` | `b8e1fb362af5ed8cd3a8f8b48b265ada36f8c081` | `3cbb765c118b0370b038d697943ce74c54b0e718` |

The PRs already have these bases and remain drafts. The lead checks each head and the appropriate evidence, makes each ready, and merges #808 into its current base. Then retarget #900 to the updated kit-v1.1 line and merge it. Retarget #946 to the updated line after #900 and merge #946 last. Use ancestry-preserving merge commits, retaining each earlier head until its dependent PR lands. Confirm the final tree equals `3cbb765c118b0370b038d697943ce74c54b0e718`. A different tree returns to review and full testing under RL-197b §1.

The projected merge commit is **`99b672142d31e683986813f75d48e4168abd862c`**, with the exact final #946 tree and an empty tree diff. A deterministic preview reproduces the calculation. It writes Git objects only. The preview is a local validation pin. A GitHub merge assigns its own commit metadata, so the lead records the actual landed full SHA, protects a permanent ref and re-pins the issued kit to that SHA before the final cold seat. Tree equality carries test evidence under RL-144 term 3. It does not carry the kit's commit identity or digest.

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

### Admission evidence on the projected tree

| Gate | Result |
| --- | --- |
| Hosted red fix and scope | PASS locally. `tests/cadence/test_legs_runner.py` is the only path changed from `043b972f9` to `b8e1fb362`. The ledger/bootstrap fixture stages a real matching Git checkout and mocks bootstrap separately from Git. All six launcher tests passed, including the previously red case. Runtime, config, workflow and all 40 frozen path bytes compare equal. |
| Independent executing review | Audit round 4 returned MERGE on the previous head `043b972f9`, with 65 focused tests and both synthetic spans green. Record the independent executing seat's confirmation for the **final** #946 head before admitting the pin. |
| Full uncached suite on the expected tree | Hosted full run [45027639795](https://github.com/mpmdw/JouleWise/actions/runs/45027639795) on `b8e1fb362`, tree `3cbb765c118b0370b038d697943ce74c54b0e718`. Its final result is required. |
| F-11 synthetic launch-to-close | `tests.cadence.test_ctl.RuntimeTests.test_span_driver_runs_real_scripts_to_close_and_desk` and `LaunchAuthorityTests` on the same tree. **PASS, 22 tests**. The scripted runtime completes both spans through close and desk, and the launcher fixtures cover the queue-bound launch, predecessor proof and hands-off startup. Record this result and the full CI run at admission. |
| Preserve and validate pin A and pin B | Pin A `2d347f721552fe03bdd19f113e7bad7a7c24908e` remains for kits 01–14. Pin B `6e9d42f1dd3d308bc9239143d0d634ab965e50e1` remains for kits 15–16 and `cl-qual-01..03`. On the projected checkout, all three qualification kits verified their pin-B frozen files. All three qualification queues covering six spans passed with the approved audited kit copies staged at their queue-relative paths. The bundled lane versions differ from the approved kit hashes, which the validator correctly refused. Both pin-B filler kits, both original queues and both W2 one-leg queue files also validated. Repeat the read-only validators with the same staged bytes on the landed head for the admission record. |
| Ctl-01 review kit and queues | The signed-off design remains 128/256/512 hidden tokens twice each, 10/30/90 s CPU legs, 600 s recovery, 60 s split gaps, 2,000 prefill, 3 + 9, seed `2026111601`. Structural comparison proved only `frozen.commit` changed within the kit. The projected draft SHA-256 is `936e866cb03d547f54ec08b280712db6f6ac24e4e8cee7b5f643d07679b0cea1`. Clean checkout verification matched all 40 files. The index and both halted queue digests validated. Rebind to the actual full landed commit, regenerate dependent hashes, and get the cold PASS by the final issued digest. |

### Draft RUN_STATE item — pin admission

**Heading** — Admit cl-ctl-01 runner `<full landed merge commit>` under RL-197b, first native run is the counted pilot.

**Typed fields** — owner `lead`, status `ISSUED`. Post after all admission evidence is recorded. The full projection SHA above is a pre-merge witness. Use the full landed SHA in the item.

> ADMIT `<full landed merge commit>` on `align/2026-11-14-kit-v1-1`, permanent ref `<never-force-moved, never-deleted ref>`. PRs #808, #900 and #946 landed in order. The landed tree `<full tree SHA>` agrees with the reviewed head `<full #946 SHA>`. Independent executing audit `<PASS and evidence>`, uncached full suite `<run, executor and green result>`, and F-11 synthetic launch-to-close `<PASS and witness>` are recorded. Qualification kits and queues revalidated on the landed head with the pin-B kit bytes `<validation evidence>`. Pin A and pin B keep their full SHAs above. The final kit has `<issued kit SHA-256>` and `<independent cold kit PASS for that digest>`. Create a separate clean detached checkout at the admitted ctl-01 SHA. L001–L003 will be its first native run. The lead posts separate span authority when the actual close is proven.

Questions for the magistrate before the pilot is issued:

1. Does the shared attempt ledger exist on the MBP, and what authority and evidence establish how its first row was written?
2. Does a pin-B ledger-backed launch accept the shared ledger when its latest attempt row is a ctl row?
3. Do today's pin-B launches pass `--span-id` equal to the issued attempt ID?

Pin B's launcher requires the complete authority tuple for a ledger-backed launch. Its runner requires the authorized date, earliest start and exclusive cutoff if an exact t0 bound is supplied, including for a filler with ledger arguments. Use the magistrate's confirmed, approved pin-B invocation for that predecessor. Ctl-01's own t0 remains free with its exact close bound. [Pin B launcher](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/launch_cadence_span.py#L215-L225) · [Pin B t0 validator](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L381-L396)

### Draft RUN_STATE item — counted pilot L001–L003

**Heading** — MAGISTRATE — cl-ctl-01 pilot L001–L003 on `<full admitted commit>`, cq-ctl-01-s01-a1.

**Typed fields** — owner `magistrate`, status `ISSUED`, expiry `<finite issue expiry>`.

```text
owner: magistrate
wait: result_json_exists
deadline: <follow-up deadline at or after the launch fence>
on_early_or_refused: Read the verdict first. A missing receipt, refusal or unproven close holds ctl-01 for the lead. Continue only when the host has a proven clean close and the ledger reflects its last armed span.
next_observable: <exact pilot runner_receipt.json> for cq-ctl-01-s01-a1, then automatic desk and signed independent pilot PASS.
```

> The immediately preceding span was kit `<f2-stab-15 or f2-stab-16>` on pin B `6e9d42f1dd3d308bc9239143d0d634ab965e50e1`. It was launched with `--span-id <predecessor attempt ID>` equal to its typed issue's attempt ID. Its unchanged receipt SHA-256 is `<full predecessor receipt digest>`. The latest row in the shared attempt ledger is that same last armed span, and the ledger SHA-256 for this issue is `<full ledger digest>`. No unledgered work may run after that close. Hold the pilot if the three admission questions are unresolved, any identity differs, or the close cannot be proved.
>
> Use the separate clean detached ctl-01 checkout from the admission item. Verify `<issued kit path and SHA-256>`, `<pilot queue path and SHA-256>`, and `<standing rank above rank-4 stability, preserving higher priorities>`. Apply **Shared Start and check**, the actual-t0 plan and the 02:00–02:35 soak check. Use only L001,L002,L003. The CLI must re-prove the latest close and exact nanosecond bound using the shared attempt ledger. Launch once as the last act of a quiet activation. Do the close and automatic desk check, then the named independent F-3(c) and RL-197 four-view hand-read of stamps and counts. Keep span 2 held until PASS.

### Draft RUN_STATE item — span 2 L004–L012

**Heading** — MAGISTRATE — cl-ctl-01 span 2 L004–L012, pilot hand-read PASS, cq-ctl-01-s02-a1.

**Typed fields** — owner `magistrate`, status `ISSUED`, expiry `<finite issue expiry>`.

```text
owner: magistrate
wait: result_json_exists
deadline: <follow-up deadline at or after the launch fence>
on_early_or_refused: Read the verdict first. A missing receipt, refusal or unproven close holds ctl-01 for the lead. Continue only when the host has a proven clean close and the ledger reflects its last armed span.
next_observable: <exact span 2 runner_receipt.json> for cq-ctl-01-s02-a1, then restored close and final accounting.
```

> Pilot automatic desk and independent F-3(c) and RL-197 view checks are PASS at `<record references>`. Bind the PASS for the same kit and latest pilot receipt in span 2's queue row `pilot_pass_sha256`, and supply `--pilot-hand-read <PASS file>`. The latest receipt used for launch is `<last armed attempt ID>`, with embedded `span_id` equal to that ID. Its receipt SHA-256 is `<full predecessor receipt digest>`. The latest attempt is also the latest row in `<shared ledger>`, whose SHA-256 is `<full ledger digest>`. No unledgered span may have run between the pilot close and this launch. If a ledgered span intervened, prove that newest close and keep the pilot PASS bound to the actual pilot.
>
> Use the same detached ctl-01 checkout and issued kit. Verify `<span 2 queue SHA-256 and expiry>`, the actual t0 and standing rank. Run L004–L012 only. Keep L006 and L007 together. At the close record the final accounting and RL-198-amended blind disclosure. The first split leg's independent hand-read is owed before the look. The look's inputs and reservation gates stay with RL-197.

If an expiry or refusal occurs before a leg starts, the leg remains unspent. Audit round 4 found that expiry after ledger append can still leave a recorded attempt without a receipt. In that case hold the chain for the lead to reconcile the actual attempt and close proof before any reissue. Keep the evidence immutable and never add a ledger entry to evade a refusal.

The admission draft and both issue pointer templates parsed with synthetic witnesses through the typed-item writer.
