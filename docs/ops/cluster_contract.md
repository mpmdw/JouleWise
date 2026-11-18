# Cluster contract: #799 desk-final, #800 queue controller, #804 span offload, #807 close-offload

Design seat: Mythos 5.2, 2026-11-17. L1–L6 were adopted by the lead in [RUN_STATE item 399](../../RUN_STATE.md). This contract governs the member PRs. Step 1 adds the shared primitive and synthetic tests.

## 0. Basis, pins and limits

**Pinned heads (every `file:line` below is at these commits).**

| PR | Branch | Head read | Note |
|---|---|---|---|
| #799 | `align/2026-11-15-desk-final` | `3747167f4` | base is #794 (`align/2026-11-14-qual-pin`), unmerged |
| #800 | `cadence/2026-11-15-queue-controller` | `ce5097e95` | not a descendant of #799's head (see D8) |
| #804 | `ops/2026-11-15-air-independence` | `5755eef52` | admitted at `ccfe442b6`; head has moved since |
| #807 | `ops/2026-11-16-close-offload` | `57f9149ce` | contains `ccfe442b6`, not #804's head |
| main | | `b85392369` | RUN_STATE items 388, 395, 396 |
| audit | `audit/2026-11-10-fable` | `b26c0d0e7` | RL-172 to RL-175 |

Citation form: `#800:scripts/cadence_controller.py:2322` is that path at #800's pinned head. `main:` and `RL:` (the decision log, `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`) likewise.

**Design review scope.** Read the four PR bodies, the seam code at the pinned heads, the round 9 and 10 reports, the #804 and #807 review reports, the Astra ops audit, the cold review, RL-172 (c)(g)(i), RL-173, RL-174 A and D, RL-175 B.1 and E, and RUN_STATE 388, 395 and 396.

**Limits of the design review.** The design seat made its findings by reading. Every defect I add beyond the Astra and cold-review findings is **by reading** and is marked so; each has a scenario in section 3 that would confirm or refute it. I did not read the gate 1 to 4 seat reports themselves, only their dispositions in the PR bodies. I opened no fixture, custody, energy, power, meter, transcript, slot, hazard, sealed or restricted file. No SSH, no push, no PR edit. The two builders are still pushing, so line numbers will drift; the pins above are what the citations mean.

**Why the cluster does not converge, in one paragraph.** Each PR is reviewed and tested against its own model of its neighbours. #800 tests #807 through a stub (`#800:tests/cadence/test_cadence_controller.py:1278-1290`, `synth.stub_controller_owned_close`); #807 tests the controller through a hand-written fence file (`#807:tests/test_close_offload.py:285`). No test runs two PRs' real code together. Meanwhile three different blobs of `joulewise/span_offload.py` exist (D1). So every seam has two or three implementations, each correct against its own tests, and each review round finds the next place where they differ. The fix is one home per seam, and one suite that binds only real code.

### Design rules the rest follows

| # | Rule |
|---|---|
| K1 | **One home per seam.** A shared artifact has one writer function and one validating reader, in one module. Every other PR imports it. Nobody copies it, wraps it with extra conditions, or keeps a private blob. |
| K2 | **The artifact is the truth.** A cached claim about it (`published`, `ok`, a remembered tip) is advisory and is reconciled against the artifact at every read. |
| K3 | **Readers never mutate.** An interrupted publication is finished by the publisher, under the publisher's lock. A reader that meets one reports BUSY. |
| K4 | **The fence mutex is short; ownership is the record.** `.desk-fence.lock` guards a read-modify-write of `desk_fence.json` and is held for seconds. Owning the host for an hour is expressed by the record (purpose, pid, deadline), never by holding the mutex. |
| K5 | **Wall-clock order across processes is never validity.** Binding is by content (names and hashes). Leases are enforced on both the wall clock and the same-boot monotonic clock. |
| K6 | **Deleting an original is opt-in.** The default is retain. A raw directory is retired only when this invocation names it and no hold names it. |
| K7 | **Deployment gaps fail before a span runs.** Missing config or attestation is refused at startup and in the arm proof, never discovered at the gate after the span. |
| K8 | **HOLD versus HALT.** HOLD (wait, automatic retry, page only at the stall bound) when re-observation can clear it: an absent artifact, a busy lock, a provider or network failure, an expired lease with a provable no-launch. HALT (page, needs acknowledgement or disposition) only for a contradiction between authorities, an integrity failure of an immutable artifact, or an indeterminate launch. A failed read is never a value (not empty, not clean, not zero). |

---

## 1. The state machine

### 1.1 Two drivers, one machine

The **driver** is the process that owns the host between runs.
- **Controller mode** (after #800 is admitted): `scripts/cadence_controller.py`, a LaunchAgent in the MBP user's GUI domain.
- **Magistrate mode** (now; RL-173 D, items issued ahead): the magistrate activation, working from an issued item.

The states, artifacts and seam interfaces are the same in both. Only the driver's own records differ (controller state directory versus RUN_STATE items). The Air owns no transition on the arm path (RL-173 A, `RL:17447`; RUN_STATE 388, `main:RUN_STATE.md:2167`).

### 1.2 States of one span (plan `P`, output directory `OUT`)

| State | Meaning | Durable fact that defines it |
|---|---|---|
| S0 QUEUED | The span is on a committed queue, or drafted as an item | Queue entry on the audit branch (A1) |
| S1 ISSUED | Authority to arm exists and is unexpired | Controller: queue valid, notice posted. Magistrate: issued item under 24 h |
| S2 ARMING | The driver has committed to one launch attempt | Arm intent published create-once (A2) |
| S3 LIVE | The launcher's fence names a live LaunchAgent | Fence record with a launch purpose (A4); arm record (A3) |
| S4 RUN_ENDED | Launch fence gone, process group absent | Observed; nothing written yet |
| S5 CHECKED | Typed close: `CLOSED_OK`, `STOPPED`, `REFUSED`, `STRANDED`, `CLOSE_UNPROVEN` | Check record (A6) |
| S6 BUNDLED | Signed bundle commit exists on the remote | `refs/heads/desk-bundles/P` (A7) |
| S7 JUDGED | The MBP desk has published a verdict | `refs/heads/cadence-desk-mbp/P` (A8) |
| S8 COPIED | Verified cloud copy, bound to `OUT`, transfers clear | `P.ok` (A10) accepted once by `copy_evidence` |
| S9 DESK_FINAL | Counts for line 9 | A counted final verdict; hand table if due; no desk disagreement |
| S10 RETIRED | Raw original removed; local archive kept | Retirement record (A12); `OUT` absent |
| S11 EVICTED | Local archive removed; two verified copies off the MBP | SSD receipt (A11) validated at reclaim |

S6, S7 and S8 are reached in that preferred order (RL-174 D.2, `RL:17636`) but **S8 does not depend on S6 or S7**: copying is always allowed. Retirement (S10) depends on S8 and S9 and on the release rule of seam E. S11 is never on the arm path.

### 1.3 Transitions

| # | From → to | Trigger | Owner process | Commit point (the write that makes it true) | On failure |
|---|---|---|---|---|---|
| T1 | S0 → S1 | Lead commits queue or issues item | Lead | Audit-branch commit | No arm |
| T2 | S1 → S2 | All arm conditions hold on two authority reads | Driver | `intent.json` linked into place | HOLD (reasons recorded); nothing written |
| T3 | S2 → S3 | Arm child: fence transfer, then bootstrap | Arm child, then LaunchAgent | Launcher's `write_fence` under the mutex; `arm.json` | See seam D: void (HOLD) or indeterminate (HALT) |
| T4 | S3 → S4 | Runner exits; wrapper clears its fence | Runner wrapper | Fence unlinked | Fence past deadline: `STRANDED_ALARM` page, no close while a PID lives |
| T5 | S4 → S5 | Driver takes the host fence, proves the close | Driver | `close.json` (controller) or the Check item (magistrate) | `CLOSE_UNPROVEN`: HALT |
| T6 | S5 → S6 | Pack, sign, push once | Driver | Remote ref created | HOLD, retried each tick; does not block T8 |
| T7 | S6 → S7 | `cadence_desk.py final`, then `publish_verdict(push=False)` | Driver (desk step, no agent) | Local ref tip read back | No verdict: HOLD, re-run. Unverifiable verdict: HALT |
| T8 | S5 → S8 | `close_offload.py after-check` | Close tool, as the driver's child | `P.ok` linked into place | Exit class decides (seam B table) |
| T9 | S7 → S9 | Verdict counted; off-host re-check agrees when present | Driver (law) | Derived at every read from A8; nothing cached | Disagreement: HALT to the research lead |
| T10 | S9 → S10 | A later `after-check --retire P` | Close tool | `.retirement.json`, then rename, then removal | Seam E |
| T11 | S10 → S11 | `close_offload.py reclaim --ssd-receipt` | Close tool, any later close interval | Archive unlinked after both copies verify | Never forced; ≤ 60 GB mails the lead only |
| T12 | successor S1 → S2 | Next arm | Driver | As T2 | As T2 |

**What the next arm (T12) requires of earlier spans.** Predecessor at S5 clean, or dispositioned. Every span in the copy-due set at S8. Span k at S9 with its Q1 record before span k+2 (RL-173 E, `RL:17497`). Gates released. Gap floors. Fresh watcher. A fresh `ICLOUD_CLEAR` (RL-174 D.1, `RL:17621`). None of S10 or S11.

### 1.4 Durable artifacts

| # | Artifact and path | Schema (fields) | Single writer | Readers | Crash rule |
|---|---|---|---|---|---|
| A1 | Queue, standing index, gate records, dispositions, Q1 records: `<records_dir>/…` on the audit branch | `joulewise.cadence_standing.v1` (`#800:joulewise/cadence/standing.py:39`, keys `:289-292`); Q1 `desk_final.Q1_RECORD_SCHEMA` | Lead | Controller; desk (queue commit named in `transition.json`) | Git |
| A2 | Arm intent: `<state>/spans/P/intent.json` | `joulewise.cadence_controller_record.v1`: `plan_id`, `span`, `queue{path,queue_id,sha256,commit,first_commit,audit_tip,role}`, `kit{sha256,campaign_id,frozen_commit,path}`, `output`, `leases{}`, `lease_until`, `arm_proof_sha256`, `watcher`, `notice`, `predecessor`, `decided_epoch` (`#800:scripts/cadence_controller.py:1877-1901`). **Add:** `standing{purpose,pid,deadline}`, `lease_mono_until` | Controller, create-once | Controller (restart, close, desk step) | Published complete or absent (seam I0) |
| A3 | Arm record: `<state>/spans/P/arm.json` | `status` ∈ `LIVE`, `VOID`, `LAUNCH_REFUSED`, `INDETERMINATE`; `t0_epoch`; `fence_purpose`; `arm_command` (`:1971-1981`) | Controller | Controller | Atomic replace |
| A4 | Fence: `<custody_root>/desk_fence.json`; mutex `<custody_root>/.desk-fence.lock` | Exactly `{purpose:str, pid:int>1, deadline:epoch}` (`main:scripts/launch_align_r0.py:80`) | Whoever owns the host at that instant, always under the mutex: controller (`cadence-controller:<token>`), launcher (`align-r0:<token>`), close in self mode (`close-offload:<token>`), watchdog (stale removal only) | All of those | Temp plus `os.replace` (`main:…launch_align_r0.py:89-101`) |
| A4b | Lease expectation: `<state>/standing-lease.json` | The fence record, or `{handoff}` | Controller | Controller | Written before the fence (`#800:…cadence_controller.py:1226-1229`) |
| A5 | Runner receipt: `OUT/runner_receipt.json` | Pinned runner's (frozen) | Pinned runner | Controller close; desk through the bundle; offload (presence and bytes only); close scan (`lstat` only) | Runner's |
| A6 | Check record. Controller: `<state>/spans/P/close.json` and `transitions.jsonl`. Magistrate: the Check item on main plus its mail (388 fallback 3) | `status`, `close_proof`, `close_proof_sha256`, `receipt_epoch`, `manifest_sha256`, `gates`, `pushed`, `bundle_commit`, `mbp_desk{}`, `offload{}` (`:2158-2167`). **Add:** `receipt_sha256`, `copy{status,marker_sha256,accepted_epoch}` | Driver | Driver law; lead | Atomic replace |
| A7 | Desk bundle: `refs/heads/desk-bundles/P` | Signed parentless commit: `bundle/<layout>` and `transition.json` (`joulewise.cadence_controller_transition.v1`) | Controller key `cadence-controller`, created once (`:543-558`) | Both desks | Same tree on retry is success |
| A8 | Verdict refs: `refs/heads/cadence-desk-final/P` (off-host, principal `cadence-desk`, pushed); `refs/heads/cadence-desk-mbp/P` (MBP, principal `cadence-controller`, local) | `desk_verdict.json` (`desk_final.VERDICT_SCHEMA`: `desk_final`, `next_arm_hold`, stops, hand gates, `verdict_sha256`, `summary_sha256`, `history_source`, `desk_code`) and `desk_summary.json` | `desk_transport.publish_verdict` only (`#799:joulewise/cadence/desk_transport.py:260-315`) | `read_verdict` (`:318-344`), `history_from_records` (`:366-381`) | CAS and read-back |
| A9 | Copy stage: `<stage_root>/P/` | `P.tgz.enc`, `P.key.enc`, `P.SHA256SUMS`, descriptor (`created_epoch_s`, `pack_verification`), `.source.json` `{source: realpath(OUT)}` (`#804:joulewise/span_offload.py:1254-1270`) | `span_offload.build_stage` under the plan lock | Offload, close, reclaim; controller only through `copy_evidence` | Built privately, renamed complete (`:1280`) |
| A10 | Copy marker: `<marker_dir>/P.ok` | `joulewise.span_offload_marker.v1`: `plan`, `span_name`, `written_epoch_s`, `backend`, `provider_confirmed`, `recipient_sha256`, `manifest_sha256`, `manifest_files`, `ciphertext{sha256,size}`, `wrapped_key_sha256`, `descriptor_sha256`, `archive_sha256`, `provider_confirmation[4]` (`:1434-1446`) | `span_offload.offload` only (`:1455`) | `copy_evidence` (controller gate), close, reclaim, Air `ssd-copy` and `pull`, the look's staging step | Create-once; seam I0. `P.ok.unconfirmed` is never a gate input (`:1716-1722`) |
| A11 | SSD receipt: `<ssd>/span-archives/P/ssd.ok.json`, couriered to the MBP | `joulewise.span_offload_ssd.v1`: `plan`, `descriptor_sha256`, `files`, `destination`, `verified_epoch_s` (`:1575-1583`, `:1631-1633`) | Air `ssd-copy` | MBP `reclaim` | Written inside a temp directory, then renamed |
| A12 | Retirement record: `<stage_root>/P/.retirement.json` | `source`, `descriptor_sha256`, `inventory` (`#807:joulewise/span_offload.py:1700-1730`) | `retire_original` | Its own resume | Create-once |
| A13 | **Retention holds (new):** `<stage_root>/raw-retention-holds.json` | `joulewise.raw_retention_holds.v1`: `holds[{id, match{path \| campaign_id \| plan_prefix}, reason, by, at}]` | `close_offload.py hold` only | Every retire and evict path | Atomic replace; unreadable means nothing is retired |
| A14 | Pending-transfer observation | `{clear, observed_epoch_s, scope}` (`#804:…span_offload.py:1561-1572`) | Not durable; one fresh read per arm, recorded in the arm proof | Driver | n/a |
| A15 | Arm notice: one line on the standing-notice issue | Text today (`#800:…cadence_controller.py:1843-1845`). **Add** a machine-readable tail: `plan_id`, `t0`, `close_deadline_epoch` | Driver, before the network closes | Ed; the off-host watcher | No post means no intent |

### 1.5 Where the four PRs disagree

Each row is a place where two heads, or a head and a ruling, cannot both be right. "Read" means found by reading and not executed.

| # | Disagreement | Evidence | Kind |
|---|---|---|---|
| D1 | **Three blobs of the shared backend.** #800 vendors `joulewise/span_offload.py` at blob `5c87d265` (byte-equal to #804 at `ccfe442b6`). #804's head is `de7ddd00` (the finding-8 repair). #807's head is `dab8e271` (its own finding-8 repair, streaming readback, retention, retirement). `close_offload` has two signatures: `#804:joulewise/span_offload.py:1657` and `#807:joulewise/span_offload.py:1734`. `recheck_marker` differs: `#804:…:1513-1558` and `#807:…:1538` with a span-name check at `:1555` that #804 lacks. Merging any two conflicts on one added file | Read (blob hashes compared) | Structure |
| D2 | **Marker validity has three definitions.** #804: `marker_files` (`#804:…span_offload.py:1480-1510`). #800 adds stage, source, time-order and key conditions around a call into its vendored copy (`#800:joulewise/cadence/standing.py:1244-1270`). #807 adds the span-name check inside `recheck_marker`. The source record is compared three ways: `realpath` in #800 (`standing.py:1258`), `str(path)` in #807 (`#807:joulewise/close_offload.py:185-190`), `_real()` at write in #804 (`:1254`) | Astra 1, and read | Seam A |
| D3 | **#800's marker conditions can strand a verified copy.** (a) `verified ≤ written` and `created ≤ uploaded` and `receipt ≤ created` are wall-clock comparisons across processes (`standing.py:1252`, `:1262`, `:1266`): a backward clock step during the offload makes an immutable marker fail for ever, as a HALT. (b) The gate needs the stage's `.source.json` and descriptor for every span ever closed, at every tick (`#800:scripts/cadence_controller.py:1546-1549`, `:1676-1679`); no PR promises that the stage outlives eviction | Read | Seam A |
| D4 | **Two config keys are optional in name and mandatory in effect.** `copy_stage_root` and `copy_key_second_copy_sha256` are optional (`#800:…cadence_controller.py:119`) and the template ships the second as `null` (`#800:configs/launchd/cadence-controller.config.json.template:21`). Without either, every marker is `OFFLOAD_FAILED` (`standing.py:1258-1260`, `:1268-1269`), found only after the first span has run | Read | K7 |
| D5 | **The fence has three readers and two exclusion models.** Readers: `main:scripts/launch_align_r0.py:67-86`; the arm child (`#800:…cadence_controller.py:950-987`); #807's own parser (`#807:…close_offload.py:104-119`). #804 refuses to offload whenever the fence file exists (`#804:…span_offload.py:1362-1366`; its runbook lists the fence in `forbid_paths`, `#804:docs/ops/SPAN-OFFLOAD.md:154`, `:158`). #800 holds that fence across the close (`#800:…cadence_controller.py:2322`). #807 refuses on its presence unless three argv values match (`:105-119`) and then strips the path from `forbid_paths` (`:267-272`) | Astra 2 | Seam B |
| D6 | **#807 holds the fence mutex for the whole close.** `Guard.lock()` takes `.desk-fence.lock` (`#807:…close_offload.py:133-145`) around all of `run()` (`:265-281`), up to the 3,600 s the controller allows. On main that mutex is a blocking `flock` (`main:scripts/launch_align_r0.py:59-61`) and the magistrate watchdog takes it to read the fence (`main:scripts/magistrate_watchdog.py:1956`). So the watchdog's fence read can block for the length of a close. RL-173 E leaves the watchdog untouched as the backstop (`RL:17496`) | Read | Seam B |
| D7 | **The per-arm pending-transfer read has no owner in controller mode.** Required at every arm by RL-174 D.1 (`RL:17621`), by #804 (`SPAN-OFFLOAD.md:107-117`) and by #807 (`#807:docs/ops/CLOSE-OFFLOAD.md:63-70`). #800's arm proof has no such line (`standing.py:1199-1207`); the controller reads `pending.clear` only once, from the close's output (`…cadence_controller.py:2367-2368`) | Read | Seam D |
| D8 | **#800 is not stacked on #799.** #799's head `3747167f4` was cherry-picked into #800 as `e7d7df5e3`. The desk files are byte-equal today (same blobs), but the next #799 change must be picked again by hand | Read (`merge-base --is-ancestor` fails) | Process |
| D9 | **Two ref listers of different strictness.** #799 requires exit 0, empty stderr and a terminated last line (`#799:…desk_transport.py:347-363`). The controller's `verdict_refs` and `local_refs` check the exit code only (`#800:…cadence_controller.py:533-541`), and `--history-empty` is asserted from that lax listing (`:2283`, `:2290`). The desk's own probe is the only backstop | Read; class of cold F4 | Seam C |
| D10 | **`published` is cached and then trusted.** `desk_close` skips a span whose `close.json` says `published` (`:2275`). If the local verdict ref later disappears, the controller halts `DESK_VERDICT_INVALID` (`:693-695`) and never re-runs a deterministic desk | Read; class of Astra 4 and 6 | Seam C |
| D11 | **The retention list cannot express the rule in force.** RUN_STATE 396 and RL-175 B.1 keep every dev-01 to dev-05 output raw until the lead records "interim look complete" (`main:RUN_STATE.md:1046-1047`; `RL:17741`). #807's list holds exact absolute paths (`#807:…span_offload.py:1126-1139`). A span's path contains its arm time (`#800:…cadence_controller.py:1797-1798`), so dev-05-s02's path cannot be listed before it arms | Read | Seam E |
| D12 | **Automatic rotation deletes the predecessor at the successor's close.** `after-check` retires the newest eligible older output of each kind at every Check (`#807:…close_offload.py:217-239`). So span k's raw directory goes at span k+1's close. Span k's Q1 record and hand gates are owed only before k+2, and during an Air absence the MBP's own directory is their only authorized source (RL-175 E, `RL:17874-17875`; RUN_STATE 388 fallback 6). The same applies to the F0 Part C outputs that item 396 says to re-read (`main:RUN_STATE.md:1049-1050`). #807 knows no desk debt; #800 knows no rotation | Read | Seam E |
| D13 | **#804 alone deletes raw with no list at all.** `close` ends in `shutil.rmtree(span_dir)` (`#804:…span_offload.py:1698`) and `#804:scripts/close_offload.py:14` exposes it. #807 keeps that entry as a fall-through (`#807:scripts/close_offload.py:14-16`). Merging #804 first puts an unguarded delete on main | Read | Seam E |
| D14 | **A stranded span owes a copy that no tool can make.** #800's copy-due set includes every closed controller span with an output, receipt or not (`…cadence_controller.py:1546-1547`). #804 refuses an output without `runner_receipt.json` (`#804:…span_offload.py:1395-1398`); #807 cannot check a managed output without one (`#807:…close_offload.py:77-82`, `:206-208`, `:195-196`). After a reboot mid-span the copy gate cannot clear, F0 included | Read | Seam A |
| D15 | **`P.failed` has a reader and no writer.** Read at `#800:…cadence_controller.py:1664` and `standing.py:1319-1320`. Nothing in #804 or #807 writes or removes it | Read | Simplification |
| D16 | **A provable non-launch is a HALT.** After the intent exists, a lease that expires before bootstrap is recorded `LAUNCH_REFUSED` with a HALT page (`…cadence_controller.py:1968-1991`), and the next tick finds the intent and halts again (`:1909-1911`). A slow notice post becomes a lead disposition | Read | Seam D |
| D17 | **Offload runs after a failed push, and may then retire.** `close()` calls push, desk, offload in order with no dependency (`:2175-2177`). With GitHub down, `after-check` still rotates an older output whose bundle was never pushed or judged. RL-174 D.2 puts the close after the push and the MBP desk (`RL:17636`) | Read | Seams C, E |
| D18 | **Four create-once writers.** `write_marker` with recovery (`#804:…span_offload.py:1287-1330`); `exclusive_json`, the same link-then-unlink shape with no recovery (`#800:…cadence_controller.py:238-252`); `atomic_json` (`:223-235`); `write_fence` on main. The first two were each found torn by Astra (8 and 11) and repaired separately | Astra 8, 11, and read | Seam I0 |
| D19 | **A span that never closes has no off-host deadline.** The arm notice names the plan and the arm time, not the close deadline (`:1843-1845`), so a watcher cannot alarm on silence (RL-173 C.1, `RL:17471`) | Astra 3 | Seam D |

---

## 2. Interfaces

Each seam has one home. Signatures are normative; names may change if all four PRs change together.

### I0. Durable publication (home: `joulewise/durable.py`, new, merged with the contract PR)

```python
publish_once(path: Path, data: bytes) -> None            # raises FileExistsError, VisibleNotDurable
replace(path: Path, data: bytes) -> None                  # raises VisibleNotDurable
read_published(path: Path, limit: int) -> bytes           # raises Busy, Absent, Unsafe
finish_publication(path: Path) -> None                    # publisher only, under its own lock
```
- **Pre:** the trusted parent exists and is on one filesystem. Writers serialize with recovery under the artifact's lock. The publisher invokes `finish_publication` under that lock after restart. Recovery never promotes a standalone temp because it can contain partial bytes.
- **Post:** after `publish_once` or `replace` returns, the path holds exactly `data`, fsynced, and the directory is synced. The hard link or atomic rename is the visibility commit point. Failure before it leaves the previous path intact or absent.
- **D1, failure after visibility.** A failed sync after the visibility commit point can leave the complete new bytes on disk. Both writers raise `VisibleNotDurable` with the SHA-256 hex digest in `digest` and the underlying errno. The writer cannot durably undo the namespace change. The caller must retry with the identical bytes before proceeding. `publish_once` accepts a byte-identical existing publication and re-syncs its directory. Different bytes still raise `FileExistsError`. If the retry also fails, the caller remains in HOLD. Ordinary pre-publication `ENOSPC` and `EIO` propagate.
- **Readers:** `read_published` is bounded and reads regular files only. A path still linked to a publisher temp is `Busy`, including when the filesystem resolves a case or Unicode spelling alias to the same inode. The reader does not unlink. The writer syncs the directory before removing a linked temp, then syncs the cleanup.
- **Replaces:** `write_marker` and `recover_marker_link`, `exclusive_json`, `atomic_json`, the SSD receipt and retirement-record writes. `write_fence` on main already satisfies `replace` and stays where it is.

### A. Copy marker validation (home: `joulewise/span_offload.py`; owner #804)

```python
copy_evidence(config, plan: str, *, out_path: Path, require_closed: bool = True) -> CopyEvidence
# CopyEvidence(status, code, marker_sha256, span_name, descriptor_sha256)
# status ∈ CLEAR | ABSENT | UNCONFIRMED | BUSY | INVALID
```
CLI twin, for the magistrate: `span_offload.py evidence --config C --plan P --span-dir OUT`, one JSON line, exit 0 only on CLEAR.

- **Pre:** `config` is the offload config (`load_mbp_config`). The caller holds no lock. It reads the marker and two stage control files and nothing else.
- **CLEAR means all of:** (1) `P.ok` reads through `read_published`; (2) `marker_files(record, plan, icloud=True)` passes; (3) the backend and `recipient_sha256` equal the config's; (4) `record.span_name == out_path.name`; (5) the stage's `.source.json` names `realpath(out_path)` and the stage descriptor's sha256 equals `record.descriptor_sha256`.
- **Not part of validity:** any comparison between two wall-clock stamps (D3a). `written_epoch_s > now + 300` is BUSY, not INVALID.
- **Statuses:** no `P.ok` → ABSENT. Only `P.ok.unconfirmed` → UNCONFIRMED. `Busy` from I0, or the plan lock held → BUSY. Anything else → INVALID with a fixed code.
- **Controller mapping:** ABSENT, UNCONFIRMED, BUSY → `JOURNAL_COPY` (HOLD; every arm, cede and F0 page, RL-173 A.7). INVALID → `OFFLOAD_FAILED` (HALT). The controller adds no condition of its own.
- **Accepted once.** When `copy_evidence` returns CLEAR the driver records `copy{status, marker_sha256, accepted_epoch}` in A6 and the span leaves the copy-due set for good. Later integrity is the look's staging check (RL-174 D.3, `RL:17639`). This removes D3b.
- **Copy-due set:** closed spans with an output whose A6 has no accepted copy, plus the newest hand-armed campaign close in the ledger. A span closed without a receipt is due with `require_closed=False`. Under L3, `after-check` copies it through `--require-file` naming the file that Check found.
- **Key second copy (RL-173 A.1):** the lead's attestation is one key in the offload config, `key_second_copy_attested_sha256`, which must equal `recipient_sha256`. It is checked by the preflight (seam D), not per marker.
- **Legacy one-line markers (RL-174 A.12, `RL:17560`):** `span_offload.py offload` on a legacy `P.ok` renames it to `P.ok.legacy-line` under the plan lock and writes the typed marker only after a full recheck. Until then `copy_evidence` returns INVALID with code `LEGACY_MARKER`.

### B. Fence ownership and close mode (fence home: `scripts/launch_align_r0.py` on main; close home: `joulewise/close_offload.py`; owner #807)

**Fence primitive (unchanged, restated).** `fence_lock(root)`, `read_fence(root)`, `write_fence(root, record)`. Every cluster reader imports these. The mutex is held for one read-modify-write and never across a subprocess, a network call or a sleep (K4). Contract bound: 5 s.

**Close CLI.**
```
close_offload.py after-check --config C --span-dir OUT --deadline-epoch T [--plan P] [--require-file F]...
      [--retire PLAN]...
      ( --fence-mode self
      | --fence-mode owner --fence-purpose S --fence-pid N --fence-deadline-epoch D )
close_offload.py reclaim --config C --span-dir OUT --ssd-receipt R --deadline-epoch T (same fence options)
close_offload.py hold add|remove|list ...            (seam E)
```
`--fence-mode` is required. There is no default and no inference from whether a fence file exists.

| | `self` (magistrate, by hand) | `owner` (controller-owned) |
|---|---|---|
| **Pre** | No fence record. No measurement runner (pgrep census) | Record equals exactly `(S, N, D)`; `D ≥ T`; PID `N` is alive; no runner |
| **During** | The close writes its own record `close-offload:<token>`, its PID, deadline `T + 60`, under the mutex, then releases the mutex | The close never writes or removes the fence |
| **Before each destructive step and at exit** | Re-read under the mutex: the record is still its own. Census again | Re-read under the mutex: the exact tuple, PID `N` still alive. Census again |
| **Post** | Its record is removed if still its own. A crash leaves a dead-PID record for the watchdog's stale removal | Fence unchanged |
| **Violation** | Fence present at start: exit 4 `DESK_FENCE_PRESENT`, HOLD, retried in the next gap | Mismatch, expiry or dead owner at any check: exit 4 `FENCE_CHANGED`; nothing further is deleted. Controller: HALT `ARM_INDETERMINATE` (its lease lapsed) |

- **Controller duty:** take a lease of at least `T + 300` before the spawn, pass the tuple it read back from the fence file, and do not rewrite the fence while the child runs.
- **`forbid_paths`:** the fence path is removed from the offload config and runbook. The close mode is the only fence rule.
- **Result (both commands):** the last stdout line is one JSON object: `status`, `holds_next_arm`, `retry` ∈ `now | backoff | never`, `spans[]`, `pending{clear,…}`. Exit codes are #804's table (`#804:…span_offload.py:56-66`).

| Exit | Meaning | Driver |
|---|---|---|
| 0 with `CLOSE_OK` and `pending.clear` | Copy verified, transfers clear | Then call `copy_evidence`; only CLEAR releases the gate |
| 3, 4 with `retry: now` (`BUSY`, lock, fence present) | Nothing was done | HOLD; next tick |
| 5, 8 (`unverified`, `unconfirmed`, `ICLOUD_PENDING`, `DEADLINE`) | Provider or time | HOLD; retry at 5 then 15 min; after three, HALT `OFFLOAD_FAILED` |
| 6, 1 (`integrity`, internal) | A hash or an invariant failed | HALT at once |
| 4 with `retry: never` (config, path, plan mismatch) | Operator error | HALT |

### C. Desk verdict publish and read (home: `joulewise/cadence/desk_transport.py`; owner #799)

```python
publish_verdict(repo, out_dir, *, plan_id, signing_key, ref_prefix, principal, push, remote="origin") -> str
read_verdict(repo, ref, *, allowed_signers, plan_id, principal) -> (verdict, summary | None)
list_history_refs(repo, ref_prefix, *, probe=False) -> list[str]
verdict_state(repo, ref_prefix, plan_id, *, allowed_signers, principal, remembered) -> VerdictState   # new
# VerdictState.status ∈ ABSENT | FINAL | NOT_FINAL | HOLD | INVALID | ROLLED_BACK | DISAPPEARED
```
- **Single writers:** the off-host desk writes `cadence-desk-final/P`; the driver's desk step writes `cadence-desk-mbp/P`. Nothing else writes either prefix.
- **`publish_verdict` post:** it returns the commit only after the ref's tip has been read back equal to it. Local: `update-ref` with the expected old value, exit checked, `rev-parse` (as at `#799:…desk_transport.py:305-314`). Remote: after the push, `ls-remote` must show the commit. Otherwise `TransportRefusal`; nothing is recorded as published.
- **`list_history_refs` is the only lister.** A failed, warned or truncated listing raises. The controller's `verdict_refs` and `local_refs` are deleted in its favour (D9). `--history-empty` is passed only when this function returned `[]`.
- **`verdict_state` is the only way the controller decides.** `remembered` is `{tip, verdict_sha256}` from the last accepted read. It folds in signature, subject, trailers, `verify_verdict`, summary hash and `counts_as_final`.
- **Truth is the ref (K2).** `close.json.mbp_desk.published` is advisory. Each tick, for each span at S6 without a counted verdict, the driver calls `verdict_state`:

| Status | MBP ref (local) | Off-host ref (remote) |
|---|---|---|
| ABSENT | Run the desk step (T7). HOLD meanwhile | Not final by this desk; the MBP verdict alone may count (RL-173 B, `RL:17463`) |
| FINAL, NOT_FINAL, HOLD | As the verdict says | As the verdict says; compare with the MBP verdict, a difference is HALT `DESK_DISAGREEMENT` |
| DISAPPEARED (remembered, now absent) | Re-run the deterministic desk once. Same `verdict_sha256`: continue. Different: HALT | HALT for disposition (Astra 6) |
| ROLLED_BACK, INVALID | HALT `DESK_VERDICT_INVALID` | HALT `DESK_VERDICT_INVALID` |
| Listing or fetch failed | HOLD `FETCH_FAILED` | HOLD `FETCH_FAILED` |

- **Fetch:** the verdict tracking namespace is fetched with `--prune` (as at `#800:…cadence_controller.py:528-530`), and the fresh inventory is compared with the remembered names.
- **GitHub outage:** a failed bundle push is HOLD, retried each tick. It does not block the copy (T8). It does block retirement of that span (seam E).

### D. Arm authority and lease (home: `scripts/cadence_controller.py`; owner #800)

```python
preflight(cfg) -> list[Reason]            # startup, and a line of every arm proof
arm_child(request) -> exit code           # request: plan_id, repo, python, kit, legs, batch_window, output, custody_root,
                                          #   standing{purpose,pid,deadline}, lease{wall_until, mono_until}
```
- **`preflight` (K7):** refuses to start, and refuses every arm, unless: the offload config loads; its backend is iCloud; `key_second_copy_attested_sha256 == recipient_sha256`; the stage root and marker directory exist; `offload_argv` is set and resolves; the retention-holds file reads; the signing key and both signers files read. HALT, with the missing key named. The controller config carries one key, `offload_config`, in place of `copy_marker_dir`, `copy_stage_root` and `copy_key_second_copy_sha256`. X-13 requires the startup diagnostic line `PREFLIGHT: missing offload_config` or `PREFLIGHT: key_second_copy_attested_sha256 does not match recipient_sha256` for its respective configuration fault.
- **Authority:** two full reads. The lease starts at the second and is `min(authority + 120 s, queue expiry, watcher lease, date end − 120 s)`. Everything after the second read spends it (as at `:1821-1875`).
- **Arm proof adds one line, `icloud_pending`:** a fresh `span_offload.pending_transfers(config)` with `clear is True`, read after the second authority read. Not clear, unknown or failed: HOLD (D7).
- **Arm notice:** its machine-readable tail carries `plan_id`, `t0` and `close_deadline_epoch`, posted before the network closes. No post, no intent. The off-host watcher alarms when no `desk-bundles/P` ref exists by that deadline plus a grace (D19; RL-173 C.1).
- **Intent:** published with `publish_once` before the spawn. It records the exact standing tuple and both lease deadlines.
- **Arm child, pre:** under the mutex, the fence equals the standing tuple and is unexpired. `time.time() < wall_until` and `time.monotonic() < mono_until`.
- **At transfer:** inside the launcher's locked write, the fence still equals the standing tuple (as at `:983-987`).
- **At bootstrap:** under the mutex, the fence equals the launch record; both clocks are checked again (as at `:960-973`).
- **Post, exactly one of:**

| Exit | Fact | Record | Driver |
|---|---|---|---|
| 0 | Bootstrap called; the LaunchAgent holds the fence | `arm.json` `LIVE`, `t0` = the bootstrap instant | Monitor |
| 4 | Lease expired; bootstrap **not** called; fence still the standing tuple | `arm.json` `VOID`; intent renamed `intent.void-<n>.json` | **HOLD** `LEASE_EXPIRED`; the same plan may arm again after two fresh authority reads (D16) |
| 2 | The launcher refused and cleared its own fence | `LAUNCH_REFUSED` | HALT (as today) |
| 3 | Fence absent, changed, expired or unreadable at any check | `INDETERMINATE` | HALT `ARM_INDETERMINATE`; never relaunched |
| Crash, no `arm.json` | Unknown | Restart: output exists → adopt `LIVE`; live launch fence, no output → wait; neither → `INDETERMINATE`, HALT (as at `:1994-2018`) | |

`VOID` requires proof, not inference: the child's own report says bootstrap was not reached and the fence read back under the mutex is the standing tuple. Anything less is exit 3.

### E. Retention (home: `joulewise/close_offload.py`; owner #807)

```python
may_retire(config, out_path: Path, plan: str, *, named: set[str]) -> (bool, code)
```
```
close_offload.py hold add --id ID (--path OUT | --campaign CAMPAIGN_ID | --plan-prefix PREFIX) --reason TEXT --by WHO
close_offload.py hold remove --id ID --by WHO
close_offload.py hold list
```
- **Rule (K6).** `after-check` retires nothing by its own selection. An output is retired only if **all** hold: (1) its plan is named by `--retire` in this invocation; (2) no hold matches its path, campaign or plan prefix; (3) it is not the checked output and not the newest receipt-bearing output of its kind (the GAP census, RL-174 D.3 `RL:17641`); (4) `copy_evidence` is CLEAR for it and the materialised pack verifies (RL-174 D.2 row 1, `RL:17630`).
- **Who names `--retire`.** Controller mode: the controller, for each older span that is DESK_FINAL with its bundle pushed, its Q1 record present, its gates released and its hand table not due. Magistrate mode: the item's own line, from the lead's record. F0 and Part C outputs are named only by the lead.
- **Who writes holds.** The lead or the magistrate, through `hold add`. Item 396 becomes five campaign holds (`cl-dev-01` to `cl-dev-05`), removed when the lead records "interim look complete". A campaign hold covers outputs that do not exist yet (D11).
- **A hold beats a release.** An interrupted retirement (A12 exists) whose output is now held stops: exit 4 `RETENTION_CONFLICT`, HALT for the lead. It is not resumed and not undone.
- **Failure:** the holds file is unreadable or malformed → nothing is retired, `retention_problem` is set in the result, exit stays 0 when the copy succeeded, and the driver pages informationally. A retention fault never holds an arm; it only stops deletion.
- **Eviction (`reclaim`)** keeps RL-174 D.2 rows 2 to 4: both copies verified, or keep the archive; never evict to a single copy; ≤ 60 GB mails the lead.
- **Deleted:** `raw_retention_paths` in the private config; `--keep-raw`; `--catch-up`; the rotation selection (`#807:…close_offload.py:217-239`); #804's deleting `close` verb and its script (D13). `span_offload` keeps `offload`, `pending`, `evidence`, `ssd-copy`, `pull`, `keygen`.

---

## 3. Contract test suite

### 3.1 Where it lives and how it binds

- `tests/contract/cluster.py` owns the scenario assertions. `python3 -m unittest discover -v -s tests/contract` reports the main and member cases. On step 1, A-09 passes, A-12 is an expected failure only when the generator accepts the duplicate pointer, and the other scenarios report `seam owner PR #N not merged`. The main owner must fix A-12 and remove its expected-failure marker before the final cluster gate.
- The world uses temporary directories, a local bare Git remote, a synthetic clock and PID namespace, and scoped fault injection. Keep production launch, process census, provider, GitHub and notification commands on the fixture side of the boundary. Simulated signals update fixture state. They never reach the operating system.
- The production ports are O (`joulewise.span_offload` and `scripts/span_offload.py`), C (`joulewise.close_offload` and the real `scripts/close_offload.py` subprocess), D (`joulewise.cadence.desk_transport` and `scripts/air/cadence_desk.py`), and Q (`scripts.cadence_controller`). Use the production fence helpers for synthetic fence records. Use production writers for positive markers and verdicts.
- Each member adds `tests/contract/test_cluster_<pr>.py`. Its `unittest.TestCase` inherits `ClusterScenarios` and specifies `required_ports` and `fixture_hooks`. Required missing ports fail. Any fully available scenario runs, so an import failure, missing fixture hook, missed checkpoint, or assertion failure from an installed seam fails the suite. Some scenarios use a real dependency beyond the §3.2 ports that own the assertions. For example, a close uses O and a full cycle uses D. When member files exist, the main collector keeps the main-only scenarios and the member collectors exercise the cluster.
- **D3, collection.** The main collector checks the actual unittest suites against the IDs in §3.2. The union of main and member IDs must match the contract exactly. Each installed member collector must collect the complete member scenario set. A partial or empty member file fails collection.

```python
from tests.contract.cluster import ClusterScenarios, FixtureHooks
from unittest import TestCase

class TestCluster804(ClusterScenarios, TestCase):
    required_ports = ("O",)
    fixture_hooks = FixtureHooks(configure=configure, prepare=prepare, observe=observe)
```

- `configure(world)` builds real configs and test-only keys under `world.root` and wires external command paths. `prepare(world, **inputs)` stages scenario inputs or changes an external response. `observe(world, name, **context)` projects production artifacts and recorded boundary calls. `invoke(world, name, **inputs)` adapts production interfaces that have no fixed signature yet. The Q hook `controller(world, module)` instantiates a real `module.Controller` and wires host subprocess calls through `world.member_argv(argv)`. Reuse the earlier members' fixture hooks on later branches. In the leaf, bind only fixture inputs and instrumentation. The decision, write, verification, retry and deletion paths run from the imported production tree.
- The scenario's `world.at`, `fault_at`, and `crash_at` name the checkpoint that the member exposes with `durable.checkpoint(name)`. Place the hook at the transition described by the scenario. Hooks that inspect or update the fence run after releasing the mutex. CLI subprocesses relay the point to the world and can exit abruptly using a controlled exit code. Provider helpers that outlive their worker are exercised through the synthetic PID namespace.
- **D2, supervised workers.** The test-side launch hook gives each close worker the same synthetic clock, PID namespace and fault actions as the supervisor, with a separate checkpoint channel. A worker using a native clock or signal function fails the scenario. Production launch defaults stay in place. The fixture close command supplies synthetic campaign and work roots and the exact fixture fence path.
- Record the scenario table in each PR's gate ledger. An expected failure for a missing seam is NOT-RUN evidence. Every scenario available at that merge step must pass. The final step requires zero NOT-RUN.

### 3.2 Scenarios

Format: **given**; **when**; **then**. Ports: O offload, C close, D desk, Q controller.

**Cross-PR (X)**

| ID | Ports | Given; when; then |
|---|---|---|
| X-01 | O C Q | A clean closed span. When the controller runs its close with the real `after-check` in owner mode. Then exit 0, `P.ok` exists, `copy_evidence` is CLEAR, the span leaves the copy-due set, and the next span arms |
| X-02 | O Q | A marker written by the real `offload`. When the controller's gate reads it. Then zero problems. And a hand-made marker asserting only a ciphertext length is INVALID (Astra 1, both halves) |
| X-03 | C Q | The controller holds its standing fence. When `after-check --fence-mode owner` runs with the tuple read back from the fence file. Then it does not refuse; the fence file is byte-equal before and after |
| X-04 | C | During X-03, another process calls `fence_lock` then `read_fence`. Then it returns within 5 s at every point of the close (D6) |
| X-05 | C Q | During X-03 the fence is replaced, or expires, or its owner PID dies, between two destructive steps. Then the close exits 4 `FENCE_CHANGED`, deletes nothing further, and the controller HALTs |
| X-06 | C | `--fence-mode self` with no fence. Then a `close-offload:` record exists for the whole close and is gone at exit. With a fence present at start: exit 4, nothing touched |
| X-07 | O C | No `--fence-mode`. Then a usage error. And a fence file's presence alone never changes which mode runs |
| X-08 | O C Q | Three spans k, k+1, k+2, automatic. When k+1 closes. Then k's raw directory still exists. When k is DESK_FINAL with Q1 and gates and k+2's predecessor closes with `--retire k`. Then k is retired (D12) |
| X-09 | C Q | A campaign hold on `cl-dev-05`. When a dev-05 span that did not exist at `hold add` time is named in `--retire`. Then it is not retired, exit 0, the result says why (D11) |
| X-10 | O C | `span_offload.py` has no verb that removes a raw directory; `scripts/close_offload.py` with a first argument other than its three commands is a usage error (D13) |
| X-11 | O Q | A span closed STRANDED with no receipt. Then `after-check --require-file` produces a CLEAR copy and the span leaves the due set (D14, L3) |
| X-12 | O Q | The second authority read passes; `pending` returns not clear, then unknown, then a failed command. Then no intent in each case, HOLD, and an arm once it is clear (D7) |
| X-13 | Q | Controller config lacks `offload_config`, or the attested fingerprint differs from the recipient. Then the controller refuses to start and no span arms (D4) |
| X-14 | D Q | The controller's history listing uses `list_history_refs`. A listing that exits 0 with a warning on stderr and no output. Then no `--history-empty`, HOLD (D9) |
| X-15 | D Q | `close.json` says `published`; the local MBP ref is deleted. Then the desk step runs again; the same `verdict_sha256` continues, a different one HALTs (D10) |
| X-16 | all | One blob: `joulewise/span_offload.py` exists once in the tree, and the controller imports it (D1). A repository check, not a runtime test |
| X-17 | O C Q | The whole cycle twice in a row (span, F0, span) in one `World`, real code on every port, asserting section 1.3's commit points in order. This is RL-172 (i) row 5's synthetic launch-to-close run for the cluster |
| X-18 | D | The desk lister returns the valid ref from the local fixture repository. A broken ref that makes Git warn then causes `TransportRefusal`. This runs at the desk merge gate without Q |

**Astra reproductions (A)** — one per finding, named by its number.

| ID | Ports | Given; when; then |
|---|---|---|
| A-01 | O Q | = X-02 |
| A-02 | C Q | = X-03, plus: a retry under the same ownership does not repeat a refusal |
| A-03 | Q | A span is armed and never closes. Then the arm notice already carries `close_deadline_epoch`, and the watcher fixture alarms at deadline plus grace with the plan id (not `subject -`) |
| A-04 | D Q | A Git ref lock makes `update-ref` fail. Then `publish_verdict` raises, `published` is not recorded, and the desk step is retried |
| A-05 | Q | 130 s elapse on the monotonic clock and the wall clock steps back 60 s after the server-time check. Then no bootstrap call |
| A-06 | D Q | The remote verdict ref is deleted; fetch exits 0. Then the tracking ref is pruned, the state is DISAPPEARED, HALT for disposition |
| A-07 | O C | An 8 GB-class archive (scaled) with less free space than its size. When `reclaim` runs with a valid SSD receipt. Then it succeeds without a second local copy; same-size corrupt cloud bytes are refused |
| A-08 | O | Kill between link and unlink of the marker temp. Then `copy_evidence` is BUSY; the next `offload` finishes the publication under the plan lock; then CLEAR. The reader unlinked nothing |
| A-09 | (main) | The notifier exits non-zero. Then the alarm identity stays pending and is retried. Runs against `scripts/air/night_results_watch.py`; outside the four PRs, listed so the suite owns it |
| A-10 | C | Three campaign outputs, a hold on the middle one. Then no invocation retires it, with or without `--retire`, including a resumed retirement |
| A-11 | Q | `ENOSPC` during intent publication. The path holds old content, is absent, or has the new bytes with `VisibleNotDurable` raised. No arm until the intent is durably published, including a byte-identical retry after the late error. A legacy torn intent is HALT `ARM_INDETERMINATE` |
| A-12 | (main) | Two pointer-bearing items with one number. Then generation refuses. Runs against `scripts/gen_current.py`; outside the four PRs |

**Cold-review reproductions (R9)**

| ID | Ports | Given; when; then |
|---|---|---|
| R9-F1 | O Q | A hand-armed predecessor declared in the ledger, no receipt and no marker, one unrelated old receipt on disk. Then no arm |
| R9-F2 | Q | The standing fence is absent at child entry; or removed after the child's first read; or replaced before bootstrap. Then exit 3, no bootstrap, HALT. Run against the qualification pin's real launcher |
| R9-F3 | Q | A prior receipt with `restore rc 9` then `restore rc 0`. Then HALT; duplicates of a required stage are never resolved by order |
| R9-F4 | D Q | The count-one probe succeeds and the full listing fails. Then no final verdict with `history_source: signed-records` |

**Crash and restart (K)** — kill at the named point, restart, assert.

| ID | Ports | Kill point; then |
|---|---|---|
| K-01 | Q | After the intent is published, before the spawn. Restart: no output, no launch fence → `INDETERMINATE`, HALT, no relaunch |
| K-02 | Q | After bootstrap, before `arm.json`. Restart: output exists → adopted `LIVE` |
| K-03 | Q | After the fence transfer, before bootstrap. Restart: live launch fence, no output → wait; the launcher's own timeout clears it → `INDETERMINATE` |
| K-04 | Q C | The controller is killed while `after-check` runs. Then the close sees a dead owner at its next check and stops deleting. A new controller takes the dead controller's fence; its `after-check` gets BUSY while the old worker lives, then completes |
| K-05 | O | Between the last provider readback and the marker. Restart: stage reused, readbacks re-observed, one marker |
| K-06 | C | Between the retirement record and the rename; between the rename and the end of removal. Restart: resumes, compares the inventory, completes. A hold added in between: `RETENTION_CONFLICT` |
| K-07 | D Q | After the verdict commit is created, before `update-ref`. Restart: ABSENT, the desk re-runs, one ref |
| K-08 | Q | After the bundle push succeeds, before `close.json` records it. Restart: the same tree on the remote is success; no second commit |
| K-09 | Q C O | The host reboots while a span is LIVE. Restart: fence with a dead PID; the span closes STRANDED; HALT; the copy follows X-11 |
| K-10 | Q | After the offload exits 0, before `close.json` records it. Restart: `after-check` runs again, finds a valid marker, rechecks hashes, exits 0 (RL-174, `RL:17566`) |

**Clock (T)**

| ID | Ports | Given; then |
|---|---|---|
| T-01 | Q | = A-05 |
| T-02 | O Q | The wall clock steps back 10 min between provider verification and the marker write. Then the marker is CLEAR (D3a) |
| T-03 | C Q | The wall clock steps forward past the fence deadline during a close. Then `FENCE_CHANGED`, nothing further deleted, HALT |
| T-04 | Q | The server-time read fails once, then succeeds. Then an arm. It fails for the whole lease. Then HOLD, no notice, no intent. Measured skew over 120 s: HALT |
| T-05 | Q | The wall clock steps forward across the span's date end between the authority read and bootstrap. Then no bootstrap |
| T-06 | O Q | A marker whose `written_epoch_s` is 10 min ahead of the clock. Then BUSY (HOLD), and CLEAR once the clock passes it |

**ENOSPC (E)**

| ID | Ports | Fault at; then |
|---|---|---|
| E-01 | Q | = A-11 |
| E-02 | O | `ENOSPC` during marker publication. The path holds old content, is absent, or has the new bytes with `VisibleNotDurable` raised. An unresolved write yields exit 5 and HOLD. A byte-identical retry after the late error must sync before success. After recovery, one valid marker |
| E-03 | O C | = A-07 |
| E-04 | Q | `write_fence` during a renewal. Then the old fence is intact; the controller treats a failed renewal as a lapse only when the deadline actually passes |
| E-05 | Q | `close.json` after a successful offload. = K-10 |
| E-06 | C | The retirement record. Then no rename; the raw directory is whole |
| E-07 | O | The stage build. Then no stage directory, no partial archive counted as a pack |

**iCloud (I)**

| ID | Ports | Given; then |
|---|---|---|
| I-01 | O | CloudDocs never reports the upload idle by the deadline. Exit 5 with no marker |
| I-02 | O | CloudDocs reports the upload idle, then eviction or readback cannot be verified. Exit 8 with only `P.ok.unconfirmed`. The regression with missing eviction supplies no dataless flag |
| I-03 | O C Q | A readback hash differs. Then exit 6, HALT at once |
| I-04 | O Q | `brctl status` reports pending, offline, error, or nothing. Then `pending` is not clear and the arm HOLDs |
| I-05 | C | A provider child outlives the worker. Then the supervisor kills the group, and the result is not `CLOSE_OK` until a fresh `pending` is clear |
| I-06 | O | iCloud Drive is signed out or the container is missing. Then exit 5 with a fixed code; no marker; nothing under the span is touched |
| I-07 | O C Q | After an I-02 result, every arm including F0 is held. Retries at 5 and 15 min precede HALT |

**GitHub outage (G)**

| ID | Ports | Given; then |
|---|---|---|
| G-01 | Q C O D | The push fails for a whole close interval. Then the copy still reaches CLEAR; no verdict is counted; that span is not named in any `--retire`; the push succeeds on a later tick and the desk then runs (D17) |
| G-02 | Q | The audit fetch fails. Then no arm, HOLD `FETCH_FAILED`, and the standing fence stays held |
| G-03 | Q | = T-04's first half |
| G-04 | Q | The notice post fails. Then no intent |
| G-05 | D Q | = A-06 |
| G-06 | Q | The outage starts after the intent and before bootstrap. Then the launch proceeds within its lease: no network call lies between the two |
| G-07 | Q | The Actions API is unreachable. Then the watcher line is unreadable: HOLD, retried; never treated as fresh |

**Air absent (N)**

| ID | Ports | Given; then |
|---|---|---|
| N-01 | all | No Air, no SSD, no off-host verdict, for three consecutive spans. Then every span reaches S8 and S9 on the MBP alone and the next arms. Nothing waits on a timer for the Air |
| N-02 | O C | No SSD receipt. Then the archive stays materialised; `reclaim` cannot be invoked; at ≤ 60 GB the lead is mailed and nothing is evicted |
| N-03 | C Q | A span's hand gates are open and the Air is absent. Then its raw directory exists until the gates are released (X-08) |
| N-04 | O C | The Air returns with a valid SSD receipt. Then `reclaim` evicts only after both copies verify |
| N-05 | D Q | The Air returns with an off-host verdict that differs from the MBP's. Then HALT `DESK_DISAGREEMENT` |
| N-06 | O | The offload encrypts with the pinned public key only; no private key, Air marker or SSD path is read on the MBP |

---

## 4. Convergence diagnosis

### 4.1 The findings do not decay

HIGH findings per round on #799 and #800, from the PR bodies: gate 1, 16 (Sol 11, Mythos 5). Gate 2, at least 5. Gate 3, 2. Gate 4, not stated by severity. Gate 5, 1. Gate 6, 1. Gate 7, 3. Round 9 cold review, 2. Round 10 (Astra, cluster-wide), 5. The count stopped falling at gate 3 and the kind changed: gates 1 to 4 found single-PR law errors; gates 5 to 10 find boundaries.

### 4.2 Every finding, by root cause

Sources: #799 and #800 PR bodies (gates 1 to 7 and rounds 9, 10), #804's and #807's review reports, the cold review, the Astra audit. Gate 1 to 4 findings are grouped from their disposition rows.

| RC | Root cause | Findings | Removed by |
|---|---|---|---|
| **RC1** | **A shared artifact has more than one reader or validator, and they drift** | Gate 1: Sol 1, Mythos F1 (protocols do not connect), F20. Gate 2: N11/R8 (history provenance), N6. Gate 3: Opus 2/T10 (two right verdicts disagree), Opus 3/T15 (marker not bound), T16. Gate 4: F6/3,12 (offload interface), F12 (code identity). #807 round 1: cloud-only `.ok` becomes Air proof; both authority conflicts. Round 10: Astra 1. RL-174's "one marker schema" (`RL:17566`). D1, D2, D9, D15 | **Yes.** K1; seams A and C; X-02, X-14, X-16 |
| **RC2** | **The fence means three things (mutex, host lease, "a run is live") and no mode names its owner** | Gate 1: Sol 3, Sol 15/Mythos F14, Mythos F5, F21. Gate 2: Sol R2, R7, N9, N15. Gate 3: T4, T13, T8. Gate 4: F5/5, F8. Gate 5: F2, F3. Gate 6: F2, F3. Gate 7: F4. Round 9: F2. Round 10: Astra 2. D5, D6 | **Yes** for the close and the arm child (K4; seams B and D; X-03 to X-07, R9-F2). The controller's internal renewal logic stays single-PR and is covered by K-04, T-03, E-04 |
| **RC3** | **Absence or a failed read is taken as a value** (empty, clean, zero, success) | The original Sol probe (zero rows final). Gate 1: Sol 5, 9, 10; Mythos F18. Gate 2: R5, N16. Gate 3: T1, T5. Gate 4: F2, F3. Gate 5: F4. Gate 6: F1, F4. Gate 7: F1, F2, F3. Round 9: F1, F3, F4. Round 10: Astra 4, 6, 9. #804: H1 (a listing satisfies `.ok`), L1 | **Mostly.** K8 and typed statuses at every seam (`copy_evidence`, `verdict_state`, exit classes) remove it at the boundaries. Inside the controller's law it is a discipline, tested by R9-F1, F3, F4 |
| **RC4** | **Authority is cached, or time is trusted** (one clock, order as proof) | Gate 1: Sol 4, 12; Mythos F4, F13, F19, F23. Gate 2: R3/N7, R10, N8, N10, N14. Gate 3: T2, T3/Opus 6. Gate 4: F1, F4. Gate 5: F1. Round 10: Astra 5, throughput 1. D3a, D7 | **Yes** at the seams (K5; seam D's two-clock lease and fresh `pending`; seam A drops time order). T-01 to T-06 |
| **RC5** | **Durable writes are not atomic, and restart does not reconcile cache with artifact** | Gate 1: Sol 14. Gate 2: N4, N5. Gate 4: F3 (stranded copy forgotten). #804: H2 (retry after a late source change). #807: interrupted removal. Round 10: Astra 8, 11. D10, D18 | **Yes.** I0 and K2, K3; K-01 to K-10, E-01 to E-07 |
| **RC6** | **A destructive step selects its own targets** | #807 round 1: pending upload releases the arm; plaintext archive. #804 original: additions and mixed versions certified. Round 10: Astra 10. RL-175 B.1's exclusion. D11, D12, D13, D17 | **Yes.** K6; seam E; X-08 to X-10, A-10, N-03 |
| **RC7** | **Outside failures are not designed for** (disk, provider, network, descendants) | Gate 3: T14, Opus 4/T9. Gate 4: F4/10 (retry spacing). #804: keygen directory, placeholder retry exit. #807 round 1: provider grandchild survives. Round 10: Astra 7, throughput 1. D14 | **Yes** as a test obligation: the E, I, G and N groups are now required of every PR. The contract adds exit classes so each failure has one meaning |
| **RC8** | **Each PR is tested against a stub of its neighbour; review is per PR** | Gate 1: Mythos F26 (the synthetic run was not the candidate). Round 10: Astra 1 and 2 were both invisible to green suites. `stub_controller_owned_close`. D8. Deployment found late: D4 | **Yes.** Section 3.1: real ports only, NOT-RUN is not a pass, zero NOT-RUN at the last merge; K7 |
| RC9 | Unsafe input paths and content | Gate 1: Sol 2, Mythos F24. Gate 2: N1/R1 (denied key shipped). Gate 6: F5 (kit path overwrote files). #807 round 1: link normalisation | No, and not needed: fixed inside one PR each, no recurrence since gate 6. Kept as regressions |
| RC10 | Single-PR law and accounting | Gate 1: Sol 6, 7, 8, 11, 13; Mythos F2, F3, F6 to F12, F15 to F17, F22, F25. Gate 2: R4, R6, R9, R11, N2, N3, N13, N17. Gate 3: Opus 7, 8, 9, T6, T7, T11, T12, T17. Gate 4: F7, F9, F10, F11; Opus 1, 7, 9. Gate 5: the draw-coverage LOW. Gate 7: parts of F1, F3 | No. These decayed by themselves (none HIGH after gate 4 except gate 7's accounting pair). They stay with #799 and #800's own tests |
| RC11 | A ruling was open or moved during review | Disposed-ancestor draw; unknown L002; N12; Q1 and typed-marker switch-over; T13; the key deadline; non-counting clearance. RL-173, RL-174 and RL-175 each landed mid-review. Astra 3 and 12 (main's process, not these PRs) | Partly. From now a ruling that touches a seam changes this document and the suite first; the PRs follow. The open questions themselves stay with the research lead |

RC1 to RC8 hold every HIGH of rounds 9 and 10 and every finding I add in section 1.5. RC9 to RC11 are the residue that per-PR review handles.

### 4.3 Who owns which seam

| Seam | Owner PR | Others must |
|---|---|---|
| I0 durable publication | Contract PR (main) | Import it; delete their own writers |
| A marker schema, `copy_evidence`, `pending_transfers`, plan lock, SSD receipt | **#804** | #800 and #807 call it and add no condition |
| B close modes, the close's fence use, result line and exit classes | **#807** | #800 passes the tuple and maps exits by the table |
| C verdict publish, read, list, `verdict_state`, bundle format | **#799** | #800 uses only these four functions |
| D preflight, authority, lease, arm child, arm notice, standing fence | **#800** | Nobody else writes a `cadence-controller:` fence |
| E holds file, `may_retire`, retirement, reclaim | **#807** | #800 supplies `--retire`; #804 deletes nothing |
| Fence primitive | main (`scripts/launch_align_r0.py`) | All import it; nobody re-parses the file |

A change to a function is reviewed by its seam owner, whichever PR carries the diff. In particular #807's edits to `joulewise/span_offload.py` (D1) are #804's to accept.

### 4.4 Merge order

1. **Contract PR → main.** `docs/ops/cluster_contract.md`, `tests/contract/cluster.py`, `joulewise/durable.py`. Tier 2. Existing production callers keep their current behavior.
2. **#804 → main,** rebased on 1. It owns the one blob of `joulewise/span_offload.py`. It adds `copy_evidence` and the `evidence` verb, moves to I0, drops the fence from `forbid_paths`, and **removes its deleting `close` verb** (D13). Its admission at `ccfe442b6` no longer covers its head, so it needs a delta admission in any case. Suite: O-only scenarios PASS.
3. **#807 → main,** rebased on 2, carrying **no** copy of `span_offload.py`: its backend changes (streaming readback, span-name check) are a reviewed diff on #804's file. It owns seams B and E. Suite: O and C scenarios PASS. After this step magistrate mode has the whole offload path, which is what items 388 and 395 need today.
4. **#794 → main,** then **#799 → main,** rebased on main. #799 touches only the desk and is independent of 2 and 3; it may go in parallel with them. Suite: X-18 and any other available D scenarios PASS.
5. **#800 → main, last,** rebased linearly on main after 4 (no cherry-picks; D8). It **deletes its vendored `joulewise/span_offload.py`** and its private marker law, lister and close stub. Suite: every scenario PASS, zero NOT-RUN. Then one cold gate on the merged tree, then the watched native span (RL-172 (g), `RL:17306`).

Why this order: #800 is the only consumer of every seam, so it cannot be judged until the others are fixed points. Everything before it is usable by the magistrate without it. And the offload pair is what the MBP needs while the Air is away.

**What a review round checks from now on:** the PR's diff against this contract, and the suite table. A finding that is a seam behaviour not in the contract is a contract change first. That is what makes the count fall.

---

## 5. Simplifications

Each item can go because a contract rule makes it redundant.

| # | Delete | Where | Why it is redundant |
|---|---|---|---|
| 1 | #800's vendored `joulewise/span_offload.py` (1,910 lines) | `#800:joulewise/span_offload.py` | K1; step 5 of the merge order |
| 2 | `offload_marker_problems`, `read_marker`, `read_copy_stage`, `MARKER_MAX_BYTES` | `#800:joulewise/cadence/standing.py:1244-1270`; `#800:scripts/cadence_controller.py:1661-1696`, `:126` | One call to `copy_evidence` |
| 3 | The three wall-clock order checks on the marker | `standing.py:1252`, `:1262`, `:1266` | K5; binding is by name and hash |
| 4 | The `P.failed` sidecar and its reason | `cadence_controller.py:1664`; `standing.py:1319-1320` | No writer exists (D15); the exit class carries the failure |
| 5 | The key-copy temporary exception: `KEY_SECOND_COPY_DEADLINE`, the `key_copy_exception` lease | `standing.py:70`, `:1268-1269`; `cadence_controller.py:1864-1870` | The deadline passed on 16 Nov 11:58; the preflight replaces it |
| 6 | Controller config keys `copy_marker_dir`, `copy_stage_root`, `copy_key_second_copy_sha256` | `cadence_controller.py:113-119`; template lines 19 to 21 | One `offload_config` path; the offload config is the single home |
| 7 | The marker-hash "changed" retry logic | `cadence_controller.py:2346-2349` | The tool's `retry` field and exit class say whether to retry |
| 8 | Re-validating every past span's marker at every tick | `cadence_controller.py:1546-1549` | Accepted once (seam A); the due set is bounded |
| 9 | `Git.verdict_refs` and `Git.local_refs` | `cadence_controller.py:533-541` | `list_history_refs` |
| 10 | `mbp_desk.published` as a gate | `cadence_controller.py:2275` | `verdict_state` reads the ref |
| 11 | The fence entry in `forbid_paths`, and its special case | `#804:…span_offload.py:1362-1366`; `SPAN-OFFLOAD.md:154`, `:158`; `#807:…close_offload.py:267-272` | The close mode is the fence rule. If nothing else uses `forbid_paths`, delete the key |
| 12 | #807's own fence parser and its whole-close mutex | `#807:…close_offload.py:104-119`, `:133-145` | Import main's helpers; K4 |
| 13 | Fence mode inferred from argv presence | `#807:…close_offload.py:92-99` | `--fence-mode` is explicit |
| 14 | #804's deleting `close` verb, its script, and #807's fall-through | `#804:…span_offload.py:1657-1713`; `#804:scripts/close_offload.py`; `#807:scripts/close_offload.py:14-16` | One destructive entry point, in #807 |
| 15 | Automatic rotation, `--catch-up`, `--keep-raw`, `raw_retention_paths` | `#807:…close_offload.py:217-239`, `:289-291`; `#807:…span_offload.py:1090`, `:1126-1139` | K6: retain by default, `--retire` and holds |
| 16 | `write_marker`, `recover_marker_link`, `exclusive_json`, `atomic_json` | `#804:…span_offload.py:1287-1330`; `#800:…cadence_controller.py:223-252` | I0 |
| 17 | `stub_controller_owned_close` and hand-written fence and marker fixtures used as seam evidence | `#800:scripts/cadence_controller_synthetic.py`; `#807:tests/test_close_offload.py:285` | The suite binds real ports |
| 18 | The marker contract text in the controller's design page | `#800:docs/process/cadence_queue_design.md:913-931` | A pointer to the contract; one home for the words too |
| 19 | The `LAUNCH_REFUSED` HALT for an expired lease | `cadence_controller.py:1968-1991` | `VOID` is a HOLD (seam D) |

Two more are the lead's, not the builders':

| # | Delete | Where | Why |
|---|---|---|---|
| 20 | The 30-minute wait for an Air marker, and "copy owner by Air state" | RUN_STATE 348 and 395 (A) (`main:RUN_STATE.md:1060-1064`) | With T8 the MBP always copies at the Check. The Air pulls later. RL-175 already says RL-173 A never asked for a wait (`RL:17900`) |
| 21 | The rclone backend as a production path | `#804:…span_offload.py:712` | It can only ever write `P.ok.unconfirmed` (`:1433`), which no gate accepts (RL-174 D.1). Keep the local backend for tests. Lower confidence: I did not check whether the Air's pull still uses it |

---

## 6. Adopted lead decisions

RUN_STATE item 399 records the decisions for this contract.

| # | Decision |
|---|---|
| L1 | Retain raw originals by default. The controller names retirement only after the span's debts close. |
| L2 | A failed bundle push permits copying and blocks retirement of that span. |
| L3 | Copy stranded outputs through `--require-file` when the runner receipt is absent. |
| L4 | The dev-01 through dev-05 holds permit encrypted copies and copy markers. Preserve the original directories and files until the lead records completion of the interim look. |
| L5 | A VOID with proof of no launch permits the same plan ID to re-arm on fresh authority. |
| L6 | Finish compatible Astra fixes 4, 5, 6, 7 and 11. Seams A, B, E and I0 replace the prior approaches to fixes 1, 2, 8 and 10. |
