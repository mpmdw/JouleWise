# Issue hp-02 on the magistrate’s filler ladder

**Threat model · lead ruling, 20 November 2026, 09:52 PST.** The lead and magistrate are the trusted writers of RUN_STATE, custody records and Checks. They are honest and can make mistakes. The reader must catch a stale selection, missing or contradictory operational evidence, a refusal, failed or unproven restoration, and an expired authority. The owner exposes its complete current public inventory during the serialized desk turn. An unavailable owner or unestablished coverage holds HP. Deliberately forged records are outside this decision, including the round-four instrument opening/validity edits, mislabelled daily credit, a Check crafted to contradict native evidence, and fabricated orphan or inconsistent receipts. Existing agreement checks continue to apply.

**Evidence order.** For each fact, use its highest published RUN_STATE item number or the highest sequence in its owning ledger. Scan the complete scoped inventory, including entries omitted by a convenience list. An old admission, clean Check or clearance cannot override a newer applicable revocation, refusal or failed/unproven recovery. Each independent outstanding host fault requires its own linked proof. Under the 11:58 ruling, a failed or unproven restore also requires a typed lead clearance naming the failure and a successful later observation. The Run block fetches origin/main and reviews every item since issue at the fetched commit. Run opens the live look ledger and both owners again. Their agreed history must preserve the sequence and event prefix that Start published. A repeat read from rolled-back copies refuses.

**Decision for the lead, 20 November 2026.** Use the same four artifacts as f2-inst and f2-stab: one typed RUN_STATE item, the activation’s start-check output, its standard Run block, and its operational Check after the fence clears. Issue one attempt for one span. Queue-b opens Saturday 21 November at 00:00 PST, when the date’s rank-1 base leg falls due. R-c rules out HP throughout that opening interval. The first HP start the OS-window rule permits is 02:35 PST, subject to rank, occupancy and the remaining checks.

The round-five reference check resolved main to `f4be023f9cb50412ebf799a73e51e103c8499fc0` and audit to `63219037052cc7ba066975f3487aef9887bc173c`. The 25 bodies for items 422, 447 and 461–483 match the lead's decision snapshot at `c05bcfc45e4625a99e022c8809bd2f97bbeac0c3`. RL-190 retains the line-2 carry-forward. The immutable successor commit below supplies queue-b and the delta. Live use requires the lead's admission of those bytes and current evidence on the issuing desk. [Main ladder and custody-template references](https://github.com/mpmdw/JouleWise/blob/c05bcfc45e4625a99e022c8809bd2f97bbeac0c3/RUN_STATE.md) · [Audit directory at intake](https://github.com/mpmdw/JouleWise/tree/04d8aa778fe6dc6ec544e86b4730a986020fd368/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203/hp-02)

Of the 30 verified audit findings, **14 still apply** under this design. The other **16** concern the removed automation. The audit table identifies the evidence or handoff check covering each surviving finding.

## Where the decision is made

The lead supplies the exact item bindings and authority. At a clean close the magistrate reads the administrative facts **once for this dispatch**, directly from committed or public records. Cite the main/audit commits, item numbers, record IDs, receipt digests, source coverage and as-of time beside each result in the ordinary `start-check.out`. A single main item may supply multiple facts. The desk uses its customary preflight, census, copy and live host checks. A custody owner can publish a scoped operational attestation. The start-check reads that public attestation without opening protected data. A filename search, a caller-set `yes` or an old “currently eligible” flag has no authority.

A passing start-check identifies the exact entry, permitted dispatch time, argument, fence and Check. The magistrate publishes the filled typed item and finishes the ordinary mail/bookkeeping, then runs the template’s actual-time replan and final host verification as its last act. Run reads the current published item, checks its bound inputs, verifies the host and reopens the authoritative look view. If the time leaves their proven range, an input changes to the magistrate’s knowledge, an overriding directive arrives, or another span intervenes, discard this dispatch and take a fresh standard start-check. A failed check ends the decision. A fresh activation reads the owning records, including outstanding stops and prior attempts. Exclusive desk dispatch and the ordinary launcher fence supply serialization. The next authorized HP span requires its own item and Check. There is no reusable HP Start receipt.

## Preconditions and their authorities

| Check | Evidence and decision at the magistrate’s start-check | Source rule |
|---|---|---|
| 1. The HP look is still available | Read the latest ledger sequence of the `lm-hp-01` execution/reservation history, including failed or interrupted starts. Read the MBP and AIR owners’ operational attestations from their fixed public roots. Require exact agreement with their ledger entries and the ledger’s ordered history of this look. All routes must report zero executions and active reservations through the read. Resolve a reservation by its own recorded disposition. A genuine execution bars this block. Only the lead’s evidenced correction of a mistaken attestation can retract a false report of execution. A missing row in `docs/process/cadence/looks/LOOKS.json` cannot establish the negative. | RL-174 B, RL-190 §§2.1–2.4, especially §2.4; gate-suite lead ruling Q1 for correction authority. |
| 2. No hp-01 leg shares HP’s local t0-date | Use the complete receipt-backed census of `cl-hp-01` on the as-run kit. Reconcile s01, s02, s03 against RS335/337, 339/340 and 342/343, summarized in 344. All three t0s are on 2026-11-15 in America/Los_Angeles. Verify scope/completeness against the current history, compute dates from span t0s and exclude the candidate date. A missing span, blank string, empty list or conflict with Nov 15 withholds HP. The close can cross midnight. | RL-174 B, RL-175 D.3, RL-179 F-1, RL-190 §2.4. |
| 3. LINE2_OK | Verify and name **all three** records below in the typed item. Preserve the admitted independent delta and inherited Class A smoke from RS337–338. | RL-165 §5, RL-174 B, RL-175 D.3, RL-190 §§2.1–2.2. |
| 4. Admitted bytes, finite queue, unspent attempt | Use the clean detached v1 runner, staged kit and separately admitted queue-b in the binding table. Check committed and staged bytes, frozen materialized paths, native kit/queue validation, the highest-numbered applicable queue decision and all scoped holds, exact sequence, block, plan id, attempt, leg order and unused output. Require a complete 12-leg history in the 3+4+5 order including any other issue or queue version. Derive spent legs from the published issue/Check pairs and the MBP receipt inventory. The roster summary must match that set and the required prefix. Each receipt belongs to one exact plan and integer attempt. Each completed attempt consumes its identity once. An ambiguous launch or spent leg requires disposition. The queue opens inclusively and expires exclusively. Require ≥600 s left when invoking the launcher and a supported latest t0 strictly before expiry. Use the same margin for any other finite expiry relied on for admission. The issue carries queue-b’s exact `expires_at` string and its integer UTC epoch in the typed expiry field. Run checks both bindings and evaluates the 600-second margin again at its final clock. | RL-174 B, RL-175 D.3, RL-179 F-6, successor build decision 3 and r4 R1. RS447’s December F2 queues have their own scope. |
| 5. Full occupancy and every pending dated start fit | Prove the chosen explicit window, complete capped work, restore/clean close and outer clearance at the actual pin. Reserve the entire item fence once, plus only transition outside it. Work backwards over every outstanding counted start, including only the outstanding half of a split block. Keep the pin’s start windows, floors, transitions and local dates. A final start at 23:59:59 meets its date even if the span finishes tomorrow. A miss cedes. Unknown or unsupported bounds withhold HP. Arithmetic and regression edges appear below. | RL-179 F-1/F-2, register rows 1–2, RS422/447, RL-190 §2.3 and FREEZE-ADDENDUM. |
| 6. Latest clean host close, current mode and restore | Bind the latest MBP Check across campaigns by its original RUN_STATE number or owner ledger sequence to its receipt, fence clearance, all restore/readback lines, proven feed/group stops and independent census. Read each historical Check’s actual restore and feed/group fields. An unproven result holds even across an unrelated clean Check. A restore failure requires a typed lead clearance naming that failure and a strictly later successful observation for the same plan, integer attempt, host, pin, Check and receipt. At Start and immediately before launch require AC/float, Automatic (exact AC-profile powermode 0), approved 0/2 sudo rules, clear marker including dangling link, free host/night lock and desk fence, valid measurement mode, network time off/frequency zero, disk, meter, collector, both censuses and no veto or maintenance. See the host and Check procedure below. | RL-157 §§3/8, RL-165 §§5–7, RL-174 C, RL-175 D.3, RL-179 F-2/F-5/F-6/F-9, RS338/422/423/431/442/443. |
| 7. Prior HP Check | s01 requires the latest clean host Check, with no required qualification or HP predecessor. For s02 require the magistrate’s operational HP Check for s01; for s03 require s02, with s01 in the spent history. Match host, kit, pin, span, attempt 1, ordered legs, receipt hash, successful automatic desk, restoration, close time and cleared fence. A newer intervening F2 Check is additive. The HP Check cannot be later than the latest host Check. Reconcile every native receipt and every published HP issue, including historical Checks. Match both item numbers, digest, identity, ordered roster, end time and outcome across the native projection and the operational Check. A dirty/ambiguous predecessor withholds the next HP span. | RL-175 D.3, RL-179 F-2/F-6, ITEM-GATES-SPEC §§1/7/9/10. |
| 8. HP wins the current ladder | Apply effective READY and eligible counted work first, then the date’s first eligible base stability leg, then eligible finite instruments, then HP, then further stability. Rank counted work from the dated programme and desk’s matched pending positions, with their own dates, readiness, legal starts and linked holds. Cede to any feasible counted position in the handoff interval. Source-entry identity for kit dispositions is the original `(source, entry)`. Apply RS480’s instrument diversion and R-c’s independent HP work exclusion. | RL-179 F-4, RL-180 §2(b), RL-190 §1.4, RS422/447/463/**464/472/480**, with RS465/471/482/483 for the instrument status. |

[Rulings through RL-190](https://github.com/mpmdw/JouleWise/blob/04d8aa778fe6dc6ec544e86b4730a986020fd368/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22383-L22423) · [Earlier item contract](../d-hp02-post-r1-issuability/ITEM-GATES-SPEC.md) · [Occupancy addendum](../d-hp02-full-occupancy-spec/FREEZE-ADDENDUM.md)

### Binding and the three line-2 entries

Let `H` denote `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203/hp-02`. All three spans use the following bindings.

| Object | Identity |
|---|---|
| Measurement runner | `dd206025abb30fd5c07515cd4b34b3e653174810`, `cadence-legs-v1` |
| Kit | `H/cl-hp-02.json`, campaign `cl-hp-02`, SHA-256 `7693b8293b42b8ba20cbd321e201974745b172dc53c4f1397d2c1494f38fbe66` |
| Queue | `e3eaa282f9d4cea3b579eeb7bde989ff897df45e:H/queue-b.json`, `cq-hp-02-b`, SHA-256 `078eb24c3149f2a7bc522a432098e51e21bd36278d288b0f41efbb5d57da528f` |
| Finite interval | Each `not_before` is the LA date `2026-11-21` (00:00 PST). `expires_at=2026-11-30T00:00:00-08:00`. The queue’s invocation cutoff alone is Sunday 29 Nov 23:50:00 PST, inclusive. R-c independently excludes HP work at that clock because it crosses the next day’s OS window. |
| Ordered entries | Seq 1 `hp-02-s01` L001–L003; seq 2 `hp-02-s02` L004–L007; seq 3 `hp-02-s03` L008–L012. Block `hp-02`, attempt 1, `rerun_of=null` throughout. Plan IDs `cq-hp-02-s0{1,2,3}-a1`. |
| Plan worst / item fence, seconds | s01 16,650 / 18,110; s02 19,350 / 20,810; s03 22,050 / 23,510. |

1. RS338, commit `6640a66719a2ff1f8cc38dbce3e8231f419e79d8`, four-part line-2 disposition for hp-01 kit `7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965`. The finished run 43673985768 has the same twelve reds as 43600776368, each passed at #777 head in 43601158271, and the frozen-path and meter comparisons are recorded in 338. Preserve that disposition as recorded.
2. `e3eaa282f9d4cea3b579eeb7bde989ff897df45e:H/HP02-DELTA.md`. The independent seat found the hp-02 frozen block byte-equal to hp-01’s, including all 37 paths on the same pin. The new seed is 2026111601.
3. Line 2 for `cl-hp-02` (`7693b829…be66`) is `cl-hp-01`'s record under RL-165 §5; no frozen byte differs (RL-190 2).

[RS338](https://github.com/mpmdw/JouleWise/blob/6640a66719a2ff1f8cc38dbce3e8231f419e79d8/RUN_STATE.md#L8153) · [Delta at its cited commit](https://github.com/mpmdw/JouleWise/blob/e3eaa282f9d4cea3b579eeb7bde989ff897df45e/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203/hp-02/HP02-DELTA.md) · [Queue-b](https://github.com/mpmdw/JouleWise/blob/e3eaa282f9d4cea3b579eeb7bde989ff897df45e/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203/hp-02/queue-b.json)

### Rank at the proposed t0

* The dated counted programme used by Check 5 also supplies Check 8. For each pending position, intersect its plan windows with the local date and readiness floor, subtract the starts covered by its effective holds, and test for an integer start in the dispatch interval. Cede on any match, even if the desk summary says exhausted or a later counted start could still fit. An inconsistent summary with no present cede holds HP for reconciliation.
* RS464 / RL-190 §1.4. At rank 1 take the lowest-numbered eligible kit from f2-stab-01..14 at `2d347f721`, first unrun leg in roster order. “Spent today” requires an identified completed base-kit leg on that pin and LA t0-date, with its Check. If no base entry can arm, cite the dated census of that pool and the grounds. Kits 15/16 at `6e9d42f1d` never spend rank 1. Finishing yesterday’s in-flight span today does not spend today’s rank 1.
* RS447/463/465/472. Examine inst-01 → 02 → 03, then any later kit with an executing delta PASS recorded on main. Cite a kit-specific queue position and disposition or terminal Check for each. -03 follows -02’s last clean Check without waiting for midnight. Prefer a pair when it fits, else test the lawful single. Test the instrument’s own pin and permitted arguments. Include the 13:15 reopening when an instrument is still outstanding. Exhaustion with a recorded nonadmission grants no redo. Reuse a shared source document only when it has an independently identifiable entry for each kit.
* RS480. For finite instruments also exclude any proposed worst-work interval `[t0,t0+worst)` overlapping the local 02:00–02:35 OS window, including tomorrow’s window. Where that rule diverts a pending instrument, follow 480’s explicit order: due base rank 1, else an eligible 15/16 leg, else wait for 02:35; resume instruments at the first clean close. R-c extends the same work exclusion to HP even when all instruments are exhausted. Test the entire HP planned work interval for every possible start through the latest t0, independently of the chosen argument and the occupancy arithmetic. An end at 02:00 or a start at 02:35 touches the boundary legally. At 01:55 with nothing else eligible, wait until 02:35 local and re-rank. Keep 15/16’s no-window midday gap and the normal rank-4 base-kit order. A gap on the instrument pin alone proves nothing about HP.
* Cede to an eligible higher rung now. Protect future counted dates by the feasibility calculation below. A legal launch before midnight may finish the next day. The first eligible dispatch of the new day is ranked anew. R1 is complete; F0 is retired. An HP-only hold allows the magistrate to use the next lawful filler. A host stop applies to all affected work.

## What to insert in the magistrate’s templates

Use the activation layout documented by RS461 and RS483. Keep the ordinary RC-checked preflight, last-act Run, Check and copy steps. Put the following Python in the activation beside `inputs.sh` as `hp_checks.py`, outside the frozen checkout. The three calls below belong respectively in the ordinary start-check, Run and the existing reservation procedure. Each shell exits on failure. The start-check result is written by the existing activation script only on success. Paste its single JSON line unchanged after `HP-DISPATCH ` in the typed item. Keep the human-readable source citations and command logs in the activation. Stage one exact kit path under exclusive desk custody, write-once through launcher/runner consumption. Never reuse an issued attempt on retry.

```bash
set -euo pipefail
cd "$REPO"
"$PY" -IB "$ACT_DIR/hp_checks.py" start > "$START_RESULT"
```

```bash
set -euo pipefail
cd "$REPO"
"$PY" -IB "$ACT_DIR/hp_checks.py" run
```

```bash
set -euo pipefail
"$PY" -IB "$ACT_DIR/hp_checks.py" before-reserve
# In this same exclusive lead-authorized turn, perform the ordinary reservation.
```

**Trusted inputs.** Export `REPO, PY, KIT, KITS_ROOT, QUEUE_FILE, AUDIT, CUSTODY, OUT, CAMPAIGN_ROOT, HOST_ID, MBP_PUBLIC, AIR_PUBLIC, ACT_DIR, ACTIVATION, START_RESULT, PUBLIC, DESK, DESK_TOOLS, F2_HOST_CHECK, SEQ` from the ordinary activation settings. For Run also export `ITEM, LEGS, ARG, MAGISTRATE_PID`. `OUT` is the full, unused UTC-stamped attempt path chosen before issue. On the MBP the campaign root is `/Users/edr/campaign-out`. `DESK` has the desk's authenticated main remote and its current objects. `DESK_TOOLS` contains that main's verified scripts including `run_state_items.py`. `F2_HOST_CHECK` is the existing verification-only body of the F2 host check, including RCs and the live checks listed under “Before dispatch”. An unavailable host check fails the activation. The authority paths, shared real fence parent, protected stage and current public view are fixed by the issuing desk independently of the candidate. A source read failure, incomplete custodian response or ambiguous program exit is a refusal. Positive fixtures use disposable equivalents.

**Evidence handoff for public prose and custody records.** The names below specify the reader's input format for this activation. They describe extracts the competent record owners can supply from their existing public records. No such bundle or admission is claimed to exist today. The desk may transcribe an authenticated record once where it exists only in prose. Before accepting an extract, the magistrate opens the cited current record and entry, verifies the owner, scope, original date/pin/position, receipt or planner reference, and reconciles all later items, typed dispositions, outstanding refusals and directives. A custodian supplies a public operational attestation for information held behind a custody boundary. An unverified transcription cannot be used. The source and entry in each extract locate that exact evidence; `sha256` binds the inspected projection. Hashes alone confer no authority.

* `PUBLIC/basis.json` is the current owner-reviewed inventory for this single desk activation. The public roots are obtained by the desk, independently of the kit or a proposed list of eligible work. `main` is the selected current main revision. `from,through` certify the interval actually covered for this decision, including any scheduled changes, using offset timestamps. The desk chooses and documents a smaller interval if needed. This creates no standard kit age. `records[id]` maps each evidence ID to its `source,entry,sha256`. `PUBLIC/records/<sha256>` contains the immutable public operational extract, with matching `id,source,entry`. A source is a commit/path or owner-controlled public record locator, with an identifiable entry or receipt. A stale mirror is insufficient. The fields consumed below are the contract. Example wires, including a complete synthetic positive for each sequence, are in the verifier.
* Each entry of `records` also has a stable logical `series` (an array of strings) and original publication `order`, for example `{"series":["host-check","mbp"],"order":{"RUN_STATE":485}}` or `{"series":["queue","<queue sha>"],"order":{"ledger/lead-admissions":12}}`. The owner identifies the same fact across revisions, including when its record ID, source document, position or state changes. Use one comparable owner order per series. Use the item number on main for a RUN_STATE decision. Use the original ledger sequence for a ledger decision. A transcription timestamp, physical listing order or new local counter supplies no order. The desk reconciles the **whole** inventory against the current main and owner ledger heads, including active stops, before attesting it complete. Unknown coverage, missing coordinates, a tie or mixed coordinate systems withhold HP.
* Ordinary selectors such as timing, the roster, daily credit for a date, and each kit’s position use their latest revision. The sorted `["queue",queue_sha]` and `["host-check",host]` histories must cover the full queue-decision and host-Check lists. Historical Checks and immutable source citations supply the audit trail. Every earlier host fault is tested even when the most recently published Check is clean. Each recovery series is `["recovery",host,check_id,fault]`. Use recovery observation time within that series. Retain each failed observation until the lead clears it explicitly. The owner transcribes a failed or unproven recovery into its actual Check or linked recovery record, retaining all failed return codes and readbacks. A host Check can also report a host-scoped state of `refused`, `revoked`, `held`, `failed-recovery` or `unproven-recovery`. A lead clearance of a host refusal names the original plan and attempt. For a kit-only refusal the owner records the affected kit as the subject. Administrative revocations, refusals and holds applying independently of those Checks use `kind="scope-disposition"`, `scope` of host, queue or kit, the exact `subject`, a stable `cause`, `owner` and `state`. Its series is `["disposition",scope,subject,cause]`. The latest `revoked`, `refused` or `held` blocks. A published lead clearance carries `state="cleared"`, the preceding disposition ID in `resolves` and the lead’s reason. A clearance applies only to that cause. The separate host recovery still requires its operational proof. These are projections of ordinary records at their owners. All HP checks are read-only.
* `PUBLIC/look.json` is the live execution ledger. `MBP_PUBLIC/look.json` and `AIR_PUBLIC/look.json` are the respective custody owners’ live public views. The desk configures and authenticates these three locations independently. Each custody document identifies its route, look, kit and activation, attests `complete: true`, and supplies its dated `history`. The ledger carries that owner’s exact projection under the same route and its own register entry. All three histories describe the same `lm-hp-01` event stream, including released reservations and evidenced corrections. Sequence, event identities, dates, dispositions and outcomes must agree. Each event has an `at` epoch. Each history, its custody attestation and the ledger have a `recorded_at` epoch. The history must precede or coincide with its attestation, and the attestation with the ledger that cites it. Reading an old Start copy, republishing AIR as MBP or losing access to an owner withholds HP. The owner must expose the current state under the same serialized turn used by all reservation writers.
* **R-d ownership.** The lead and analysts control every reservation route. Serialize the HP start-check through publication against reservation writers using the ordinary lead turn. All look executors, including those on the other custody root, must inspect the same canonical MBP fence and current published issue while holding that turn through their reservation write. The typed item itself is the HP issue marker. A conventional local mirror, when present, also bars reservation. The prohibition begins at issue and survives fence removal, expiry, void and supersession until the magistrate’s operational HP Check explicitly closes the identified item. Keep the original issue open until its Check. If a terminal transition already prevents a typed set closing it, record a separate CLOSED operational Check, using the exact heading `<new number>. **Magistrate HP CHECK #<original number> for <complete plan_id>.**`. Use that same heading on a normal typed Check that closes the original. A previously terminal issue may be Checked in a later CLOSED item without a second closing set. An earlier standalone note, a different attempt or a different item number gives no clearance. Read the published main at the reservation clock. In this procedure CHECKED means the exact magistrate Check is already published and the original is terminal at that clock. For a separate Check, the administrative transition must already have been published at the Check’s timestamp, or the issue must already have expired. A future Check, a backdated Check and a future receipt all refuse. For a receipt-bearing Check, reconcile its digest and native close against the MBP’s current public inventory. An ordinary pre-launch disposition with no receipt may release after its exact operational Check when the MBP inventory also shows none. Start records the agreed look sequence, SHA-256 of the ordered event prefix, and the ledger, owner and projection publication times. Run synchronously reopens all three authoritative endpoints while the exclusion is in force. Refuse a lower sequence, different prefix, regressed publication time, intervening reservation or any current execution/reservation. A fresh read may return the same unchanged history. A refused launch is reconciled and Checked before the exclusion is released. If the desk cannot establish shared visibility and serial ownership for **all** routes, hold HP. There is no HP journal or lock service to deploy.
* For checks 2–4 and 6–7, transcribe the three as-run hp-01 t0s and their receipt identities, the exact three RL-190 entries, the latest **lead** queue decision including any later amendment/revocation and all relied-on finite expiries, and the all-queue 12-leg spend history. For the MBP, enumerate Checks across campaigns in their original publication order, including each applicable HP Check. Reconcile outstanding fault/stop and recovery dispositions before naming the latest Check. For an unproven restore keep the host held through independent recovery proof and the typed lead clearance below. A Check reports its restored AC value, feed/group disposition, receipt hash, desk verdict and any residual independent stop. For a fault, record the original plan ID, positive JSON integer attempt, runner pin, Check ID and receipt SHA in both the Check and its linked public disposition. The disposition names the fault and its proof digest and time. For restore, prove successful pinned `restore-owed` on the clear job/fence and independent Automatic/marker/lock/measurement/network readbacks. For a group stop or group REFUSAL, bind the original feed/PID-start/group identities to positive stop proof, independent absence and mode-0 readback. Each failed or unproven restore and each unsuccessful recovery requires a typed lead clearance. A restore disposition cannot clear an independent group stop. A subsequent clean Check alone clears neither. The desk verifies the RS338 and delta commit/path once against the identified original records and uses the literal §2.2 sentence.
* For check 5, the lead supplies the complete ordered dated programme (both halves of split blocks, each with separate disposition); the scheduling desk supplies its independently enumerated outstanding positions and pins. “None” requires positive, matching, complete enumerations of the owning sources. Each pending row carries the first feasible start, dated integer-second intervals from **its own** pin’s plan, and its worst duration through the transition to the next start. The desk verifies the interval endpoints and the referenced plan against that counted span. For a pending position, a public `hold_refs` list names any effective counted holds. Each hold must match the position, date, pin, queue entry and plan reference and identify its owner, disposition and inclusive blocked integer starts. An omitted list removes no legal start. The same remaining legal intervals drive immediate rank and the backwards deadline. The timing source names pin, MBP, span, permitted arguments and proved joint bounds. `runner` bounds T through the runner replan, `guard` ends at the post-dwell remaining-work check, and `selector` ends at the actual soak selector after journal writes. `dispatch,inner` cover overshoot and the child's OS check. `pre_leg,leg_overshoot,tail,close,outer` include service outside the attempt caps. `transfer_outside` charges only the subsequent transfer/transition outside the fence. `call_tail,runner_tail` cover final clock read to invocation and runner respectively, including process startup. Unknown timing holds HP.
* For check 8, obtain the admitted instrument list from the current lead admission register. Independently locate one actual queue position or terminal entry for every eligible pool and pin, including all 14 base kits, 15 and 16, READY and counted. Use RS464’s completed dated base receipt where available. For each kit row, independently resolve its position against the original authenticated queue entry or terminal Check, retaining that record’s pin, queue SHA, kit SHA and position. In the candidate row `windows` are the inclusive effective **administrative** start ranges from the source queue dates, readiness floor and dispositions. Never transcribe last-sampled planner eligibility into that field. A held/exhausted/unavailable disposition must cover the whole requested interval; a temporarily closed position with a known reopening is available with its dated windows. Use `sizes=[2,1]` when a pair and its lawful fallback are available, otherwise `[1]`. The reader derives the actual rank intervals from those very same rows, the two RS463 pins, the specified work durations and the RS480 boundaries. A new kit on a different pin requires its own verified planning rule before HP can outrank it. READY uses its source availability. Counted work comes from the matched dated positions. The optional aggregate counted row can expose a conflict but cannot suppress a feasible start. `daily_completion=null` selects the complete base pool, never “already spent”. At an RS480 diversion, prefer due base, otherwise eligible 15/16; if neither can start, wait until 02:35 and re-rank. R-c also bars HP independently of instrument exhaustion.

**Run decision review (P1).** In the ordinary Run turn the magistrate fetches the authenticated main ref and reads the complete numbered items in `git show refs/remotes/origin/main:RUN_STATE.md`. For every intervening item, read the heading, body, transitions and any cited disposition needed to establish scope. A queue-b or hp-02 revocation, a cl-hp-02 hold, or a halt or refusal on this MBP ends this issue’s dispatch, even if a later item lifts it. Apply the same review to an intervening item published between Start and issue. Missing, ambiguous or inaccessible evidence holds. For intervening prose, use `"$PY" -IB "$ACT_DIR/hp_checks.py" run-review > "$ACT_DIR/run-decisions.json"` as the review step of the same Run turn. It fetches main, displays each complete item on stderr and writes a worksheet with the source bindings filled. The magistrate fills only the disposition and grounds after reading each item. Its fields are the reviewed Git commit in `head`, the integer HP issue in `issue`, and `items` keyed by every intervening item number. Each entry carries `disposition` (`block` or `unaffected`), `grounds` giving an exact passage identifying its disposition or unrelated scope, and `item_sha256` from the full reviewed item. For that digest, split the fetched document with Python `splitlines()`, take the heading through the line before the next heading recognized by `run_state_items.heading_lines` (or EOF), join those lines with LF and hash the resulting UTF-8 bytes. Do this as part of Run under the ordinary serialized turn. The literal block fetches again, reads the document at that exact commit and requires exact coverage. A different head requires a new review. An issue with no intervening decision needs no review file. Start checks that its inventory review covers publication of every typed decision through its head. Run repeats that coverage check on the published Start so an issue created from a stale pre-issue review also refuses.

**Typed host clearance (P2).** The lead records the clearance in a CLOSED typed RUN_STATE item with owner `lead`. For each failure it clears, include one line beginning `HP-HOST-CLEAR ` followed by a JSON object with `host,plan_id,attempt,pin,check_id,receipt_sha,failure,proof`. The first six fields identify the original Check. The last two are the exact immutable inventory IDs of the failed observation (the original Check ID in the inventory when it reports the failure) and its successful independent operational proof. For multiple failures list each ID, including a later failed retry. A later proof may cover multiple earlier failures on that attempt if the lead names each. Its observation must strictly follow each failed observation and be published by the lead item’s clock. The lead may cite a successful magistrate repair. Filing a repair, refreshing the inventory, or filing an unrelated clean Check leaves the halt in force. Start and Run both scan the full recovery history and read the actual typed lead item on main.

**Evidence agreement and dates.** Each source gives the timestamp of its original entry in `recorded_at`. Every accomplished event must be at or before its source record, each cited record at or before the item or projection reading it, and each reading at or before the action clock. Future schedule endpoints such as `through`, `allowed_starts` and queue expiry describe prospective permissions. A later recovery or Check can cite an earlier fault or issue. Its proof becomes usable only after publication. `agree()` compares complete typed values across the readers. Required affirmative flags accept only JSON `true`. Explicit clearance negatives such as `reserved` accept only JSON `false`. The timing authority may list exact certified window strings or supply a window-to-boolean map. Only an affirmative grant for the selected argument authorizes it. Run compares that same grant from the published issue and Start result.

**Attempt and receipt evidence.** The MBP custodian publishes `MBP_PUBLIC/hp-receipts.json`, its current complete public HP receipt index, with its positive integer head sequence in `ledger_seq`, for this host and kit, including a positive empty index for s01. `basis.hp_receipt_inventory` names the same dated index in the activation inventory. Each `receipts` entry is a public native-span projection keyed by its immutable record ID. It includes plan, integer attempt, host, pin, kit, span, ordered legs, native digest, close time, result and original publication time. The magistrate verifies each projection against the owner’s receipt metadata. The Check has a separate source, the exact `issue_item` and `check_item`, and its `receipt_ref`. In the published operational Check, cite an available native digest on its own line as `HP-RECEIPT <64 lowercase hex digits>`. A pre-launch refusal with no native receipt records the disposition in the standard Check. It cannot supply a spent predecessor. A duplicate, omitted or orphan receipt or Check withholds HP. The latest roster extract must cover the cited Checks. A new output path, clock or activation never reopens an attempt. Any further attempt requires its own authorized queue entry and typed issue. Queue-b specifies attempt 1 for each of the three spans.

The numeric fields have two wire types. Counts, item references, sequence and attempt numbers, mode readbacks, recovery exit codes, instrument roster sizes and counted-window endpoints require JSON integers. Numeric clocks, bounds and durations accept finite numbers. Both categories exclude booleans. The canonical typed-item validator checks its header and transition numbers. Run compares the typed dispatch payload with the successful Start output without Python's boolean/integer equality shortcut.

The code below is the complete HP insertion. Host and launcher commands in it belong exclusively to the operational desk. The reproduction harness substitutes those external effects and runs the remaining code literally.


```python
import hashlib
import json
import math
import os
import re
import stat
import subprocess
import sys
import time
from datetime import date, datetime, time as wall, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

PIN = "dd206025abb30fd5c07515cd4b34b3e653174810"
SRC = "e3eaa282f9d4cea3b579eeb7bde989ff897df45e"
H = "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203/hp-02"
K = "7693b8293b42b8ba20cbd321e201974745b172dc53c4f1397d2c1494f38fbe66"
K1 = "7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965"
Q = "078eb24c3149f2a7bc522a432098e51e21bd36278d288b0f41efbb5d57da528f"
BASE = "2d347f721552fe03bdd19f113e7bad7a7c24908e"
PIN_B = "6e9d42f1dd3d308bc9239143d0d634ab965e50e1"
RS338 = "6640a66719a2ff1f8cc38dbce3e8231f419e79d8:RUN_STATE.md#338"
QUOTE = "Line 2 for `cl-hp-02` (`7693b829…be66`) is `cl-hp-01`'s record under RL-165 §5; no frozen byte differs (RL-190 2)."
LINE2 = [RS338 + " " + K1, SRC + ":" + H + "/HP02-DELTA.md 37 frozen paths equal", QUOTE]
LA = ZoneInfo("America/Los_Angeles")
ROSTERS = [[f"L{i:03}" for i in g] for g in (range(1,4), range(4,8), range(8,13))]
WINDOWS = ("02:00-02:35", "13:14-13:15")
E = os.environ

def need(ok, message):
    if not ok:
        raise ValueError(message)

def pairs(rows):
    result = dict(rows)
    need(len(result) == len(rows), "HOLD duplicate key")
    return result

def read_json(data):
    def invalid(value):
        raise ValueError("HOLD nonfinite JSON " + value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)

def number(n):
    return type(n) is int or (type(n) is float and math.isfinite(n))

def integer(n, expected):
    return type(n) is int and n == expected

def agree(reason, first, *others):
    """Compare complete JSON values, including wire types, from independent readers."""
    def canonical(v):
        return json.dumps(v, sort_keys=True, allow_nan=False, separators=(",", ":"))
    need(others and all(canonical(v)==canonical(first) for v in others), reason)
    return first

def flags(row, required, reason):
    for key in required:
        agree(reason, True, row[key])

def recorded(epoch, ceiling, reason):
    need(number(epoch) and number(ceiling) and epoch<=ceiling, reason)
    return epoch

def stamp(s):
    dt = datetime.fromisoformat(s)
    need(dt.utcoffset() is not None, "HOLD timestamp without offset")
    return dt.timestamp()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def sha(s):
    return isinstance(s,str) and re.fullmatch("[0-9a-f]{64}",s) is not None

def named(s):
    return isinstance(s,str) and bool(s.strip())

def ids(entries):
    need(type(entries) is list and all(named(s) for s in entries)
         and len(set(entries)) == len(entries), "HOLD incomplete or duplicate inventory")
    return entries

def path(name):
    return Path(E[name])

def cmd(*args):
    return subprocess.check_output(args, cwd=path("REPO"))

def absent(file):
    # Open the actual directory first. Only ENOENT on this final name means absent.
    fd = os.open(file.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        try:
            os.stat(file.name, dir_fd=fd, follow_symlinks=False)
        except FileNotFoundError:
            return
        raise ValueError("HOLD present " + str(file))
    finally:
        os.close(fd)

def current_items(now, *, fetch=False):
    import run_state_items as rs
    desk = path("DESK")
    if fetch:
        cmd("git","-C",desk,"fetch","--no-tags","origin","refs/heads/main:refs/remotes/origin/main")
        head = cmd("git","-C",desk,"rev-parse","--verify","refs/remotes/origin/main^{commit}").decode().strip()
        agree("HOLD fetched main mismatch",head,cmd("git","-C",desk,"rev-parse","FETCH_HEAD").decode().strip())
    else:
        remote = cmd("git","-C",desk,"ls-remote","--exit-code","origin","refs/heads/main").decode().split()
        need(len(remote)==2 and remote[1]=="refs/heads/main", "HOLD current main")
        head = remote[0]
    need(re.fullmatch("[0-9a-f]{40}",head),"HOLD current main")
    raw = cmd("git","-C",desk,"show",head+":RUN_STATE.md").decode()
    parsed = rs.parse(raw)
    need(parsed.top_line is not None and not rs.validate(parsed), "HOLD invalid RUN_STATE")
    lines = raw.splitlines()
    headings = [n-1 for n,_,_ in rs.heading_lines(raw)]
    items = {}
    issues = {}
    attempts = set()
    for item in sorted(parsed.items, key=lambda i:i.number):
        h = item.header
        issued = recorded(h["issued_epoch_s"],now,"HOLD future published item")
        lo = item.line-1
        end = next((n for n in headings if n>lo),len(lines))
        body = lines[lo:end]
        items[item.number] = dict(header=h, body="\n".join(body), issued=issued)
        markers = [s.removeprefix("HP-DISPATCH ") for s in body if s.startswith("HP-DISPATCH ")]
        match = re.search(r"\b(hp-02-s0[123]) ISSUED\b",item.heading,re.I)
        if markers or match:
            need(match and len(markers)==1 and h["owner"]=="magistrate" and h["status"]=="ISSUED",
                 "HOLD malformed HP issue")
            d = read_json(markers[0])
            span = match[1].lower()
            plan = "cq-"+span+"-a1"
            issue_plans = [field for field in item.heading.split(", ") if field.startswith("cq-")]
            agree("HOLD published attempt contradicts heading",
                  [span,1,plan,[plan]], [d["span"],d["attempt"],d["plan_id"],issue_plans])
            key = (plan,d["attempt"])
            need(key not in attempts,"HOLD attempt already issued")
            attempts.add(key)
            read_at=recorded(d["read_at"],issued,"HOLD issue predates its Start evidence")
            for prior in issues.values():
                need(prior["check"] is not None and prior["check"]["at"]<=read_at,
                     "HOLD previous HP Check absent at issue Start")
            issues[item.number] = dict(item=item.number,dispatch=d,body=body,state="ISSUED",
                                      issued=issued,expiry=h["expires_epoch_s"],terminal=None,check=None)
        # Replay only published transitions, with both the event and its publishing
        # item visible. 'terminal' is the time the disposition became public.
        for ref in h["supersedes"]:
            if ref.isdecimal() and int(ref) in issues:
                entry=issues[int(ref)]
                recorded(entry["issued"],issued,"HOLD supersession chronology")
                entry.update(state="SUPERSEDED",terminal=issued)
        for change in h["sets"]:
            recorded(change["at_epoch_s"],issued,"HOLD transition after reading item")
            if change["item"] in issues:
                entry=issues[change["item"]]
                recorded(entry["issued"],change["at_epoch_s"],"HOLD transition before issue")
                entry["state"]=change["status"]
                if entry["state"] in ("CLOSED","VOID","EXPIRED"):
                    entry["terminal"]=issued
        check=re.fullmatch(r"(\d+)\. \*\*Magistrate HP CHECK #(\d+) for ([\w-]+)\.\*\*",item.heading)
        if check:
            entry=issues.get(int(check[2]))
            need(entry and check[2]==str(entry["item"]) and int(check[1])==item.number
                 and h["owner"]=="magistrate" and h["status"]=="CLOSED"
                 and check[3]==entry["dispatch"]["plan_id"],"HOLD wrong operational Check")
            terminal=entry["terminal"]
            if terminal is None and entry["state"]=="ISSUED":
                terminal=entry["expiry"]
            need(terminal is not None and entry["issued"]<=terminal<=issued
                 and entry["check"] is None,"HOLD operational Check chronology or duplicate")
            receipts=[s.removeprefix("HP-RECEIPT ") for s in body if s.startswith("HP-RECEIPT ")]
            need(len(receipts)<=1 and all(sha(v) for v in receipts),"HOLD conflicting published receipt")
            entry["check"]=dict(number=item.number,at=issued,receipts=receipts)
    states=rs.derive(parsed,math.floor(now))
    receipt_issues={}
    for n,entry in issues.items():
        entry["state"]=states[n]
        if entry["check"] is not None:
            need(states[n] in ("CLOSED","VOID","EXPIRED","SUPERSEDED"),"HOLD issue still open")
            for receipt in entry["check"]["receipts"]:
                agree("HOLD published receipt reused",n,receipt_issues.setdefault(receipt,n))
            entry["state"]="CHECKED"  # Operational interpretation of this exact Check as of now.
    top = max(n for _,n,_ in rs.heading_lines(raw))
    return head, list(issues.values()), top, items

def intervening(items, issue, start_top):
    need(type(start_top) is int and 0<start_top<issue, "HOLD published item order")
    return {str(n):item for n,item in items.items() if n>start_top and n!=issue}

def review_sheet():
    head,published,_,items = current_items(time.time(),fetch=True)
    opened = [r for r in published if r["state"]!="CHECKED"]
    need(len(opened)==1 and str(opened[0]["item"])==E["ITEM"],"HOLD no unique published issue")
    issue = opened[0]
    rows = {}
    for key,item in intervening(items,issue["item"],issue["dispatch"]["last_item"]).items():
        print(item["body"],file=sys.stderr)
        rows[key] = dict(item_sha256=digest(item["body"].encode()),disposition=None,grounds=None)
    return dict(head=head,issue=issue["item"],items=rows)

def review_decisions(items, head, issue, start_top):
    # Interpret each complete source item in the ordinary magistrate's Run turn.
    later = intervening(items,issue,start_top)
    if not later:
        return
    review = read_json((path("ACT_DIR")/"run-decisions.json").read_bytes())
    agree("HOLD review for different head or issue",[head,issue],[review["head"],review["issue"]])
    agree("HOLD incomplete Run decision review",sorted(later),sorted(review["items"]))
    for key,item in later.items():
        row = review["items"][key]
        need(row["item_sha256"]==digest(item["body"].encode())
             and row["disposition"]=="unaffected" and named(row["grounds"])
             and row["grounds"] in item["body"], "HOLD intervening decision #"+key)


def administrative_facts(book):
    # A desk can attest unchanged operational facts against a later unrelated main.
    facts = {k:v for k,v in book.items() if k not in ("main","recorded_at")}
    return digest(json.dumps(facts,sort_keys=True,separators=(",",":"),allow_nan=False).encode())

class Evidence:
    """Owner-authenticated public inventory and its immutable operational extracts."""
    def __init__(self, head, now, top):
        self.root = path("PUBLIC")
        raw = (self.root/"basis.json").read_bytes()
        self.hash = digest(raw)
        self.book = read_json(raw)
        b = self.book
        need(b["scope"]=="hp-02" and b["complete"] is True and b["main"]==head
             and b["host"]==E["HOST_ID"] and b["activation"]==E["ACTIVATION"]
             and stamp(b["from"])<=now<=stamp(b["through"]), "HOLD evidence basis")
        self.revision = administrative_facts(b)
        self.as_of = recorded(b["recorded_at"], now, "HOLD future evidence basis")
        self.cache = {}
        self.receipt_owner = {}
        self.attempt_receipt = {}
        self.receipt_roster = {}
        self.versions = {}
        self.series_for = {}
        for key, ref in b["records"].items():
            r = self.original(key)
            series = ref["series"]
            need(type(series) is list and series and all(named(s) for s in series),
                 "HOLD unidentified evidence series")
            series = tuple(series)
            order = ref["order"]
            need(type(order) is dict and len(order)==1, "HOLD ambiguous evidence order")
            origin, n = next(iter(order.items()))
            need((origin=="RUN_STATE" or (origin.startswith("ledger/") and named(origin[7:])))
                 and type(n) is int and n>0, "HOLD invalid evidence order")
            if origin=="RUN_STATE":
                need(n<=top, "HOLD evidence beyond published RUN_STATE")
            source, entries = self.versions.setdefault(series,(origin,{}))
            need(source==origin and n not in entries, "HOLD incomparable or duplicate evidence order")
            entries[n] = key
            self.series_for[key] = series
            # Classify effective operational records even when a selector omits them.
            if "fault" in r and "check_id" in r:
                expected = ("recovery",r["host"],r["check_id"],r["fault"])
            elif "check_id" in r and "host" in r:
                expected = ("host-check",r["host"])
            elif r.get("kind")=="scope-disposition":
                expected = ("disposition",r["scope"],r["subject"],r["cause"])
            elif "queue_sha" in r and "owner" in r and "effective" in r:
                expected = ("queue",r["queue_sha"])
            else:
                continue
            need(series==expected, "HOLD incorrectly scoped operational evidence")
        self.check_dispositions()

    def history(self, series):
        _, entries = self.versions[series]
        return [self.cache[entries[n]] for n in sorted(entries)]

    def row(self, key, reader_at=None):
        row = self.original(key,reader_at)
        series = self.series_for[key]
        need(self.history(series)[-1]["id"]==key, "HOLD newer evidence for "+key)
        # A selected HP authority can itself carry a withdrawal. Rank rows for
        # other kits keep their own disposition semantics.
        if row.get("kit")==K or row.get("queue_sha")==Q or series[0]=="timing":
            need(row.get("state") not in ("revoked","held","refused","failed-recovery","unproven-recovery"),
                 "HOLD withdrawn authority for "+key)
        return row

    def check_dispositions(self):
        scope = {"host":E["HOST_ID"], "queue":Q, "kit":K}
        for series in self.versions:
            if series[0]!="disposition":
                continue
            _, unit, subject, cause = series
            need(unit in scope and named(cause), "HOLD disposition scope")
            if scope[unit]!=subject:
                continue
            rows = self.history(series)
            for i, r in enumerate(rows):
                need(r["kind"]=="scope-disposition" and r["owner"] in ("lead","magistrate"),
                     "HOLD unauthorised disposition")
                if r["state"]=="cleared":
                    need(i and r["owner"]=="lead" and r["resolves"]==rows[i-1]["id"]
                         and named(r["disposition"]), "HOLD unlinked disposition")
                else:
                    need(r["state"] in ("revoked","refused","held"), "HOLD unknown disposition")
            need(rows[-1]["state"]=="cleared", "HOLD current "+unit+" disposition: "+rows[-1]["state"])

    def bind_receipt(self, row):
        receipt=row["receipt_sha"]
        plan=row["plan_id"]
        attempt=row["attempt"]
        need(sha(receipt) and named(plan) and type(attempt) is int and attempt>0,
             "HOLD host Check or receipt identity")
        key=(plan,attempt)
        identity=[plan,attempt]
        agree("HOLD receipt reused across attempts",identity,self.receipt_owner.setdefault(receipt,identity))
        agree("HOLD contradictory attempt receipts",receipt,self.attempt_receipt.setdefault(key,receipt))
        if "legs" in row:
            legs=ids(row["legs"])
            need(legs,"HOLD empty receipt roster")
            agree("HOLD conflicting receipt roster",legs,self.receipt_roster.setdefault(receipt,legs))

    def original(self, key, reader_at=None):
        if key not in self.cache:
            ref = self.book["records"][key]
            h = ref["sha256"]
            need(sha(h) and named(ref["source"]) and named(ref["entry"]), "HOLD source identity")
            data = (self.root/"records"/h).read_bytes()
            need(digest(data)==h, "HOLD source digest")
            row = read_json(data)
            agree("HOLD source/entry mismatch",[key,ref["source"],ref["entry"]],
                  [row["id"],row["source"],row["entry"]])
            recorded(row["recorded_at"],self.as_of,"HOLD future source record")
            # These fields describe accomplished facts. Schedule windows, deadlines,
            # prospective dates and readiness floors are deliberately separate.
            for field in ("ended","at","effective","t0"):
                if field in row:
                    epoch = stamp(row[field]) if field=="t0" else row[field]
                    recorded(epoch,row["recorded_at"],"HOLD future event in host Check or evidence")
            if "receipt_sha" in row:
                self.bind_receipt(row)
            self.cache[key] = row
        row=self.cache[key]
        if reader_at is not None:
            recorded(row["recorded_at"],reader_at,"HOLD source postdates reading item")
        return row

def public_hp_receipts(now):
    # Public operational projection supplied by the MBP custodian at a fixed root.
    census=read_json((path("MBP_PUBLIC")/"hp-receipts.json").read_bytes())
    agree("HOLD HP receipt census scope",["custody-mbp",E["HOST_ID"],K,True],
          [census[k] for k in ("custody","host","kit","complete")])
    recorded(census["recorded_at"],now,"HOLD future receipt census")
    need(type(census["ledger_seq"]) is int and census["ledger_seq"]>0,"HOLD MBP receipt ledger sequence")
    receipts=census["receipts"]
    need(type(receipts) is dict,"HOLD HP receipt inventory")
    plans=set()
    hashes=set()
    for key,r in receipts.items():
        plan=r["plan_id"]
        attempt=r["attempt"]
        need(named(key) and type(attempt) is int and attempt>0 and sha(r["receipt_sha"])
             and plan==f"cq-{r['span']}-a{attempt}" and r["span"] in ("hp-02-s01","hp-02-s02","hp-02-s03"),
             "HOLD native HP receipt identity")
        agree("HOLD native HP receipt scope",[K,E["HOST_ID"],PIN,ROSTERS[int(r["span"][-1])-1]],
              [r[k] for k in ("kit","host","pin","legs")])
        need((plan,attempt) not in plans and r["receipt_sha"] not in hashes,"HOLD ambiguous native receipts")
        plans.add((plan,attempt))
        hashes.add(r["receipt_sha"])
        recorded(r["recorded_at"],census["recorded_at"],"HOLD future receipt in index")
        recorded(r["ended"],r["recorded_at"],"HOLD future native receipt close")
    return census

def event_digest(events):
    data = json.dumps(events,sort_keys=True,separators=(",",":"),allow_nan=False)
    return digest(data.encode())

def look(now, previous=None):
    # Direct synchronous owner view, reopened on every call, never the Start copy.
    d = read_json((path("PUBLIC")/"look.json").read_bytes())
    need(d["id"]=="lm-hp-01" and d["kit"]==K and d["activation"]==E["ACTIVATION"]
         and d["complete"] is True and d["routes"]==["register","custody-air","custody-mbp"]
         and set(d["histories"])==set(d["routes"]), "HOLD look coverage")
    ledger_at=recorded(d["recorded_at"],now,"HOLD future look ledger")
    snapshot=None
    dates={"ledger":ledger_at}
    for route in d["routes"]:
        view = d["histories"][route]
        cutoff=recorded(view["recorded_at"],ledger_at,"HOLD look projection date")
        dates[route+"/history"]=cutoff
        agree("HOLD look route",route,view["source"])
        if route!="register":
            # Desk-configured owner roots. Never resolve these paths from the ledger.
            root=path("MBP_PUBLIC" if route=="custody-mbp" else "AIR_PUBLIC")
            file=root/"look.json"
            need(file.is_file() and not file.is_symlink()
                 and not os.path.samefile(path("MBP_PUBLIC")/"look.json",path("AIR_PUBLIC")/"look.json")
                 and not os.path.samefile(file,path("PUBLIC")/"look.json"),"HOLD look custody origin")
            owner=read_json(file.read_bytes())
            owner_at=recorded(owner["recorded_at"],ledger_at,"HOLD look custody attestation date")
            dates[route+"/owner"]=owner_at
            recorded(cutoff,owner_at,"HOLD look history postdates custody attestation")
            agree("HOLD look custody scope",[route,d["id"],K,E["ACTIVATION"],True],
                  [owner["route"],owner["id"],owner["kit"],owner["activation"],owner["complete"]])
            agree("HOLD look custody and ledger disagree",view,owner["history"])
        need(view["executed"] is False and view["reserved"] is False
             and view["conflicts"]==[] and named(view["source"])
             and type(view["events"]) is list, "HOLD look")
        active, used, disputed = set(), set(), set()
        last_at=-math.inf
        for n,event in enumerate(view["events"],1):
            at=recorded(event["at"],cutoff,"HOLD look execution or event chronology")
            need(last_at<=at,"HOLD look event chronology")
            last_at=at
            key = event["id"]
            need(type(event["seq"]) is int and event["seq"]==n and named(key), "HOLD look history")
            if event["kind"]=="reserved" and key not in used:
                active.add(key)
                used.add(key)
            elif event["kind"]=="released" and key in active and named(event["disposition"]):
                active.remove(key)
            elif event["kind"]=="reported_execution" and key not in used:
                used.add(key)
                disputed.add(key)
            elif (event["kind"]=="correction_of_false_report" and key in disputed
                  and event["owner"]=="lead" and event["mistaken_report"] is True
                  and named(event["disposition"]) and sha(event["proof_sha"])):
                disputed.remove(key)
            else:
                raise ValueError("HOLD look execution, unknown event or disputed disposition")
        need(type(view["last_seq"]) is int and view["last_seq"]==len(view["events"])
             and not active and not disputed, "HOLD look history")
        facts=[view[k] for k in ("events","last_seq","executed","reserved","conflicts")]
        if snapshot is None:
            snapshot=facts
        else:
            agree("HOLD look histories disagree",snapshot,facts)
    events, seq = snapshot[:2]
    if previous is not None:
        n = previous["seq"]
        need(type(n) is int and 0<=n<=seq and sha(previous["prefix_sha256"])
             and event_digest(events[:n])==previous["prefix_sha256"], "HOLD look history rollback")
        agree("HOLD look sources changed",sorted(dates),sorted(previous["dates"]))
        for source, at in dates.items():
            recorded(previous["dates"][source],at,"HOLD look source revision regressed")
        need(all(e["kind"]!="reserved" for e in events[n:]),"HOLD reservation during HP issue turn")
    return dict(seq=seq,prefix_sha256=event_digest(events),dates=dates)

def host():
    need("JOULEWISE_HOST_STATE_DIR" not in E,"HOLD MBP identity")
    agree("HOLD MBP identity",E["HOST_ID"],cmd("/usr/sbin/scutil","--get","LocalHostName").decode().strip())
    # The existing RC-checked F2 host verification (without its planner or launcher).
    subprocess.run([path("F2_HOST_CHECK")],cwd=path("REPO"),stdout=sys.stderr,check=True)
    for mode in ("0","2"):
        cmd("sudo","-n","-l","/usr/bin/pmset","-c","powermode",mode)
    from joulewise.align.apple import powermode
    powermode.host_lock_preflight(role="hp-02 preflight")
    absent(Path("/Users/Shared/JouleWise/host-power/high-power.marker"))
    absent(path("CUSTODY")/"desk_fence.json")
    m = powermode.observe_ac_powermode()
    agree("HOLD AC Automatic",0,m)

def kit_binding():
    repo, kit = path("REPO"),path("KIT")
    need(cmd("git","rev-parse","HEAD").decode().strip()==PIN,"HOLD runner pin")
    rc = subprocess.run(["git","symbolic-ref","-q","HEAD"],cwd=repo,stdout=subprocess.DEVNULL).returncode
    need(rc==1 and not cmd("git","status","--porcelain"), "HOLD detached clean checkout")
    for name,h,file in (("cl-hp-02.json",K,kit),("queue-b.json",Q,path("QUEUE_FILE"))):
        agree("HOLD committed or staged binding",h,
              digest(cmd("git","-C",path("AUDIT"),"show",SRC+":"+H+"/"+name)),digest(file.read_bytes()))
    need(kit==path("KITS_ROOT")/"hp-02/cl-hp-02.json" and not kit.parent.is_symlink()
         and stat.S_ISREG(kit.lstat().st_mode), "HOLD staged path")
    frozen = read_json(kit.read_bytes())["frozen"]
    need(frozen["commit"]==PIN and len(frozen["paths"])==37, "HOLD frozen map")
    for name,h in frozen["paths"].items():
        file = repo/name
        need(stat.S_ISREG(file.lstat().st_mode) and digest(file.read_bytes())==h,"HOLD materialized "+name)
    cmd(sys.executable,"-B","scripts/cadence_queue.py","validate-queue",path("QUEUE_FILE"),"--kits-root",path("KITS_ROOT"))
    return read_json(path("QUEUE_FILE").read_bytes())

def clean(r, host_id):
    fields = ("receipt_ok","auto_desk_ok","restore_proven","fence_gone","measurement_mode_ok",
              "feeds_stopped","groups_absent","lock_free","marker_clear","network_time_ok")
    flags(r,fields,"HOLD latest host Check or predecessor")
    need(r["host"]==host_id and sha(r["receipt_sha"]) and named(r["check_id"])
         and number(r["ended"])
         and type(r["restore_mode"]) is int and r["restore_mode"]==0
         and r["failed_recovery"] is False and r["open_stops"]==[], "HOLD latest host Check or predecessor")

def faults_for(r):
    # The Check's individual readbacks take precedence over an empty stop list.
    restore_flags = ("restore_proven","measurement_mode_ok","lock_free","marker_clear","network_time_ok")
    flags = (*restore_flags,"feeds_stopped","groups_absent","failed_recovery")
    need(all(type(r[k]) is bool for k in flags) and type(r["restore_mode"]) is int
         and ("attempt" not in r or (type(r["attempt"]) is int and r["attempt"]>0))
         and named(r["check_id"]) and sha(r["receipt_sha"]), "HOLD ambiguous host history")
    faults = set(ids(r["open_stops"]))
    if r["restore_mode"]!=0 or not all(r[k] for k in restore_flags):
        faults.add("restore")
    if not (r["feeds_stopped"] and r["groups_absent"]):
        faults.add("group-stop")
    state = r.get("state","checked")
    if state in ("revoked","refused","held"):
        faults.add("host-refusal")
    if state=="unproven-recovery":
        faults.add("restore")
    if r["failed_recovery"] or state=="failed-recovery":
        faults.add("failed-recovery")
    return faults

def restore_proof(p):
    return (p.get("command")=="restore-owed" and integer(p.get("rc"),0)
            and integer(p.get("restore_mode"),0)
            and all(p.get(k) is True for k in ("job_and_fence_clear","restore_proven",
                    "independent_readback","marker_clear","lock_free","measurement_mode_ok","network_time_ok")))

def recovery_ok(p):
    if (p.get("cleared") is not True or p.get("failed_recovery",False) is not False
            or p.get("state","cleared")!="cleared" or ("rc" in p and not integer(p["rc"],0))):
        return False
    if p["fault"] in ("restore","failed-recovery") or p.get("command")=="restore-owed":
        return restore_proof(p)
    if p["fault"] in ("group-stop","REFUSAL"):
        return (all(p.get(k) is True for k in ("feeds_stopped","groups_absent","independent_readback"))
                and integer(p.get("restore_mode"),0))
    return all(p[k] is True for k in ("restore_proven","independent_readback",
               "groups_absent","feeds_stopped") if k in p)

def newest_observation(ev, series):
    # Sequence breaks ties between publications of the same observation time.
    # No success at the failure time can satisfy the strict clearance rule.
    return max(reversed(ev.history(series)), key=lambda p:p["at"])

def check_halts(ev, checks, items, now):
    host = ev.book["host"]
    originals = {r["check_id"]:r for r in checks}
    fields = ("host","plan_id","attempt","pin","check_id","receipt_sha")
    failures = {}
    for r in checks:
        faults = faults_for(r)
        if {"restore","failed-recovery"} & faults:
            failures[r["id"]] = (r,r["ended"])
    for series in ev.versions:
        if series[:2]!=("recovery",host):
            continue
        for p in ev.history(series):
            r = originals[p["check_id"]]
            agree("HOLD recovery for different attempt",[r[k] for k in fields],[p[k] for k in fields])
            recorded(r["ended"],p["at"],"HOLD recovery predates original close")
            if not recovery_ok(p):
                failures[p["id"]] = (p,p["at"])
    cleared = set()
    for n,item in items.items():
        for line in item["body"].splitlines():
            if not line.startswith("HP-HOST-CLEAR "):
                continue
            release = read_json(line.removeprefix("HP-HOST-CLEAR "))
            if release["host"]!=host:
                continue
            need(item["header"]["owner"]=="lead" and item["header"]["status"]=="CLOSED"
                 and named(release["failure"]) and named(release["proof"]), "HOLD invalid lead clearance")
            key = release["failure"]
            need(key in failures,"HOLD lead clearance names unknown failure")
            failed, observed = failures[key]
            proof = ev.original(release["proof"],item["issued"])
            recorded(failed["recorded_at"],item["issued"],"HOLD lead item predates failure report")
            for row in (failed,proof):
                order = ev.book["records"][row["id"]]["order"]
                if "RUN_STATE" in order:
                    need(order["RUN_STATE"]<n,"HOLD lead clearance order")
            agree("HOLD lead clearance identity",[failed[k] for k in fields],
                  [proof[k] for k in fields],[release[k] for k in fields])
            fault = failed.get("fault","restore")
            same_fault = (proof["fault"]==fault or
                          {proof["fault"],fault} <= {"restore","failed-recovery"})
            need(ev.series_for[proof["id"]][:3]==("recovery",host,failed["check_id"])
                 and same_fault
                 and proof["owner"] in ("magistrate","lead") and sha(proof["proof_sha"])
                 and recovery_ok(proof) and observed < proof["at"] <= item["issued"] <= now,
                 "HOLD missing post-failure recovery observation")
            cleared.add(key)
    need(cleared==set(failures),"HOLD latest host Check or predecessor: unresolved host fault (typed lead clearance required)")

def host_faults(ev, r, now):
    for fault in sorted(faults_for(r)):
        if fault=="failed-recovery":
            continue  # check_halts verifies the operational proof and the lead item together.
        ref = ev.book["host_resolutions"].get(r["check_id"]+"/"+fault)
        need(named(ref), "HOLD latest host Check or predecessor: unresolved host fault")
        p = ev.original(ref)
        need(newest_observation(ev,("recovery",r["host"],r["check_id"],fault))["id"]==ref,
             "HOLD newer evidence for "+ref)
        need(ev.series_for[ref]==("recovery",r["host"],r["check_id"],fault),
             "HOLD unlinked host recovery series")
        check_ref, proof_ref = (ev.book["records"][key]["order"] for key in (r["id"],ref))
        if check_ref.keys()==proof_ref.keys():
            need(next(iter(check_ref.values())) < next(iter(proof_ref.values())),
                 "HOLD recovery must follow original host Check")
        recorded(r["recorded_at"],p["recorded_at"],"HOLD unlinked host recovery date")
        need(named(r["plan_id"]) and type(r["attempt"]) is int and r["attempt"]>=1
             and re.fullmatch("[0-9a-f]{40}",r["pin"])
             and integer(p["attempt"],r["attempt"]) and p["fault"]==fault
             and p["cleared"] is True and p.get("failed_recovery",False) is False
             and p.get("state","cleared")=="cleared" and p["owner"] in ("lead","magistrate")
             and sha(p["proof_sha"]) and number(p["at"]) and r["ended"]<=p["at"]<=now,
             "HOLD unlinked host recovery")
        fields=("host","plan_id","check_id","receipt_sha","pin","attempt")
        agree("HOLD unlinked host recovery",[r[k] for k in fields],[p[k] for k in fields])
        if fault=="restore":
            need(restore_proof(p),
                 "HOLD unproven pinned recovery")
        if fault=="host-refusal":
            need(p["owner"]=="lead" and named(p["halt_disposition"]), "HOLD halted host")
        if fault in ("group-stop","REFUSAL"):
            subjects = ids(r["stop_subjects"])
            need(subjects and set(ids(p["stop_subjects"]))==set(subjects)
                 and p["feeds_stopped"] is True and p["groups_absent"] is True
                 and p["independent_readback"] is True and integer(p["restore_mode"],0),
                 "HOLD unproven group clearance")

def host_history(ev, items, now):
    b = ev.book
    checks = ev.history(("host-check",b["host"]))
    need({r["id"] for r in checks}==set(ids(b["host_checks"])), "HOLD incomplete latest host Check history")
    need(checks and all(r["host"]==b["host"] and number(r["ended"]) and r["ended"]<=now for r in checks)
         and len(set(r["check_id"] for r in checks))==len(checks)
         and checks[-1]["id"]==b["latest_host_check"] and b["unresolved_host_stops"]==[],
         "HOLD latest host Check")
    # Every earlier close participates, even if another kit has since closed cleanly.
    for r in checks:
        host_faults(ev,r,now)
    for series in ev.versions:
        if series[:2]==("recovery",b["host"]):
            _, _, check_id, fault = series
            last = newest_observation(ev,series)
            need(last["id"]==b["host_resolutions"].get(check_id+"/"+fault)
                 and last["cleared"] is True
                 and any(r["check_id"]==check_id for r in checks),
                 "HOLD unresolved host recovery")
    check_halts(ev,checks,items,now)
    return checks

def histories(ev, seq, now, published, items):
    b = ev.book
    hp01 = ids(b["hp01"])
    need(len(hp01)==3 and len({ev.row(k)["receipt_sha"] for k in hp01})==3,"HOLD hp-01 census")
    for j,key in enumerate(hp01):
        r = ev.row(key)
        agree("HOLD hp-01 census",[f"cq-hp-01-s0{j+1}-a1",1],[r["plan_id"],r["attempt"]])
        need(type(r["issue"]) is int and type(r["check"]) is int
             and (r["kit"],r["span"],r["issue"],r["check"],r["legs"])==
             (K1,f"hp-01-s0{j+1}",[335,339,342][j],[337,340,343][j],ROSTERS[j])
             and sha(r["receipt_sha"]) and day(stamp(r["t0"]))==date(2026,11,15),"HOLD contradictory hp-01 census")
    agree("HOLD line 2",LINE2,b["line2"])
    audit=path("AUDIT")
    def blob(ref):
        return cmd("git","-C",audit,"show",ref)
    # Fixed published records. Limit the RS338 inspection to its own item.
    rs=blob(RS338.split("#")[0]).decode()
    section=re.search(r"(?ms)^338\. \*\*.*?(?=^337\. \*\*)",rs)
    need(section and all(x in section[0] for x in (K1,"43673985768","43600776368","43601158271")),
         "HOLD RS338")
    delta=blob(SRC+":"+H+"/HP02-DELTA.md").decode()
    hp1=blob("bbd34dc876001786c3603d9c4583391639284253:docs/process/cadence/kits/cl-hp-01.json")
    need(K1 in delta and K in delta and "37" in delta and digest(hp1)==K1
         and read_json(hp1)["frozen"]==read_json(path("KIT").read_bytes())["frozen"],"HOLD frozen delta")
    rld=blob("04d8aa778fe6dc6ec544e86b4730a986020fd368:"+H.split("/evidence/")[0]+"/RESEARCH-LEAD-DECISIONS.md").decode()
    need('3. This sentence: "'+QUOTE+'"' in rld,"HOLD RL-190 literal")
    decisions=ev.history(("queue",Q))
    need({r["id"] for r in decisions}==set(ids(b["lead_queue_decisions"]))
         and decisions[-1]["id"]==b["current_queue_authority"], "HOLD latest queue authority")
    for r in decisions:
        need(r["owner"]=="lead" and r["queue_sha"]==Q and number(r["effective"])
             and r["effective"]<=now and r["state"] in ("admitted","revoked","held","refused"),
             "HOLD queue decision history")
    admission=decisions[-1]
    agree("HOLD current queue authority",["lead",Q,"admitted",SRC],
          [admission[k] for k in ("owner","queue_sha","state","commit")])
    expected = {leg:"spent" if i<seq else "unrun" for i,ls in enumerate(ROSTERS,1) for leg in ls}
    history = ev.row(b["hp_roster"])
    need(history["kit"]==K and history["all_attempts"] is True
         and history["unreconciled"]==[], "HOLD HP roster")
    checks = host_history(ev,items,now)
    # Derive spend from typed issue/Check pairs and independent public native
    # receipt projections. A refreshed output name never changes this identity.
    # Examine the entire owner inventory once, including receipts with no
    # corresponding issue, and dates on entries omitted from a desk summary.
    native_ids=set()
    for key, row in ev.cache.items():
        if row.get("kind")=="native-span-receipt":
            native_ids.add(key)
    census=ev.row(b["hp_receipt_inventory"])
    agree("HOLD native MBP receipt census",census,public_hp_receipts(now))
    agree("HOLD stale MBP receipt index",{"ledger/MBP-hp-receipts":census["ledger_seq"]},
          b["records"][census["id"]]["order"])
    need(set(census["receipts"])==native_ids,"HOLD incomplete HP receipt census")
    for key in native_ids:
        row=ev.row(key,census["recorded_at"])
        agree("HOLD native receipt contradicts MBP index",row,census["receipts"][key])
    issued={r["dispatch"]["plan_id"]:r for r in published}
    spent={leg:"unrun" for leg in expected}
    for r in checks:
        flags(r,("receipt_ok","auto_desk_ok","fence_gone"),"HOLD host Check")
        plan=r["plan_id"]
        attempt=r["attempt"]
        need(named(plan) and type(attempt) is int and attempt>0,"HOLD host Check attempt")
        sha256=r["receipt_sha"]
        hp=re.fullmatch(r"cq-hp-02-s(0[123])-a([1-9][0-9]*)",plan)
        if not hp and r.get("kit")!=K and r.get("span") not in ("hp-02-s01","hp-02-s02","hp-02-s03"):
            continue
        need(hp and plan in issued,
             "HOLD HP roster or unpublished HP attempt")
        entry=issued.pop(plan)
        ck=entry["check"]
        need(entry["state"]=="CHECKED" and ck is not None,"HOLD unchecked HP attempt")
        dispatch=entry["dispatch"]
        index=int(hp[1])
        legs=ROSTERS[index-1]
        agree("HOLD HP roster or predecessor identity",
              [index,int(hp[2]),"hp-02-s"+hp[1],K,PIN,b["host"],legs],
              [dispatch[k] for k in ("seq","attempt","span","kit_sha256","pin","host","legs")],
              [index,attempt,r["span"],r["kit"],r["pin"],r["host"],r["legs"]])
        agree("HOLD Check receipt or issue mapping",
              [entry["item"],ck["number"],[sha256]],[r["issue_item"],r["check_item"],ck["receipts"]])
        need(entry["issued"]<=r["ended"]<=ck["at"]<=history["recorded_at"]
             and r["recorded_at"]==ck["at"],"HOLD host Check chronology")
        native=ev.row(r["receipt_ref"],min(ck["at"],r["recorded_at"]))
        need(r["receipt_ref"] in native_ids and native["source"]!=r["source"]
             and native["kind"]=="native-span-receipt",
             "HOLD predecessor receipt origin")
        native_ids.remove(r["receipt_ref"])
        fields=("plan_id","attempt","host","kit","pin","span","legs","receipt_sha","span_result")
        agree("HOLD predecessor receipt and Check disagree",[r[k] for k in fields],[native[k] for k in fields])
        need(number(native["ended"]) and native["ended"]==r["ended"],"HOLD predecessor receipt close time")
        clean(r,b["host"])
        need(r["span_result"]=="MEASURED_OK" and r["mode2_included_verified"] is True,
             "HOLD predecessor")
        for leg in legs:
            agree("HOLD HP roster duplicate spend","unrun",spent[leg])
            spent[leg]="spent"
    need(not issued and not native_ids,"HOLD HP roster missing receipt-backed Check")
    agree("HOLD HP roster",expected,spent,history["state_by_leg"])
    latest = checks[-1]
    need(all(latest[k] is True for k in ("receipt_ok","auto_desk_ok","fence_gone")),
         "HOLD latest host Check")
    priors = [ev.original(k) for k in ids(b["hp_predecessors"])]
    need(len(priors)==seq-1,"HOLD predecessor enumeration")
    for j,r in enumerate(priors,1):
        clean(r,b["host"])
        need(any(c is r for c in checks) and r["kit"]==K and r["pin"]==PIN and r["span"]==f"hp-02-s0{j}"
             and r["plan_id"]=="cq-"+r["span"]+"-a1" and integer(r["attempt"],1)
             and r["legs"]==ROSTERS[j-1] and r["runner_kind"]=="cadence-legs-v1"
             and r["mode2_included_verified"] is True and r["span_result"]=="MEASURED_OK"
             and r["ended"]<=latest["ended"] and (j==1 or priors[j-2]["ended"]<r["ended"]), "HOLD predecessor")
    return admission

def day(t):
    return datetime.fromtimestamp(t,LA).date()

def bounds(interval):
    lo,hi = interval
    need(number(lo) and number(hi) and lo<=hi,"HOLD unordered window")
    return lo,hi

def os_hit(t,w):
    from joulewise.cadence import legs
    return next((end for start,end in legs.window_epochs(t,[legs.parse_window(WINDOWS[0])])
                 if t<end and t+w>start),None)

def rank(ev, lo, hi, worst, pending):
    b = ev.book
    day0 = day(lo)
    base = [f"f2-stab-{i:02}" for i in range(1,15)]
    inst = ids(b["admitted_instruments"])
    need(set(inst)>={f"f2-inst-{i:02}" for i in range(1,4)}
         and all(re.fullmatch(r"f2-inst-\d+",k) for k in inst),"HOLD instrument register")
    sub = ["f2-stab-15","f2-stab-16"]
    names = ["READY",*base,*inst,*sub]
    if "counted" in b["positions"]:
        names.append("counted")  # Optional desk summary, never the programme authority.
    need(set(b["positions"])==set(names) and len(set(b["positions"].values()))==len(names),
         "HOLD rank inventory")
    credit = b["daily_completion"]
    if credit is not None:
        c = ev.row(credit)
        need(c["kit"] in base and c["pin"]==BASE and day(stamp(c["t0"]))==day0
             and number(c["ended"]) and stamp(c["t0"])<=c["ended"]<=lo and c["leg"] in {f"L{i:03}" for i in range(1,13)}
             and c["leg"] in ids(c["completed_roster"]) and sha(c["receipt_sha"])
             and c["checked"] is True, "HOLD base-kit completion")
    rows = {}
    times = {lo, hi}
    midnight = datetime.combine(day0,wall.min,LA).timestamp()
    # At November queue-b dates LA has 86400-second days. Include both OS edges,
    # end-touch for the pair/single/HP, and each pin-A eligibility transition.
    for delta in (0,86400):
        for s in (0,7200,9300,39000,47700,7200-5850,7200-8550,7200-worst):
            if lo <= midnight+delta+s <= hi:
                times.add(midnight+delta+s)
    evidence_entries = set()
    original_entries = set()
    for k in names:
        r = ev.row(b["positions"][k])
        identity = (r["source"],r["entry"])
        need(identity not in evidence_entries and r["kit"]==k and named(r["position"])
             and r["entry"]==r["position"] and "starts" not in r and r["date"]==str(day0)
             and stamp(r["valid_from"])<=lo<=hi<=stamp(r["valid_through"]),
             "HOLD rank position or stale evidence")
        evidence_entries.add(identity)
        if k in inst+base+sub:
            need(r["pin"]==(PIN_B if k in sub else BASE) and sha(r["kit_sha"])
                 and sha(r["queue_sha"]),
                 "HOLD rank pin or queue position")
            original=ev.row(r["position_ref"],r["recorded_at"])
            locator=(original["source"],original["entry"])
            need(locator not in original_entries and original["kind"] in ("queue-entry","terminal-check")
                 and (r["state"]!="exhausted" or original["kind"]=="terminal-check")
                 and (r["state"]!="available" or original["kind"]=="queue-entry")
                 and original["source"]!=r["source"], "HOLD rank source position")
            fields=("kit","kit_sha","pin","queue_sha","position")
            agree("HOLD rank source position",[r[f] for f in fields],[original[f] for f in fields])
            original_entries.add(locator)
        need(r["state"] in ("available","exhausted","held","unavailable")
             and named(r["disposition"]), "HOLD rank state")
        if r["state"]=="available":
            need(r["windows"] and type(r["windows"]) is list, "HOLD rank windows")
            if k in inst:
                need(r["sizes"] in ([1],[2,1]) and all(type(n) is int for n in r["sizes"]),
                     "HOLD pair/single candidates")
            for interval in r["windows"]:
                left,right = bounds(interval)
                times.update(t for t in (left,right) if lo<=t<=hi)
        else:
            need(r["windows"]==[],"HOLD conflicting rank evidence")
        rows[k]=r
    for position in pending:
        for left,right in position["allowed_starts"]:
            if max(left,math.ceil(lo))<=min(right,math.floor(hi)):
                raise ValueError("CEDE READY/counted "+position["position"])
    if pending and "counted" in rows:
        need(rows["counted"]["state"]!="exhausted", "HOLD counted summary contradicts dated programme")
    points=sorted(times)
    for t in sorted(set(points+[(x+y)/2 for x,y in zip(points,points[1:])])):
        def ready(k):
            return any(l<=t<=h for l,h in rows[k]["windows"])
        def pin_a():
            # RS463's inclusive 10:50:00 boundary, then resumes at 13:15:00.
            return not (39000<t-midnight<47700)
        if ready("READY"):
            raise ValueError("CEDE READY/counted")
        if "counted" in rows and ready("counted"):
            raise ValueError("HOLD counted summary without a feasible dated position")
        if credit is None and pin_a() and any(ready(k) for k in base):
            raise ValueError("CEDE daily base")
        diverted = False
        for k in inst:
            if pin_a() and ready(k):
                for size in rows[k]["sizes"]:
                    if os_hit(t,{1:5850,2:8550}[size]) is None:
                        raise ValueError("CEDE "+k)
                    diverted = True
        hit = os_hit(t,worst)
        if hit or diverted:
            if any(ready(k) for k in sub):
                raise ValueError("CEDE eligible 15/16")
            raise ValueError("WAIT until 02:35 local; re-rank")


def calendar(ev):
    # The order/membership comes from the lead's whole dated programme.
    # The desk's outstanding table is a second source with exact set equality.
    program = ev.row(ev.book["counted_program"])
    desk = ev.row(ev.book["counted_outstanding"])
    need(program["complete"] is True and desk["complete"] is True and
         program["source"]!=desk["source"], "HOLD counted authorities")
    pending = []
    all_spans = ids(program["ordered_spans"])
    need(set(program["dispositions"])==set(all_spans), "HOLD counted inventory")
    for key in all_spans:
        r = ev.row(program["dispositions"][key],program["recorded_at"])
        need(r["position"]==key and named(r["pin"]) and named(r["queue_entry"]),
             "HOLD counted span identity")
        if r["state"]=="checked":
            need(sha(r["receipt_sha"]) and r["check_ok"] is True, "HOLD counted Check")
        elif r["state"]=="pending":
            need(key in desk["pins"], "HOLD omitted counted start")
            recorded(r["recorded_at"],desk["recorded_at"],"HOLD counted position postdates reading item")
            agree("HOLD counted plan",r["pin"],desk["pins"][key])
            need(named(r["plan_ref"])
                 and number(r["ready_at"]) and type(r["allowed_starts"]) is list,
                 "HOLD counted plan")
            midnight=datetime.combine(date.fromisoformat(r["day"]),wall.min,LA)
            first=max(int(midnight.timestamp()), math.ceil(r["ready_at"]))
            last=int((midnight+timedelta(days=1)).timestamp())-1
            usable=[]
            for left,right in r["allowed_starts"]:
                need(type(left) is int and type(right) is int and left<=right,"HOLD counted window")
                if max(left,first)<=min(right,last):
                    usable.append((max(left,first),min(right,last)))
            # Only an effective disposition linked to this dated position can
            # remove a legal start. Clip both rank and occupancy identically.
            for ref in ids(r.get("hold_refs",[])):
                hold=ev.row(ref,r["recorded_at"])
                need(hold["kind"]=="counted-hold" and hold["owner"] in ("lead","magistrate")
                     and all(hold[k]==r[k] for k in ("day","position","pin","queue_entry","plan_ref"))
                     and named(hold["disposition"]) and hold["in_force"] is True,
                     "HOLD unlinked counted disposition")
                left,right=bounds(hold["blocked_starts"])
                need(type(left) is int and type(right) is int,"HOLD counted hold interval")
                usable=[(a,b) for x,y in usable
                        for a,b in ((x,min(y,left-1)),(max(x,right+1),y)) if a<=b]
            pending.append(dict(r,allowed_starts=usable))
        else:
            raise ValueError("HOLD unknown counted disposition")
    keys=[r["position"] for r in pending]
    agree("HOLD omitted counted start",keys,ids(desk["ordered_pending"]))
    need(set(desk["pins"])==set(keys),"HOLD omitted counted start")
    return pending

def occupancy(seq,p,arg,a,b,u,pending):
    from joulewise.cadence import legs as timing
    from scripts import align_r1_rehearsal as r1, launch_cadence_span as launcher
    W=(16650,19350,22050)[seq-1]
    F=W+1460
    flags(p,("blackout_clear",),"HOLD pin plan")
    agree("HOLD pin plan",[arg],p["batch_windows"])
    need(number(p["worst_case_s"]) and p["worst_case_s"]==W
         and [x["leg_id"] for x in p["legs"]]==ROSTERS[seq-1] and p["campaign_id"]=="cl-hp-02"
         and integer(p["redo_quota"],2) and number(p["leg_cap_s"]) and p["leg_cap_s"]==2700
         and number(p["soak_s"]) and p["soak_s"]==1950
         and launcher.cadence_minimum_seconds(p)==W+560,"HOLD pin plan")
    fields=("runner","guard","selector","dispatch","inner","pre_leg","leg_overshoot","tail","close","outer","transfer_outside")
    need(all(number(u[k]) and u[k]>=0 for k in fields),"WAIT timing evidence")
    w=timing.parse_window(arg)
    n=len(ROSTERS[seq-1])+2
    D=a+F
    need(not timing.blackout_bound_s(a,b-a+u["runner"]+W,[w]),"WAIT replan")
    need(b+u["runner"]+W+560<=D,"CEDE launch minimum")
    need(300+u["runner"]<=u["guard"]<=u["selector"],"WAIT dwell/selector proof")
    need(b+u["guard"]+1950+n*2700<=D-370,"CEDE pre-soak guard")
    need(u["dispatch"]+u["inner"]<=150,"WAIT child OS-window proof")
    end=b+u["selector"]
    end+=timing.interval_delay(end,1950,[w,r1.OS_BATCH_WINDOW_LOCAL])+u["dispatch"]+1950
    for _ in range(n):
        end+=u["pre_leg"]
        end+=timing.leg_start_delay(end,[w])+u["leg_overshoot"]+2700
    work=end+u["tail"]
    close=work+u["close"]
    clear=close+u["outer"]
    need(work<=D-370 and close<=D-190 and clear<=D,"CEDE full fence")
    limit=math.inf
    for r in reversed(pending):
        midnight=datetime.combine(date.fromisoformat(r["day"]),wall.min,LA)
        lo=int(midnight.timestamp())
        hi=int((midnight+timedelta(days=1)).timestamp())-1
        step=r["through_transition_s"]
        need(number(step) and step>=0 and number(r["ready_at"]), "WAIT transition")
        if limit!=math.inf:
            hi=min(hi,math.floor(limit-step))
        choices=[]
        for left,right in r["allowed_starts"]:
            need(type(left) is int and type(right) is int and left<=right,"WAIT counted window")
            if max(lo,left,math.ceil(r["ready_at"]))<=min(hi,right):
                choices.append(min(hi,right))
        need(choices,"CEDE counted date")
        limit=max(choices)
    need(math.ceil(b+F+u["transfer_outside"])<=limit,"CEDE dated start")
    return dict(work_end=work,close_end=close,clear_end=clear,latest_fence=b+F,
                latest_counted=None if limit==math.inf else limit)

def timing_grant(grants,arg):
    need(arg in WINDOWS,"WAIT timing argument")
    if type(grants) is dict:
        need(set(grants)<=set(WINDOWS) and all(type(v) is bool for v in grants.values())
             and arg in grants,"WAIT timing argument")
        agree("WAIT timing argument",True,grants[arg])
    else:
        need(type(grants) is list and all(type(v) is str and v in WINDOWS for v in grants)
             and len(set(grants))==len(grants) and arg in grants,"WAIT timing argument")

def queue_time(now,call,last,admission,opening,expiry):
    need(all(number(x) for x in (opening,now,call,last,expiry)) and opening<=now<=call<=last
         and type(admission["other_expiries"]) is list
         and all(call<=e-600 and last<e for e in [expiry,*map(stamp,admission["other_expiries"])]),
         "WAIT or renew queue")

def start():
    from joulewise.cadence.legs import PlanError
    from scripts import launch_cadence_span as launcher
    snapshot_at=time.time()
    head,published,top,items=current_items(snapshot_at)
    need(all(row["state"]=="CHECKED" for row in published),"HOLD unchecked HP item")
    absent(path("CUSTODY")/"hp-issue.marker")
    q=kit_binding()
    host()
    now=time.time()
    ev=Evidence(head,now,top)
    need(all(item["issued"]<=ev.as_of for item in items.values()),"HOLD Start review predates published decision")
    observed_look=look(now)
    seq=int(E["SEQ"])
    need(seq in (1,2,3),"HOLD sequence")
    legs=ROSTERS[seq-1]
    span=f"hp-02-s0{seq}"
    plan_id=f"cq-{span}-a1"
    need(q["queue_id"]=="cq-hp-02-b" and q["halt"] is None and len(q["spans"])==3
         and q["expires_at"]=="2026-11-30T00:00:00-08:00","HOLD queue")
    for i,r in enumerate(q["spans"],1):
        need(integer(r["seq"],i) and integer(r["attempt"],1)
             and (r["seq"],r["span_id"],r["block_id"],r["legs"],r["attempt"],r["rerun_of"],r["kit"],r["not_before"])==
             (i,f"hp-02-s0{i}","hp-02",ROSTERS[i-1],1,None,{"path":"hp-02/cl-hp-02.json","sha256":K},"2026-11-21"),"HOLD queue entry")
    admission=histories(ev,seq,now,published,items)
    pending=calendar(ev)
    tr=ev.row(ev.book["timing"])
    need((tr["pin"],tr["host"],tr["span"])==(PIN,E["HOST_ID"],span) and tr["joint_bound"] is True,
         "WAIT timing scope")
    a,b=bounds(tr["plan_range"])
    u=tr["bounds"]
    arg=WINDOWS[0]
    try:
        p=launcher.cadence_plan(path("KIT"),",".join(legs),arg,t0=a)
    except PlanError as e:
        need(len(e.problems)==1 and "meets a batch blackout" in e.problems[0],"HOLD plan error")
        arg=WINDOWS[1]
        need(time.time()<=a, "WAIT fresh alternate plan anchor")
        p=launcher.cadence_plan(path("KIT"),",".join(legs),arg,t0=a)
    timing_grant(tr["arguments"],arg)
    call=tr["call_by"]
    need(all(number(v) and v>=0 for v in (call,u["runner"],u["call_tail"],u["runner_tail"])),
         "WAIT timing evidence")
    last=b+u["runner"]
    need(now<=a<=b<=call<=last and 0<=u["call_tail"]<=u["runner_tail"]<=u["runner"]
         and last<=stamp(ev.book["through"]),"WAIT handoff bounds")
    opening=stamp("2026-11-21T00:00:00-08:00")
    expiry=stamp(q["expires_at"])
    queue_time(now,call,last,admission,opening,expiry)
    need(day(now)==day(last) and day(now)!=date(2026,11,15),"WAIT t0-date or re-rank")
    need(number(p["worst_case_s"]),"HOLD planned work duration")
    rank(ev,now,last,p["worst_case_s"],pending)
    fit=occupancy(seq,p,arg,a,b,u,pending)
    cmd(sys.executable,"-B","scripts/cadence_queue.py","validate-kit",path("KIT"),"--repo",path("REPO"),"--batch-window",arg)
    out=path("OUT")
    need(out.is_absolute() and out.parent==path("CAMPAIGN_ROOT")/"cl-hp-02"
         and re.fullmatch(plan_id+r"-\d{8}T\d{6}Z",out.name), "HOLD output identity")
    datetime.strptime(out.name[-16:],"%Y%m%dT%H%M%SZ")
    absent(out)
    return dict(read_at=now,basis_at=ev.as_of,admin_sha256=ev.revision,look=observed_look,main=head,last_item=top,activation=E["ACTIVATION"],host=E["HOST_ID"],seq=seq,span=span,attempt=1,
                plan_id=plan_id,campaign="cl-hp-02",pin=PIN,kit_sha256=K,queue_sha256=Q,
                expires_at=q["expires_at"],other_expiries=admission["other_expiries"],
                kit=str(path("KIT")),legs=legs,arg=arg,out=str(out),basis=ev.hash,
                admission=admission["source"]+"#"+admission["entry"],line2=LINE2,
                timing_arguments=tr["arguments"],plan_range=[a,b],call_by=call,call_tail=u["call_tail"],runner=u["runner"],
                runner_tail=u["runner_tail"],worst=p["worst_case_s"],occupancy=fit)

def run():
    run_head,published,top,items=current_items(time.time(),fetch=True)
    opened=[r for r in published if r["state"]!="CHECKED"]
    need(len(opened)==1,"HOLD no unique published issue")
    issue=opened[0]
    n,d,body,state,expiry,issued=(issue[k] for k in ("item","dispatch","body","state","expiry","issued"))
    start_result = read_json(path("START_RESULT").read_bytes())
    agree("HOLD published issue and start-check disagree",d,start_result)
    need(str(n)==E["ITEM"]
         and all(s in "\n".join(body) for s in (RS338.split(":")[0],K1,SRC,QUOTE)),
         "HOLD published issue and start-check disagree")
    seq=int(E["SEQ"])
    need(seq in (1,2,3) and integer(d["seq"],seq) and d["activation"]==E["ACTIVATION"]
         and d["host"]==E["HOST_ID"] and d["span"]==f"hp-02-s0{seq}"
         and integer(d["attempt"],1) and d["plan_id"]==f"cq-hp-02-s0{seq}-a1"
         and d["campaign"]=="cl-hp-02" and d["pin"]==PIN and d["queue_sha256"]==Q
         and d["kit_sha256"]==K and d["line2"]==LINE2 and d["legs"]==ROSTERS[seq-1]
         and E["LEGS"].split(",")==d["legs"] and E["ARG"]==d["arg"] and E["OUT"]==d["out"]
         and E["KIT"]==d["kit"],"HOLD published dispatch identity")
    timing_grant(d["timing_arguments"],d["arg"])
    roster_clause=(f"- Issue one attempt for block hp-02, queue cq-hp-02-b seq {seq}, "
                   f"{d['span']}, ordered {','.join(d['legs'])}, attempt 1.")
    runner_clause=f"- Runner {PIN}, cadence-legs-v1, cl-hp-02 SHA-256 {K}."
    need([s for s in body if s.startswith("- Issue one attempt ")]==[roster_clause]
         and [s for s in body if s.startswith("- Runner ")]==[runner_clause],
         "HOLD published roster or digest")
    q=kit_binding()
    need(d["expires_at"]==q["expires_at"] and type(expiry) is int and expiry==stamp(q["expires_at"])
         and body.count("Queue-b expires_at="+q["expires_at"])==1, "HOLD published queue expiry")
    absent(path("OUT"))
    kit=path("KIT")
    need(digest(kit.read_bytes())==d["kit_sha256"],"HOLD published kit")
    t=time.time()
    a,b=bounds(d["plan_range"])
    need(state=="ISSUED" and issued<=t<expiry and a<=t<=b, "WAIT expired issue or actual-t0 range")
    args=["--kit",str(kit),"--legs",",".join(d["legs"]),"--batch-window",d["arg"]]
    p=read_json(cmd(sys.executable,"-B","scripts/cadence_legs_runner.py","plan",*args,"--t0",str(t)))
    w=d["worst"]
    need(number(w) and w==(16650,19350,22050)[seq-1] and number(p["worst_case_s"])
         and number(p["launch_deadline_epoch_s"]) and number(p["t0_epoch_s"])
         and all(number(d[k]) and d[k]>=0 for k in ("call_by","runner","runner_tail","call_tail"))
         and d["call_tail"]<=d["runner_tail"]<=d["runner"], "HOLD Run numeric evidence")
    deadline=p["launch_deadline_epoch_s"]+900
    need(p["kit_sha256"]==d["kit_sha256"] and p["campaign_id"]==d["campaign"]
         and [r["leg_id"] for r in p["legs"]]==d["legs"] and p["batch_windows"]==[d["arg"]]
         and p["t0_epoch_s"]==t and p["blackout_clear"] is True and p["worst_case_s"]==w
         and os_hit(t,w) is None and abs(deadline-t-w-1460)<1e-5,"HOLD actual-t0 plan")
    command=[sys.executable,"-B","scripts/launch_cadence_span.py","launch","--repo",E["REPO"],
             "--python-bin",sys.executable,*args,"--output",d["out"],"--disk-path",E["REPO"],
             "--custody-root",E["CUSTODY"],"--magistrate-pid",E["MAGISTRATE_PID"],
             "--deadline",str(deadline),"--exit-wait-seconds","180","--start-wait-seconds","30"]
    # Check the revision of the scoped administrative inventory once more. A
    # changed input ends this single dispatch and gets a fresh ordinary Start.
    live=read_json((path("PUBLIC")/"basis.json").read_bytes())
    recorded(d["basis_at"],live["recorded_at"],"HOLD administrative inventory rollback")
    recorded(live["recorded_at"],time.time(),"HOLD future administrative inventory")
    need(type(d["last_item"]) is int and 0<d["last_item"]<n,"HOLD published item order")
    need(all(item["issued"]<=d["basis_at"] for num,item in items.items() if num<=d["last_item"]),
         "HOLD issued Start review predates published decision")
    review_decisions(items,run_head,n,d["last_item"])
    own_issue_only=(top==n==d["last_item"]+1 and live["main"]==d["main"])
    need((own_issue_only or live["main"]==run_head) and administrative_facts(live)==d["admin_sha256"],
         "HOLD changed administrative evidence; repeat start-check")
    cmd("git","-C",path("DESK"),"merge-base","--is-ancestor",d["main"],run_head)
    ev=Evidence(live["main"],t,top)
    agree("HOLD changed Run inventory",live,ev.book)
    host_history(ev,items,t)
    host()
    look(time.time(),d["look"])
    now=time.time()
    opening=stamp(q["spans"][seq-1]["not_before"]+"T00:00:00-08:00")
    queue_time(now,now+d["call_tail"],now+d["runner_tail"],d,opening,expiry)
    need(t<=now and now+d["call_tail"]<=d["call_by"] and now+d["runner_tail"]<=t+d["runner"],
         "WAIT handoff interval elapsed")
    # Keep the parent magistrate alive until the launcher reports the fence.
    subprocess.run(command,cwd=path("REPO"),check=True)

def reserve():
    # Executed under the lead/analyst's serialized authority to publish a reservation.
    absent(path("CUSTODY")/"desk_fence.json")
    absent(path("CUSTODY")/"hp-issue.marker")
    now=time.time()
    _,published,_,_=current_items(now)
    need(all(r["state"]=="CHECKED" for r in published),"HOLD issued HP awaiting Check")
    if published:
        census=public_hp_receipts(now)
        native={r["plan_id"]:r for r in census["receipts"].values()}
        for issue in published:
            ck=issue["check"]
            recorded(ck["at"],census["recorded_at"],"HOLD receipt coverage predates Check")
            r=native.pop(issue["dispatch"]["plan_id"],None)
            hashes=[] if r is None else [r["receipt_sha"]]
            agree("HOLD published Check and MBP receipts disagree",ck["receipts"],hashes)
            if r is not None:
                recorded(r["recorded_at"],ck["at"],"HOLD receipt postdates reading Check")
                recorded(issue["issued"],r["ended"],"HOLD receipt predates issue")
        need(not native,"HOLD orphan native HP receipt")

def main():
    sys.path[:0]=[str(path("DESK_TOOLS")),str(path("REPO"))]
    action=sys.argv[1]
    if action=="start":
        print(json.dumps(start(),sort_keys=True,allow_nan=False))
    elif action=="run-review":
        print(json.dumps(review_sheet(),sort_keys=True))
    elif action=="run":
        run()
    elif action=="before-reserve":
        reserve()
    else:
        raise ValueError("unknown desk operation")

if __name__=="__main__":
    try:
        main()
    except (OSError,ValueError,KeyError,IndexError,TypeError,subprocess.SubprocessError) as e:
        sys.exit("hp-02: "+str(e))

```

Here T is the **actual Run plan/deadline anchor**, so its fence end is T+F. The interval proof charges `b+F` once against the calendar. If the desk instead anchors the fence at a later launcher t0, include the supported startup delay before placing that fence; equivalently subtract the delay from the latest permissible decision time. Do not add startup again when it already lies inside the fence. The transfer term is the actual proven portion beyond the protected interval, including stopping the bounded copy where applicable. Budget unrelated transitions at their own steps. With no pending starts, an explicitly complete empty calendar passes this test. For a fixed T, use `a=b=T` to verify the exact arithmetic; for a real handoff allow for the remaining elapsed time. Earliest allowed start after a delay is monotone, so endpoint bounds cover intermediate selector times, including the discontinuity immediately after an end-touch. A conservative wide dispatch interval may be narrowed at start-check.

**Regression examples, conditional on the freeze’s invented timing profile.** At Friday 12:00 all three bare plans pass. The Automatic soak waits for the extra 11:45–13:15 window. S01 needs 20,420 s through clearance against 18,110 s; cede. At 12:38:29 / :30 / :31 the slack is −1 / 0 / +1 s for each span. At 12:45 and 14:00 it is +390 and +1,090 s. In the historical occupancy-only fixture at 23:59:59 the alternate window fits across midnight. Under R-c, the additional 02:00 test cedes that HP dispatch. A prospective **t0** of 00:00:00 needs the new date’s evidence and rank. In the two-dated-start fixture, a last start at 23:59:59 passes and one at 00:00:00 next day cedes. At Saturday 10:50 a selector offset of +1,350 s touches the OS window; +1,351 crosses it and incurs the wait. These are timing tests. Friday 20 Nov is outside the real queue-b interval. [Fixture, chart of cases and pin source](../d-hp02-full-occupancy-spec/FREEZE-ADDENDUM.md)

### Run and Check handoff

1. **Before dispatch.** Print the cited sources, chosen span/ARG, dispatch range, latest allowed launcher call, absolute planning bounds, through-clear time, fence, dated slack (or an explicitly empty calendar) and scope of any refusal to the ordinary start-check output. Capture the four RL-174 C lines: spotlightknowledged/updater presence, corespotlightd presence, root indexing state and Time Machine destination. Apply the ordinary measurement-mode verification, case-insensitive agent and independent process/group census, including only documented own-tree/authorized-job exceptions. Check no loaded measurement job/plist, foreign group, fence, host marker or dangling link, no maintenance or stand-down, positive instrument and disk/AC checks. Verify the RC of each command. List both authorized AC powermode commands without setting either mode. Evidence must agree with the latest receipt, including PID/start-time or group identity. Treat provider copy as an independently accounted operation.
2. **Run as last act.** The literal `run()` above fetches origin/main, reviews all intervening item bodies under P1, verifies every latched host failure against a typed lead clearance under P2, obtains the open item from that revision, loads the successful ordinary start-check result, verifies the verbatim queue expiry and typed epoch, checks the actual staged bytes and executes the pin’s real planner. Run compares the current owner inventory at its fixed public endpoint to the Start inventory. A change in scoped evidence requires a fresh Start. The desk may cite the pre-issue main while this HP item is the sole intervening item. If any other item intervenes, the current desk inventory must attest coverage through the new main tip with all scoped facts unchanged. The ordinary desk turn protects that handoff. Final operations are host verification, a synchronous read of all three look endpoints with sequence/prefix continuity, a final clock comparison against the published expiry, all other finite authorities and the supported call/start bounds, and one launcher invocation. The lead and analysts retain exclusive administrative control of publication and reservations through Check. Once invocation starts, the unchanged launcher owns its internal handoff. A host change after the final native read is a residual risk.

3. **Power ownership.** The pinned runner soaks in Automatic on AC, keeps its G0/quiet/load checks, creates its ownership marker before setting mode 2, checks High Power for each included leg, and prevents leg children changing it. The runner owns the return to Automatic. The magistrate neither pre-sets mode 2 nor performs recovery in an arm block.
4. **Check at actual fence clearance.** Use `cq-hp-02-s01-a1-<actual UTC stamp>` (or its separately issued successor) under `/Users/edr/campaign-out/cl-hp-02/`. Verify non-mock receipt, runner kind, pin, kit SHA, exact attempt/output/roster, actual ARG, planned/finished counts, rc=0, no error and terminal COMPLETE/MEASURED_OK. Run the pinned automatic cadence desk on the operational projection. Record its verdict, stops, included legs and any revocation/overtime; a failed child stays unadmitted. Verify successful restore/close steps and proof, Automatic mode 0 read back independently, no marker/link, free night lock, measurement mode restored, network time off/frequency zero, all agents/meter/volumes proven stopped and independent groups absent. An empty census cannot override a contradictory receipt. Record actual t0, close time, the HP-RECEIPT citation to the native digest, and fence clearance. Escalate LEG_OVERTIME or fewer than nine included across the block as applicable. Keep HP sealed, descriptive only, with zero reserve and outside 132, day count, line 9 and every fit. The eventual manifest names both kits, receipts, rosters and as-run positions before any HP read.
5. **Refusal, restore or debt.** An unproven restore or unowned HP marker holds the host. Once the job and fence are clear, perform one additional pinned `cadence_legs_runner.py restore-owed` through its safe recovery route and independently read everything back. Respect night-lock deferral and W1 marker ownership. A failed retry halts the host and pages Ed and the lead. A successful restore supplies the operational proof. The host halt lasts until the typed lead clearance names the failure and the later successful observation. A surviving REFUSAL, unresolved group or revoked HP admission still requires its own disposition. An in-span restore may already have made up to three attempts. Disk below floor and missing meter/collector have their ordinary stop scopes. A launcher refusal/non-clean HP Check holds the kit until an input changes; reconcile any ambiguous attempt before using any entry again. Copy at once, verify the typed manifest/ciphertext digests, size and provider readback. After at most 600 s carry unresolved debt only with the transfer stopped before soak. Notify at 2 h and daily thereafter. Retain originals until two verified off-host copies and the off-host key exist. This copy allowance is independent of the queue runway.

## Eight audits, finding by finding

**14 still apply; 16 are gone, out of 30 verified HIGH/MED rows.** Count the report rows in order (5 + 5 + 3 + 3 + 4 + 3 + 3 + 4). One row can contain several reproductions; repeated findings in different audits count as reported. “Still applies” means bad evidence, a time boundary or host drift could produce the same bad dispatch in an ordinary one-span handoff; the named check covers it. “Gone” means the reported failure requires a repeater, publication race, custom latch/journal or guard rule that this ladder does not use. The underlying fact may remain a mandatory precondition. Controls, suite reconciliation and the last report’s refuted reruns are excluded.

| Audit / row | Verified finding | Disposition under the standard ladder |
|---|---|---|
| P1.1 H | Run used a look sample from before Start passed | **Still applies.** The executing audit reached dispatch with a new reservation. Check 1 reads the register and both custody-owned public sources and compares their full dated histories. R-d excludes all reservation writers until the HP Check. Run reopens all three look endpoints and verifies the Start sequence, event prefix and per-source timestamps before launch. |
| P1.2 H | Queue-b expired during a one-second claim write | **Still applies.** An ordinary handoff also takes time. Check 4 selects the latest scoped lead decision across the complete inventory and requires the inclusive opening, ≥600 s runway at invocation and a latest possible t0 strictly before expiry. |
| P1.3 H | Host identity changed, predecessor ended after “latest”, or “proven” recovery also reported failure/open refusal | **Still applies.** Checks 6–7 bind the same host, chronology and receipt. Order the full MBP Check inventory by its original item number or ledger sequence. Check each failed restore and recovery by observation time. Require linked operational proof for that exact plan, attempt, pin and receipt, plus the typed lead clearance for each host halt. Run rereads the history and re-verifies the host. |
| P1.4 H | A blank or incomplete hp-01 t0-date census passed | **Still applies.** Check 2 requires complete coverage and reconciles the known Nov 15 receipts. |
| P1.5 M | Unavailable inst-03 lacked an entry identity | **Still applies.** Check 8 names each kit’s real candidate or terminal record and supporting evidence. |
| P2.1 H | After Run had halted on failed recovery on close 18, retry replayed close 17 | **Gone.** There is no retry with a replaceable observation. Any new start uses the latest public Check and the unresolved host stop under check 6. Replaying a clean older Check cannot clear that stop. |
| P2.2 H | Same issue forgot a confirmed look execution on a later read | **Gone.** No authorized same-issue retry. Check 1 reads the full execution history; a later summary never retracts a genuine start. |
| P2.3 H | Same predecessor Check ID carried different hashes/end times | **Still applies.** Checks 4 and 7 join published Checks to the MBP native receipts in both directions. They reject a shared digest, conflicting digests for a plan and attempt, conflicting close times, and a repeated Check ID. |
| P2.4 H | S01 accepted history with all of s02 already spent | **Still applies.** Check 4 derives the spent prefix from published Checks and native receipts, compares all 12 summary entries, and refuses reissue of the same attempt. |
| P2.5 M | Inst-03 borrowed inst-02’s unavailable entry and evidence | **Still applies.** Check 8 deduplicates the original `(source, entry)` behind each projection. Two projections of one entry supply one piece of evidence and leave the second kit unproven. Distinct entries from a shared document can support separate kits. |
| P3.1 H | Queue was valid at dispatch but expired at the launcher’s computed t0 | **Still applies.** Check 4 and the Run clock limit cover the actual handoff, including startup; equality at expiry refuses. |
| P3.2 H | Run sampled after Start’s clock but before receipt publication | **Gone.** The last-act look read follows publication of the ordinary typed item. There is no separate Start receipt to order. |
| P3.3 M | Removing the 01–14 daily completion did not change synthetic inputs; kit 15 could spend rank 1 | **Still applies.** Check 8 binds the dated completed leg, its base-kit ID, pin and Check, or verifies a complete no-eligible-base census. |
| P4.1 H | Saturday’s rank-1 proof authorized a Sunday t0 | **Still applies.** Checks 2/8 cover the proposed dispatch date, including launcher delay. Crossing midnight before t0 requires Sunday’s start-check. |
| P4.2 H | Inst-03 reopened at 13:15 while HP was being handed off | **Still applies.** Check 8 excludes a dispatch range spanning a higher rung’s actual eligible start. Shorten the range or re-rank. |
| P4.3 H | Host left Automatic during the claim write | **Still applies.** The private claim write is gone, but mode can drift during normal bookkeeping. Check 6 and the final native Run read cover that interval. |
| P5.1 H | A final-read look execution was lost on same-issue retry | **Gone.** No same-issue retry; check 1 retains the terminal fact in the public execution history. |
| P5.2 H | Reservation, same-date census and unproven group stop each disappeared on retry | **Gone.** No retry takes a replacement envelope. Checks 1/2/6 respectively require reservation disposition, complete dated records and positive group/receipt agreement. |
| P5.3 M | G1 omitted the boundary where 600 s of runway remains | **Gone as reported.** Its trace had 601 s at final read **and at launcher invocation** and 599 at bootstrap. Check 4 protects the runway through invocation; startup can consume it. Exclusive expiry still covers actual t0. The retired 120 s pre-boundary exclusion would be a second margin. |
| P5.4 M | The frozen launcher wrote runner.json/plist/fence between final read and bootstrap | **Gone.** r6 expressly scoped G2 to invocation. The standard Run ends in the unchanged launcher and accepts its documented internal handoff. |
| P6.1 H | Higher-rank cede and failed AC read left no holds; retry reused an earlier clear observation | **Gone.** No open-hold ID or replay path. Cede under check 8; failed native read withholds launch under check 6. |
| P6.2 M | G1 missed the startup-adjusted latest counted-start boundary | **Gone as reported.** The probe was still 90 s before the last safe decision; it violated a 120 s software guard. Check 5 retains the real startup/fence/transfer arithmetic and refuses an actual miss. |
| P6.3 M | Missing safety record raised during hold creation, stranding Start without a clearable ID | **Gone.** Unreadable proof exits the ordinary start-check; a new complete check is possible without repairing an unfinished HP ledger. |
| M1.1 H | Replacement issue missed an interrupted Start marker for the same queue position | **Gone.** No HP in-flight marker or replacement protocol. The magistrate reconciles actual fence/output and unspent roster before any issue. |
| M1.2 H | Stale Check correctly refused but wrote no L1 issue hold | **Gone.** The ordinary refusal suffices. Check 6 still rejects stale host evidence. |
| M1.3 H | Issue-ledger lock EIO correctly refused but wrote no Q2 queue hold | **Gone.** No HP issue lock or secondary hold store. Unreadable required records fail the standard check. |
| M2.1 H | Journal metadata EIO created a second sequence 00000001 | **Gone.** No HP journal, queue failure record or sequence allocator. |
| M2.2 H | Compound fence/date conflict persisted only one latch, or G1 suppressed the date latch | **Gone.** Check 5 requires both inequalities to pass on the same snapshot. Clearing a recorded reason cannot make the other inequality true. |
| M2.3 H | At 13:15:01 Issue/Start accepted a 13:14:59 instrument census | **Still applies.** Check 8 derives contemporaneous eligible starts from public entries on their own pins; the clock test makes the old sample unusable. |
| M2.4 M | Successful recovery left a separate restore_stop after fence disposition | **Gone.** There is no second stop cache. Check 6 applies the identified proven recovery and evaluates any independently open stop. |

P1–P6 are the six pre-machine final verdicts and M1–M2 the two frozen-machine verdicts. [P1](../pl-hp02-successor/void-premachine-audit-1/FINAL-MESSAGE.md) · [P2](../pl-hp02-successor/void-premachine-audit-2/FINAL-MESSAGE.md) · [P3](../pl-hp02-successor/void-premachine-audit-3/FINAL-MESSAGE.md) · [P4](../pl-hp02-successor/void-premachine-audit-4/FINAL-MESSAGE.md) · [P5](../pl-hp02-successor/void-premachine-audit-5/FINAL-MESSAGE.md) · [P6](../pl-hp02-successor/void-premachine-audit-6/FINAL-MESSAGE.md) · [M1](../pl-hp02-successor/audit-1/FINAL-MESSAGE.md) · [M2](../pl-hp02-successor/audit-2/FINAL-MESSAGE.md)

## Text to issue for hp-02-s01

Render the following once the magistrate has a passing start-check and the lead has admitted queue-b. Use the normal `run_state_add.py` numbering and serialization. The literal queue timestamp below is the source for the typed `expires_epoch_s` value of 1796025600. Replace each angle-bracket field with a real value from the same activation. `N` is the assigned integer; `ISSUED_EPOCH` is the actual issue epoch. `CHECK_BY` is a real offset-qualified reporting deadline chosen by the lead from the latest permitted fence end and Check target. `sets` stays empty unless a specific preceding item has actually been checked and the issuer is recording its closure. The item string below intentionally authorizes only s01.

~~~~markdown
<N>. **Laptop lead, <issue local date/time PST>: MAGISTRATE — hp-02-s01 ISSUED at filler rank 3, cq-hp-02-s01-a1, L001–L003 only, one launch as the last act.**

```pointer
owner: magistrate
wait: none
deadline: <CHECK_BY>
on_early_or_refused: Check at early fence clearance. On ordinary launcher refusal, missing required proof or non-clean HP Check, record the reason, hold cl-hp-02 until an input changes, notify Ed and the lead, reconcile the attempt and take the next safe eligible rung. A timing cede returns to the ladder. An unresolved host restore stops host dispatch. Halt and page Ed and the lead on failed pinned restore. If the Check is missing by the deadline, report it. At a clean close resume the eligible ladder.
next_observable: <activation>/run-out.txt reports the launcher result and fence for cq-hp-02-s01-a1. At first fence clearance the magistrate checks the actual stamped output, copies at once and records the operational Check and restore in RUN_STATE.
```

```item
{"expires_epoch_s": 1796025600, "issued_epoch_s": <ISSUED_EPOCH>, "number": <N>, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- Issue one attempt for block hp-02, queue cq-hp-02-b seq 1, hp-02-s01, ordered L001,L002,L003, attempt 1.
- Latest clean MBP Check <original item number or ledger sequence, host, receipt SHA, end and fence-gone>. No named HP predecessor for s01. Current 12-leg roster, published HP issue/Check history and independent MBP receipt index <refs>. All three agree at the Start clock.

Queue-b expires_at=2026-11-30T00:00:00-08:00

HP-DISPATCH <single-line JSON from this activation's successful start-check stdout>

- Runner dd206025abb30fd5c07515cd4b34b3e653174810, cadence-legs-v1, cl-hp-02 SHA-256 7693b8293b42b8ba20cbd321e201974745b172dc53c4f1397d2c1494f38fbe66.
- Current lead admission <latest original item number or ledger sequence for this queue SHA, effective status and later dispositions>. Cite the complete applicable host, queue and kit histories and the latest linked recovery for each outstanding fault. A newer refusal, revocation, failed recovery or unproven recovery holds dispatch. Admitted queue e3eaa282f9d4cea3b579eeb7bde989ff897df45e:docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203/hp-02/queue-b.json, SHA-256 078eb24c3149f2a7bc522a432098e51e21bd36278d288b0f41efbb5d57da528f. Local opening 2026-11-21 00:00 PST, exclusive expiry 2026-11-30 00:00 PST. Run verifies this item's integer expiry and exact queue timestamp, and requires at least 600 s at launcher invocation.
- LINE2_OK=yes. (1) RS338 at 6640a66719a2ff1f8cc38dbce3e8231f419e79d8, four-part line 2, cl-hp-01 SHA-256 7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965. (2) HP02-DELTA.md beside that queue at e3eaa282f9d4cea3b579eeb7bde989ff897df45e finds hp-02’s frozen block byte-equal to hp-01’s at the same pin, 37 paths. (3) Line 2 for `cl-hp-02` (`7693b829…be66`) is `cl-hp-01`'s record under RL-165 §5; no frozen byte differs (RL-190 2).
- From publication until the magistrate records the HP Check, the lead and all analysts must make no look reservation. Every look executor must refuse if the desk fence or HP issue marker exists, including this unchecked published item after fence clearance. Serialize reservation commits and HP publication with the lead. At Run read the latest look ledger and both current custody histories. Require the issued sequence and event prefix to survive and each source clock to be at least its Start value.
- Start-check <activation>/start-check.out, rc 0 at <clock>. Current no-execution/no-reservation evidence <ledger, independent MBP and AIR locators, event sequences and original timestamps>. All three histories agree. The HP-DISPATCH payload records their Start sequence, prefix digest and source dates. Complete hp-01 t0-date census <ref>; proposed LA date <date> clear. READY disposition and dated counted positions, effective holds and legal start intervals <refs>, dated rank-1 base-kit Check or eligible-pool census <ref>, individual rank-2 dispositions with distinct original source entries and RS480 decision <refs>. HP is next. Host preflight/close, censuses, copy or stopped transfer/debt and scoped stops <refs>.
- Run P1. In this Run turn fetch origin/main and read RUN_STATE.md at the fetched head. Review the complete text of every item numbered after this issue and any item between Start and issue. Refuse this dispatch if any revokes queue-b or hp-02, holds cl-hp-02, or reports a halt or refusal for this MBP, even if a subsequent item clears it. For intervening items record the head, this issue number and each disposition and passage in the activation’s run-decisions.json. Bind each reviewed item’s complete text by SHA-256. The Run block fetches again and verifies complete coverage through its own head. An unknown disposition or a fetch or read failure holds the kit.
- Run P2. Reopen current host Checks and the complete MBP recovery history. A failed or unproven restore or unsuccessful recovery holds the host until a typed LEAD RUN_STATE clearance names that exact failure and its linked successful proof on the same host, Check, receipt, pin, plan and integer attempt. Check the observation clocks. The proof must strictly follow the failure and be published by clearance. A later magistrate success or a late filing of an older observation leaves the host halted. Verify each clearance before the final host and look checks.
- ARG <selected explicit window> is explicitly certified by <timing record and timestamp> for this ordered roster. Plan worst 16,650 s, item fence 18,110 s from actual Run plan anchor. Approved plan range <a..b>, call by <clock>, latest possible t0 <clock>. Composed work/close/outer bound <values and source>, all remaining dated starts and slack <refs or confirmed empty>. Run <activation>/run-block.sh after publishing this item and completing ordinary notifications. Bind the published HP-DISPATCH line to start-check.out. Rehash the staged kit against this item's digest. Assert campaign, exact ordered L001,L002,L003, argument and stamped output. Replan at actual t0 and enforce R-c on HP work, including tomorrow’s 02:00–02:35. At 01:55 with no eligible substitute, wait to 02:35. Verify host Automatic/clear, reread the look register and invoke the pinned launcher once, exit on fence claim. If the dispatch no longer fits, return to the ladder.
- The runner owns Automatic soak, G0, marker, High Power 2 and restore. Check <activation Check template> for cq-hp-02-s01-a1 under /Users/edr/campaign-out/cl-hp-02/ after clearance: exact kit/pin/ARG/roster, automatic desk, mode-2 included legs, mode-0 independent restore/readback, cleared marker/lock/groups, stopped feeds, scoped stops and copy. Report to the lead by <CHECK_BY>. For an unproven restore or unowned marker, hold host, one safe pinned recovery after job/fence clearance; if still unproven, halt and page Ed and lead. For the Check heading, use its assigned number followed by `. **Magistrate HP CHECK #<N> for cq-hp-02-s01-a1.**`, with a typed set closing item <N>. If the original is administratively CLOSED, VOID, EXPIRED or SUPERSEDED, publish a subsequent CLOSED Check with the same exact heading and no repeat transition. For a receipt-bearing Check, put `HP-RECEIPT` and the actual lowercase native SHA-256 on a line of their own, separated by one space. The lead and analysts may resume reservations only when the matching Check is already effective at the reservation clock, the MBP receipt index agrees, and the fence and local marker have cleared. S02 needs this clean Check and a fresh single-span issue.
~~~~

## Retain, retire and verify

**Retain byte-for-byte** the original six evidence fixtures. The first four are from the post-R1 issuability seat. The last two are the occupancy seat’s archive and regression driver. Keep the addendum itself (SHA-256 `77f34fae9bd88ae415d7b949ef6ea6ac68759b1ef47aec214a50c32317ad99c4`), the admitted queue-b binding, the preserved superseded queue-a for replay, the kit, the independent HP delta, RS338/inherited smoke and the RL-190 line-2 record. Use the pin’s real pure arithmetic in the start-check. Keep the original vectors and their context, including legacy gate-phase labels, queue-a examples and invented timing assumptions. They can be exercised as pure decision cases; they confer no live authority.

| Fixture | SHA-256 |
|---|---|
| `item-cases.json` | `fa13f60290d7830a69b77a3e0734378009bca15a18a8498d94b253924a9ac8dd` |
| `check_contract.py` | `c73506b716e770c1590bcb6bf5b5e7d10eb7c194a60b24249952e008eca1223b` |
| `replay_legacy.py` | `92f386d454a31c8c7f2bbdc8fbe5b5dc3860fdce954f4bcbe3262caba84ec112` |
| `review_kit.py` | `d3344f2e628a35632ea1d2f3d37480cc6a66837d44d307f784e76c4fcfea2a9d` |
| `hp02-occupancy-fixture.zip` | `9ae11ae62e91a79ca26eb5e742371a86f7b57e7b940d2a622e13f2ef56e7244f` |
| `successor_regression.py` | `f28df8c505128d360de4345cb16fec4a7d1f7575fcda451b627c72c3decf3aab` |

**Retire the proposed automaton as an issuing mechanism.** Archive its PR history, three generated Issue/Start/Run programs, `hp_gate`/custom stager admission protocol, separate observations and Start-publication receipts, claims/retry machinery, host/admission database, per-issue and per-queue latch journals, interrupted-read markers, lock/replacement handling, disposition sequence numbers and second restore-stop cache. Retire r4 R2, the universal r5 G1/G2 automation, r6 L1 and Q2/Q3’s secondary custody machinery. Keep r4 R1’s runway, R3’s rank-1 evidence, Q1’s factual execution bar and normal last-act host verification. Archive the *different* six-file gate-machine suite, both freeze versions and their 374,900-assertion history as engineering evidence. They do not define acceptance for the magistrate’s template. No frozen kit, launcher, raw evidence or prior item needs editing. [r4](../pl-hp02-successor/lead-rules-r4.md) · [r5](../pl-hp02-successor/lead-rules-r5.md) · [r6](../pl-hp02-successor/lead-rules-r6.md) · [Machine-suite freeze](../astra-hp02-gate-suite/DELTA.md)

Keep retired fixed Saturday/same-date qualification, 00:30 cutoff, synthetic guard windows, fixed rest intervals, kit/item age, three-ahead cap, watcher and line-9 gates out of the new item. The actual finite queue interval still binds. RL-190 §2.4 and R-d require the ordinary start-check attestation, publication under the reservation exclusion, and the fresh Run read. A checked and cleared issue releases this exclusion. A known revocation, intervening span or dispatch outside proved bounds requires a fresh standard decision.
 
## Earlier fixture regressions retained

The replay drivers exercise the literal shell and Python above with public-evidence fixtures. The ordinary Run uses the pinned planner, native kit/queue validators and a recording launcher. A disposable Git main holds the rendered item and each successive Check. Host commands and clocks are simulated. The original audit reports, JSONL and frozen fixtures remain intact.

| Round-two finding | Regression and acceptance condition |
|---|---|
| 1. Counted programme | At 14:00 a ready counted position with a long legal window cedes, including when its rank summary says exhausted. A position reopening during handoff also cedes. A scoped hold covering handoff permits HP when the later dated start still fits. |
| 2. Historical restore and stop | An older failed restore and unproven group stop survive an unrelated clean Check. A linked restore alone still refuses. Under P2 the restore also needs the typed lead clearance naming the failure and the later successful observation. Wrong plan, attempt, pin, receipt, group subjects, readback or recovery RC refuses. A failed additional recovery leaves the host halted pending the lead's disposition. |
| 3. Underlying evidence | Distinct inst-02 and inst-03 projections citing the same original source and entry withhold HP. Two separate entries in one source pass. Crosswalk row P2.5 uses the underlying alias as its regression. |
| 4. Exact Check identity | Both the normal closing set and a separate operational Check bind the whole original item number and plan. A Check for a10 cannot release a1, even after VOID. |
| 5. Administrative CLOSED | Administrative closure alone excludes reservations. A subsequent exact CLOSED operational Check releases them after fence clearance. An earlier standalone Check cannot release a later closure. |
| 6. Numeric wire types | The predecessor accepts integer 1 and refuses true and 1.0. The probes also substitute booleans for timing, mode, instrument size, issue and recovery fields. |
| 7. Published expiry | The rendered item contains the verbatim queue timestamp and epoch 1796025600. A different expiry refuses even if it would leave 601 seconds. A late final clock with the authentic item refuses after expiry or at 599 seconds. At the queue predicate, 599/600/601 gives refuse/allow/allow. The same inclusive cutoff is exercised at the literal Run entry using a finite daytime admission and its supported time to invocation. HP work starting in the actual queue's last ten minutes would also cross the next day's RS480 window. |

## Round-four verification and handoff

| Round-three execution finding | Round-four regression and positive control |
|---|---|
| Completed s01/a1 reissued | A fully receipted s01 permits s02 with the correct spent prefix. Marking the same legs unrun refuses. Forcing a second typed s01/a1 with matching local dispatch bytes also refuses at Run. |
| AIR in the MBP slot | Start checks each fixed custody root. Run reopens those same roots at its last evidence read. An AIR copy, a missing MBP file and two histories that both say clear but disagree on a released reservation all refuse. Three matching histories containing the release pass. |
| Future Check frees a look | Future normal and standalone Checks refuse at the reservation clock. A separate Check dated before its administrative close refuses. The same exact Check after closure, and a legitimate Check after actual expiry, release. An otherwise valid Check citing a receipt published one second after that Check also refuses. |
| Incompatible predecessor receipts | Distinct checked s01 and s02 receipts admit the s03 control. A shared digest, two digests for one attempt, an omitted receipt, an omitted Check, an orphan receipt, or a disagreement on the native roster or outcome refuses. |
| Timing source denies its selected window | A one-window allowlist and a map granting just the selected argument pass. A string containing the window, an explicit false grant, null, numeric one, or another non-boolean value refuses. The Run regression supplies the same malformed grant in both local and published dispatch records. |

These commands and linked results record the round-four replay of the archived [round-four spec](SPEC-v4.md). The round-five commands below adapt the existing fixture publisher to the ordered evidence format. The crosswalk also compares each historical row to its original report.

| Command | Fixture coverage |
|---|---|
| `python3.13 -IB verify_round4.py` | All 53 original audit case IDs, the 30-row crosswalk, s01–s03 positives, eight precondition negatives, real typed-item and pointer validation, 54 frozen occupancy cases, 11 dated pairs, six fixture digests and the addendum. [Results](results-round4.jsonl) · [Driver](verify_round4.py) |
| `python3.13 -IB probe_prior_round4.py` | Earlier executing probes for dated rank, linked recovery, source-entry identity, exact attempts, administrative closure, strict numeric types and inclusive expiry. [Results](probes-prior-round4.jsonl) · [Driver](probe_prior_round4.py) |
| `python3.13 -IB probe_round4.py` | Every case ID and expected decision in the audit’s 29-row round-three log, with additional independent source, clock, false-flag and failed-Run controls. [Results](probes-round4.jsonl) · [Driver](probe_round4.py) · [Executing audit](../d-hp02-ladder-audit/AUDIT-r3.md) |

The revised fixtures publish dated predecessor items and independent operational receipt and custody records. The earlier release control now reads its Check after the published timestamp. The linked-recovery positive uses a prior instrument attempt so it tests recovery independently of reissuing a completed HP attempt. Host commands and the launcher are fixture adapters. The pinned planner, validators and Markdown entry points execute on a disposable Git main. The source worktree’s Git pointer was unavailable, so versioned public objects and the read-only review clone supplied the source comparison. Hardware evidence remains PROVISIONAL. The next operational step belongs to the lead and magistrate when queue-b admission, the owner views, timing bounds and a fresh start-check are available.

## Round-five verification and handoff

The executing audit’s findings 1 and 2 reproduce operational mistakes. A stale queue selector omitted a revocation still present in the owner inventory. A stale host selector omitted a later failed recovery on the same MBP. Both hold at Start. A change in those authorities between a passing Start and the first Run also withholds the launcher. Finding 7 is the separate Run reread regression. A rollback from two released look events to zero refuses even when all three endpoints agree. An unchanged sequence and prefix on a fresh read passes. Findings 3–6 are the explicitly excluded forgery scenarios in the lead’s 09:52 ruling. The historical ladder crosswalk still counts 14 retained and 16 retired findings.

The round-five archive below used `python3.13 -IB verify_round5.py SUITE` for each listed suite. Round six tightens the former positive controls for host clearance and intervening decisions. The driver reuses the archived probe actions and reads the literal Python and shell blocks from this file. It supplies invented source coordinates in the fixture publisher, uses disposable Git history and records launcher calls. All host and clock effects are simulated.

| Suite | Regression record |
|---|---|
| `original` | Original 53 IDs, 30-row crosswalk, three positive spans, one refusal per precondition, frozen fixtures and occupancy. [Results](results-round5.jsonl) |
| `r2`, `r3` | Previous audit probes for rank, exact attempts, linked recovery, expiry, custody and evidence agreement. [Round two](probes-r2-round5.jsonl) · [Round three](probes-r3-round5.jsonl) |
| `r4` | Original executing auditor’s most recent adverse/control pairs, with the lead’s scope applied to each row. Refusal at Start prevents publication of that issue. [Disposition and results](probes-r4-round5.jsonl) |
| `latest` | Reversed list order, backdated effective/close times, omitted queue and host records, later recovery failure, scoped kit refusals, stale timing, first Run after changed authority and look continuity controls. [Results](probes-latest-round5.jsonl) |

The lead may use the s01 item template once queue-b is admitted and the magistrate’s current public sources, timing evidence and MBP start-check pass. Hardware validation remains PROVISIONAL.

## Round-six verification

Run `python3.13 -IB verify_round6.py` for the two lead rulings and `python3.13 -IB verify_round6.py original` for the original dry runs, frozen occupancy cases and 30-row crosswalk. Both use disposable Git repositories, an invented MBP history and a recording launcher. The independent round-five positive is exercised twice under P2. A lead-owned ledger entry alone holds. The same later operational proof, explicitly cited by a typed lead RUN_STATE item naming each failure, permits the clean control. The separate-reader P1 control starts without the intervening commit in its object database. Its Run fetches, reviews the unrelated item and dispatches. Removing access to its remote makes the next Run refuse. [P1 and P2 probes](probes-round6.jsonl) · [Original dry runs and crosswalk](results-round6.jsonl)
