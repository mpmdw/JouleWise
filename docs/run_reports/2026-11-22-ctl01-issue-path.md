# cl-ctl-01 issue path — 2026-11-22

**Status:** ready for cold review as a data draft. Issue awaits the landed runner and queue-authority guard pin, the independent cold kit PASS and the lead's standing-ladder item. The MBP work belongs to the magistrate in a quiet session. This seat used public code, rulings, metadata and synthetic inputs only.

Mission M0 selected the lead's explicit [AGENT] task. The audit checkout started clean at RL-197, `1de85b0c1`, with no remote issue-path branch or PR. It fast-forwarded through RL-197a at `75526ed44` to RL-198 at `0a4d9d3cf`. The audit pointer was item 513 and the main pointer was item 531 when checked. Both kernels had no active stop card. Main items 532–533 authorize option C before W1. RL-198 §0 and §3.3 place it in separate P windows and preserve RL-197's ctl-01 kit, issue order and look. Main item 365 records dev-02 complete, satisfying RL-149 §2.5's predecessor.

## Merge plan for the lead

Snapshot against `main@82b93c157`. The common ancestor with `align/2026-11-14-kit-v1-1@6e9d42f1d` is `d842f697f`. Main is 1,831 commits ahead and the kit line is 1,634 commits ahead on its side. The kit line includes PR #812 (the qualification/t0 guard) at `6e9d42f1d`, but it contains neither ctl PR. PR #808's head `1f8541e4b` is 12 commits past that base. PR #900's head `9bb03a741` is another three commits on top. Both PRs are draft with 21 passing substantive checks each on those heads and are reported MERGE_READY on their present bases. Main has none of `joulewise/cadence/`, `scripts/cadence_legs_runner.py` or `scripts/launch_cadence_span.py`, and lacks the pinned ALIGN R1 runtime, endpoint and registration inputs. A direct retarget of PR #808 currently shows 3,559 files relative to its merge base with main.

1. First land a scoped cadence prerequisite PR **into `main`**, based on current main. Bring the RL-145 ALIGN runtime/registration and host integration needed by the cadence runner, then the campaign runner from PR #775 (`8bd31ae5a`), kit v1.1/span-reference layer from PR #788 (`9cbb365a6` before the qualification merge), and the qualification/recorded-t0 fixes already integrated by PR #812. Use `6e9d42f1d` as the comparison baseline for the combined closure. PR #775 currently targets `align/2026-11-13-rl145-build` and PR #788 targets `align/2026-11-14-campaign-runner`. Integrating a narrow prerequisite PR avoids promoting the divergent ALIGN tree or its unrelated W1 changes. Check the import and frozen-path closure and compatibility with current main, then get the integrated tree through the full suite. This port remains lead work.
2. Rebase **PR #808** from old base `6e9d42f1d` onto the main commit containing the prerequisite, retarget it to **`main`**, and land it first. Review the new diff against the original ctl delta and re-run the required full-tier checks and the independent executing gate on the final main-bound head. The queue-authority follow-up refreshes the old instrument-read wording in the runner instructions and draft refusal.
3. Rebase **PR #900** from its old base `1f8541e4b` onto main **after PR #808 lands**, retarget it to **`main`**, and land it second. Keep the old #808 head available until the #900 rebase and verify that the new #900 diff contains only its failed-envelope follow-up. Retaking the three-commit delta works even if #808 is squashed. Use fresh main gate ledgers for both PRs with the six Impact answers and five evidence rows. Keep the reviewed heads tied to their CI and executing audit evidence.
4. After PR #900, rebase the queue-authority delta in [PR #946](https://github.com/mpmdw/JouleWise/pull/946) from `9bb03a741` onto main, retarget it to **`main`**, and land it after its executing audit and final-head gates. Pin the kit to the **actual main commit containing all three**. `043b972f9` is the review pin for this draft. Earlier stacked heads lack at least one required delta. At the selected main pin, regenerate frozen digests with `scripts/cadence_legs_runner.py pin-kit KIT --commit MAIN_SHA --write`, verify the frozen bytes with `scripts/cadence_queue.py validate-kit KIT --repo RUNNER_CHECKOUT --batch-window 02:00-02:35`, and take new kit, index and queue hashes. Compare the pinned payload to the cold-reviewed draft. After the independent cold seat passes on the layout, capture/consumer balance and bytes, the lead sets `status: issued` and `ruling.authorizes_spans: true` in the final kit. Validate those final bytes before hashing and binding them in the index and authorized queues.

**Measurement dependencies on PR #795:** none. The look depends on #795 through freeze 2 and the instrument read. There is no #795 dependency in the ctl runner/kit stack.

PR metadata: [#775](https://github.com/mpmdw/JouleWise/pull/775), [#788](https://github.com/mpmdw/JouleWise/pull/788), [#812](https://github.com/mpmdw/JouleWise/pull/812), [#808](https://github.com/mpmdw/JouleWise/pull/808), [#900](https://github.com/mpmdw/JouleWise/pull/900).

## Kit and queues

The [review kit](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/ctl-01/kits/cl-ctl-01.draft.json) uses the runner's `ctl.generate_legs` and `pin-kit` tooling. The [KITS.json row](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/ctl-01/KITS.json), [pilot queue](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/ctl-01/queues/ctl-01-s01.draft.json) and [span 2 queue](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/ctl-01/queues/ctl-01-s02.draft.json) name the same draft bytes. Kit SHA-256 is `39ad1bd43719af42942207c2109ce6099b944d74146a55046611549c1d3f4e3a`. The kit is `draft` with `authorizes_spans: false`. Each queue is halted with a review-only date and expiry and contains just one span. The lead sets the actual finite expiry, earliest local date and standing notice at issue. For the active span 2 queue, the lead also sets `pilot_pass_sha256` on its selected row after the hand-read. Separate queues keep the generic queue reader from chaining through the hand gate.

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
