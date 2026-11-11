# State-machine lane: inventory and plan

Fable 5.2, lane lead. Written 2026-11-11 03:20 PST on the Air. Implements section 8 of
`origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/implicit-state-machines.md`.

Refs read: `main` @ `41c7a1444`; the W1 line `align/2026-11-08-v4-r11` @ `b4a6c217f`;
`ops/2026-11-10-hostlink` @ `f3d2d7882`. No MBP contact, no custody, no results branch was opened.

## 1. What decides where an item goes

- **The W1 line is ahead of `main` on the whole arm stack.** The reliability rounds (rel-r2 to r7), the
  watchdog port and RL-37 landed there. `main` has none of it: its watchdog still has the single
  `HOLD_UNSAFE`, and its driver has no `chain_exit_nonzero`.
- **On the W1 line almost every operational file is bound.** `ARTIFACTS` is `_NAMED_ARTIFACTS` plus the whole
  executed closure, and every bound path is strict. `scripts/magistrate_watchdog.py`, `scripts/run_night.py`,
  `scripts/watchdog_status.py`, `scripts/post_window_unstrand.sh`, `scripts/align_v4_session.py`,
  `joulewise/b5/driver.py`, `joulewise/night_gate.py`, `joulewise/arm_retry.py` and
  `joulewise/align/apple/powermode.py` are all inside.
- **New modules that no bound module imports are not bound.** They can land on `main` and reach the W1 line
  when it next takes `main`, with no re-registration (RL-51's table).
- **So the lane splits in two.**
  - *Track M (`main`, no ruling needed):* new read-only or shadow-mode modules, Air-side tools, docs, CI checks.
  - *Track W (W1 line, bound files):* each item is a question for the research lead, listed in section 4.
    Nothing on track W is built into the line before its ruling.

## 2. Inventory

Status words: **done**, **partly**, **open**. "W1" means on the W1 line only; `main` does not have it.

### 2.1 Quick wins

| # | Item | Status | Evidence | Target | Bound file? | [rebind]? |
|---|---|---|---|---|---|---|
| Q1 | Results-branch watcher | open in the repo | A scratch script exists outside the repo; nothing under `scripts/` polls `night-results/*`. | `main` | No | No |
| Q2 | One outcome function | open | No `window_outcome` on either ref. | `main` | No (new module) | No |
| Q3 | Nonzero chain exit is a fault | done on W1 | `scripts/run_night.py:2309` appends `chain_exit_nonzero:<rc>`; tested in `tests/test_w1_reliability.py`. Not on `main`. | none owed | n/a | n/a |
| Q4 | Watchdog acceptance at arm | partly | RL-35 item 4 makes the dry run a native arm check (procedure). No code in the arm helper runs it. | W1 line | Yes (`scripts/align_v4_session.py`) | Yes, question W-1 |
| Q5 | Production-store preflight | partly, on W1 | `powermode.host_lock_preflight` runs at `prepare`. It covers the lock. The two `sudo -n` rules and the network-time permission are not probed. | W1 line | Yes | Yes, question W-2 |
| Q6 | Unstrand covers pre-chain refusals and restores the host | open | `scripts/post_window_unstrand.sh` still requires `night/chain.exited` and says so in its usage text. | W1 line | Yes | Yes, question W-3 |
| Q7 | Pointer rule | open | No rule in `docs/process/`. | `main`, with item 4 | No | No |
| Q8 | Stale status files | open | `WINDOW_STATUS.md` last changed 2026-08-24; the kernel still says `AUTHORITATIVE_WORK_SELECTION_STATE`; `AGENTS.md` 42-47 unchanged. | `main` | No | No. The kernel string is the orchestrator's edit. |
| Q9 | Hostlink monitor | partly, elsewhere | The watchdog now exports status to `watchdog-status/<host>` and `watchdog_status.py` has an Air-side poll with alarm reasons. `mbp_link_monitor.sh` is unmerged on `ops/2026-11-10-hostlink`; nothing writes `armed_until`. | `main` (Air side) | No | No |
| Q10 | Offload and release fixes | open | `offload_window.py` is on the W1 line only; `compare_v4_recompute.py` is on the release-tools branch only. | their own branches | `align_v4_offloads.py` is bound; `offload_window.py` to be checked | Question W-5 |
| Q11 | Honest courier name | done on W1 | `night/courier.delivery.json` is written and read by the release check (`run_night.py:1498, 1707, 1730`); RL-35 F-09. | none owed | n/a | n/a |
| Q12 | Analysis-side hygiene | partly | `R1_FIX_BRANCH` is gone from `main`. Still open: a test that the four analysis-commit notions agree; `release_b5` HEAD against the pinned commit; the second `B5-ARM-RELEASED` line (RUN_STATE lines 21 and 3151); the stale ledger pin note; `archive/pre-prune-2026-11-06` is still both a tag and a branch. | `main` | No | Block 5 is released; RL-51 reasoning applies. RUN_STATE and the ref rename are the orchestrator's. |

### 2.2 Structural items

| # | Item | Status | What exists | What is left | Target |
|---|---|---|---|---|---|
| 1 | Explicit window lifecycle | open | Nothing. | Shadow step: `WindowState`, `derive_window_state`, violated invariants. Then readers adopt it. The journal and the result-schema split come last. | Shadow step: `main`. Writers: W1 line, question W-4. |
| 2 | Watchdog dwell, split holds, voice | mostly done on W1 | Ten named holds, a 900 s dwell limit ending in `STRANDED`, a safety notice on every new reason, heartbeat and stream-growth liveness with a notice, status export with an Air poll. | A declared transition table; a tolerant fence reader; dwell limits on the states that are not holds (`ACTIVE` stale, `BACKOFF`, an open chain "without a clock limit"); a silence alarm. The Air notifier is not installed. | Air notifier and silence alarm: `main`, Air side. The rest: W1 line, question W-6. |
| 3 | Host side-effect ledger | partly, on W1 | `powermode.restore_owed`, `_restore_owed_on_exit` on terminal paths, a network-time ON restore, a dead-man restore. | One ledger file with owner and deadline; non-W1 markers; one restorer per effect. | Shadow step (a read-only `owed_effects()` view): `main`. Writers: W1 line, question W-4. |
| 4 | One head pointer | open | Nothing. | `CURRENT.json`, a check against RUN_STATE's top item, the pointer rule (Q7). | `main` |
| 5 | Finality as one field | open | `desk_failed` appears in `align_v4_session.py` as a word only. | One writer, a lead-signed release for the k+2 deadlock. | W1 line. It changes what a record says: question W-7. Not built in this lane before a ruling. |
| 6 | Chain exit contract | open | Nothing. | A declared table per chain; undeclared codes are failures. | Table and classifier: `main`. Driver adoption: W1 line, question W-4. |
| 7 | Unseal as a recorded transition | open | Nothing. | `unseal.json` and the refusal in display tools. | The release-tools branch. Research design: question W-8. |
| 8 | Fail-closed harvest for the next block | open | Nothing. | Belongs to the next block's registration, as the audit says. | Not this lane. |
| 9 | One exit-code contract | open | Nothing. | Built with item 6. | `main` |

### 2.3 Invariants (section 8.3)

All fifteen are open as assertions. Eleven can be evaluated from files alone and go into the shadow module of
item 1 as named checks. Two need live host state (network time, AC power mode) and go into the `owed_effects`
view. Two are analysis-side (analysed attempt has all three verdicts; the four commit notions) and go with Q12.

## 3. Order of work

At most three seats at once. Every seat's work gets a cold Fable review before a PR.

**Wave 1, now, all `main`, all new files:**

| Seat | Builds | Audit section |
|---|---|---|
| `sm-window-state` | `joulewise/window_state.py`: `WindowState`, `derive_window_state`, `window_outcome`, the file-level invariants. Synthetic fixtures only. | Q2, 8.2 item 1 (shadow), 8.3 |
| `sm-exit-contract` | `joulewise/exit_contract.py`: the nine existing exit vocabularies as data, one classifier, undeclared code is a failure. | 8.2 items 6 and 9 |
| `sm-current-pointer` | `docs/process/CURRENT.json`, its generator and check, the pointer rule, retire `WINDOW_STATUS.md`, align `AGENTS.md`. | 8.2 item 4, Q7, Q8 |

**Wave 2, after wave 1 is admitted, `main`:**

| Seat | Builds | Audit section |
|---|---|---|
| `sm-air-watch` | The results-branch watcher and the silence alarm on the Air, built on `window_outcome`; folds in the watchdog-status poll's alarm reasons and replaces the scratch script. Structure-only fields. | Q1, Q9, 8.2 item 2 (voice) |
| `sm-host-effects` | A read-only `owed_effects()` view over the host state directory and the night records, with the two host invariants. | 8.2 item 3 (shadow), 8.3 |
| `sm-analysis-hygiene` | The four-commit agreement test and the `release_b5` HEAD check. | Q12 |

**Wave 3, W1 line, after rulings:** Q6, Q4, Q5, the watchdog transition table and non-hold dwell limits, the
adoption of the shadow modules by the bound writers. Each is built on a side branch off the W1 line, and its PR
stays open until the ruling names it.

## 4. Questions for the research lead

One framing question, then the items. My recommendation is given with each.

**W-0. When may bound bytes on the W1 line change for this lane?** The STRICT re-registration has not been
signed: it waits on R1's slots. RL-35 placed bound-file edits before PREQUAL and the smoke for that reason.
*Recommendation:* one batch of bound-file edits from this lane lands on the W1 line before the STRICT
re-registration, limited to items that close a known stranding path and change no measured byte (W-1, W-2, W-3).
Everything else stays off the line until the series ends or the next registration. The W1 line already carries
what protects W1's data; what is left costs schedule, by RL-35's own split.

| # | Change | Files | Alters a measured byte, verdict or registration? | Recommendation |
|---|---|---|---|---|
| W-1 | Q4: the arm helper runs the installed watchdog with `--dry-run` after install and refuses the arm on any `HOLD_*` or `STRANDED` | `scripts/align_v4_session.py` | No measured byte. Adds one arm refusal. | Land before registration. It is RL-35 item 4 made mechanical. |
| W-2 | Q5: extend the prepare preflight to probe the two `sudo -n` rules and the network-time permission | `joulewise/align/apple/powermode.py` or `align_v4_session.py` | No. Adds one prepare refusal. | Land before registration. |
| W-3 | Q6: unstrand accepts a delivered `REFUSED` result with no `chain.*`, and gains a separate explicit host-restore flag | `scripts/post_window_unstrand.sh` | No. Post-window tool. | Land before registration. This is the 11-10 stranding. |
| W-4 | Bound writers adopt the shadow modules: the driver maps chain exits through the declared contract, terminal paths call one `restore_owed()`, a `window.journal.jsonl` is written | `scripts/run_night.py`, `joulewise/b5/driver.py`, `powermode.py` | The journal is a new custody file. The contract can change which fault reasons a result carries. | Not before W1. Build and prove in shadow on `main`; adopt at the next registration. |
| W-5 | Q10: offload re-queue and re-push, `_supervised` exit code | `scripts/offload_window.py`, and whether it is in the closure | No measured byte; custody handling. | Land before registration if the file is bound; otherwise plain engineering. I will check the closure and report. |
| W-6 | Watchdog: declared transition table, dwell limits on non-hold states, and a tolerant fence reader | `scripts/magistrate_watchdog.py`, `joulewise/night_gate.py` | No measured byte. The tolerant reader changes a fence decision: an unknown plan key would fence, not hold. The reliability round declined this ("no unknown key is ignored"). | Transition table and dwell limits: after W1. Tolerant reader: your call on the design. I recommend it, for fence arithmetic only, with admission still strict. |
| W-7 | Finality as one field, `desk_failed`, a lead-signed release for the k+2 deadlock | `scripts/align_v4_next_arm_packet.py`, `align_v4_series.py` | Yes: it adds a way for the series to continue past a failed desk. | Research design. You decide whether the release exists at all; I build nothing until then. |
| W-8 | `unseal.json` and outcome tools that refuse without it | release tools | It changes who may read outcomes and when. | Research design; your ruling first. |

## 5. Decisions for the orchestrator (not research design)

- **Q1 goes in the repo.** A watcher that only lives in scratch is the gap the audit named.
- **`CURRENT.json` is generated, never bumped by hand** (orchestrator, 03:40 PST). Format in section 5.1; it
  is shown to the orchestrator before anything reaches `main`. Seat `sm-current-pointer` was launched with the
  earlier manual-bump design; a round 2 converts it.
- **Q1 scratch script:** `night_results_watch.sh` in the lead session's scratchpad (zsh; baseline ref set; prints
  verdict, chain exit, fault, fault reasons). Wave 2 moves it into the repo as Python on `window_outcome`. The
  running instance is not touched until R1's chain has exited.
- **The orchestrator's edits, exact places:**
  - Kernel authority: `docs/process/state_kernel.json:4` (`"authority": "AUTHORITATIVE_WORK_SELECTION_STATE"`).
    The same word is the constant `AUTHORITY_NOTICE` at `scripts/gen_state.py:32` and is rendered into the
    generated regions, so the string, the constant, the schema and `tests/test_gen_state.py` change together.
  - `B5-ARM-RELEASED`: `RUN_STATE.md:21` (`beta gamma`) and `RUN_STATE.md:3151` (`alpha beta gamma`). No program
    reads either. Delete line 3151's copy or mark it history, and drop "because a program reads it" from item 31
    (`RUN_STATE.md:54`).
  - Archive refs: `refs/heads/archive/pre-prune-2026-11-06` and the annotated tag
    `refs/tags/archive/pre-prune-2026-11-06` both resolve to `eeea6d5cf`. Keep the tag (`docs/ARCHIVE.md`
    retrieves by that name, and a tag does not move); delete the branch:
    `git push origin :refs/heads/archive/pre-prune-2026-11-06`.

### 5.1 `CURRENT.json`: proposed format (for the orchestrator's approval)

**Source.** A small block directly under a numbered RUN_STATE item's heading line. It is visible in the
rendered file, so a phone reader sees it too. The values below are made up for illustration.

````
262. **Laptop lead (...), 2026-11-11 04:10 PST: R1 re-armed.**

```pointer
owner: magistrate
armed: align-r1-20261111T0453Z
host: mbp
t0: 2026-11-10T20:53:00-08:00
latest_end: 2026-11-11T19:03:00-08:00
wait: result_json_exists
deadline: 2026-11-11T19:33:00-08:00
on_early_or_refused: read verdict first; REFUSED means unstrand, restore network time, re-plan
next_observable: branch night-results/align-r1-20261111T0453Z carrying result.json
```
````

- `armed`, `host`, `t0`, `latest_end` are given together or all left out ("nothing armed").
- `wait` comes from a closed list a program can check: `result_json_exists`, `results_branch_exists`,
  `watchdog_status_state`, `pr_merged`, `ruling_recorded`, `none`. `chain_exited` is refused, because a window
  refused before its chain never writes it (audit section 0).
- `deadline` is required unless `wait: none`, and may not be earlier than `latest_end`.
- Times are ISO with an offset. The generator converts them to epochs and refuses anything else.

**Generated file.** `docs/process/CURRENT.json`, written by `python3 scripts/gen_state.py` and checked by
`python3 scripts/gen_state.py --check`, which CI already runs (`.github/workflows/ci.yml:103`).

```json
{"schema": "joulewise.current_pointer.v1", "pointer_item": "262", "owner": "magistrate",
 "armed": {"plan_id": "align-r1-20261111T0453Z", "host": "mbp", "t0_epoch_s": 1794372780,
           "latest_end_epoch_s": 1794452580},
 "wait": {"observable": "result_json_exists", "deadline_epoch_s": 1794454380,
          "on_early_or_refused": "read verdict first; ..."},
 "next_observable": "branch night-results/... carrying result.json"}
```

**One choice for the orchestrator.**

- *(a) Newest block wins (recommended).* `pointer_item` is the highest-numbered item that carries a block. An
  item without a block changes nothing, so an ordinary RUN_STATE commit never needs the generator and cannot
  turn CI red. Only a commit that writes or edits a block must run `gen_state.py`. The cost: a new top item
  that changes the pointer but forgets the block leaves the old pointer standing. The Air watcher covers that
  from the other side, because it alarms when a `deadline` passes.
- *(b) Top item must agree.* The file also records the top item's number, so every new item needs the
  generator run. It never goes stale silently, and it breaks CI whenever someone forgets.

`gen_state.py` and `tests/test_gen_state.py` are files Sol may not edit under the standing rules. Either the
orchestrator lifts that for this seat, or the pointer generator lives in a new `scripts/gen_current.py` that
`gen_state.py` calls through one added line, which I make myself in review.

## 6. MBP install list for the post-R1 batch

All remote (SSH after custody closes, no night label loaded). No physical step.

| Item | What is installed | When |
|---|---|---|
| Wave 1 and 2 modules | Nothing on the MBP: they are read-only and run on the Air. `window_outcome` reaches the MBP when its checkout next moves. | n/a |
| W-1, W-2, W-3 | Arrive with the W1 line checkout that gets registered. | With the W1 STRICT re-registration, before PREQUAL and the smoke |
| Air notifier for the watchdog-status poll | Air only. | Before the W1 arm (closes W-01/W-02 of the measurement audit) |

## 7. Log

Times are from `date` on the Air, PST.

- 03:20: plan written. 03:22: wave 1 launched (`sm-window-state`, `sm-exit-contract`, `sm-current-pointer`).
- 03:26: orchestrator answered section 5; section 4 went to the research lead. Section 5.1 added.
- 03:27: orchestrator approved 5.1 with option (a), the generator in a new `scripts/gen_current.py`, and one
  added field `source_item`. The duplicate archive branch was later deleted by Ed; that item is closed.
- 03:28: **RL-53 ruled** (audit branch `99f1cc46c`). W-0: one batch (W-1, W-2, W-3) may land on the W1 line
  before the STRICT re-registration, with a cut-off at the post-R1 PREQUAL. W-4 and W-6: not during the series.
  W-5: plain engineering if unbound. W-7: no release; runbook fix and a read-only investigation. W-8: the
  unseal record is approved.
- 03:31: `sm-exit-contract` finished. Cold review ADMIT (10 of 10 mutants killed). PR #722.
- 03:31: `w1-armcheck` launched (W-1 and W-2), base the W1 line, branch `ops/2026-11-11-w1-armcheck`.
- 03:33: `w1-unstrand` launched (W-3), branch `ops/2026-11-11-w1-unstrand`. `sm-current-pointer` round 1
  finished; its round 2 (generated pointer) waits for a seat slot, as does `w1-finality-tests`.

## 8. Findings owed to the research lead under RL-53

**W-5, confirmed.** `scripts/offload_window.py` is not in `ARTIFACTS` (324 paths) and not in the receipt at
`b4a6c217f`. It appears once in the dynamic trace, in `by_event.opened`, as one of 201 unbound files that a
directory sweep of `scripts/` opens; the trace's `not_bound` list is empty. It is plain engineering, under the
condition that source removal and its verification are untouched.

**W-1, one conflict in the ruling's terms, for a ruling.** On this line the quiet-dwell stamp is taken before
the installer runs (`scripts/align_v4_session.py:1225-1246`: stamp, `dwell.json`, then `pilot.install`). So a
check "after the install" cannot also be "before the dwell, never during it". The seat is briefed to run the
pre-install check before the meter probe and the stamp, and the post-install check immediately after the
installer returns, with its end time recorded on the dwell clock beside `installer_end_ns`, in one function
with one call site so it can be removed cleanly. The dry run forks `ps`/`pgrep` probes and, outside a span,
one bounded `git ls-remote`. *Recommendation:* keep the post-install check; it adds about a second next to the
installer's own `launchctl` calls, several minutes before t0, and it is the only check of the installed plist
path. The alternative is pre-install only.

**W-7 (2), late exclusion: replay recovers. No deadlock found. Read from code, not yet executed.**
`scripts/align_v4_next_arm_packet.py` on the W1 line:

- Counts are never stored. Each packet build walks the record chain and recomputes every calibration row
  (`:957-971`). A final record reads the full desk's `pilot` and `exclusions` through its successor's
  `previous_final` (`source`, `:237-242`; `pilot_view`, `:292-298`), so a member excluded late lowers that
  window's `eligible_benign` on the next build. The history carries the desk's provisional count as a ceiling
  the final count "may lower, never raise" (`:1014-1017`).
- The one refusal that names this case, "a finally excluded member of K is in the pool" (`:964-966`), compares
  against the series ledger's current `pool_members`. That list must be a subset of the previous window's D
  roster (`:847`), and member ids carry the window's pack id (`align_v4_series.py:343`), so at the arm of k+2
  it names k+1's members and cannot contain a member of k. If a ledger is written wrongly, the repair is a
  corrected `pool_members` in a new series commit (the runbook's table already says so).
- Not traced: whether any analysis-side reader takes pool membership from old `pool_members` lists and not from
  replay. Anchor members keep their kit run id across windows; I did not check whether one can appear in
  `pool_members`.

**W-7 (1), the runbook, and a second question it raises.** `bind_final` pairs each record only with its
immediate successor (`:942-943`), so runbook section 4's "until a later record carries it" is wrong. The only
record that can carry k's final sources is k+1. If k+1 was first committed without them, the repair must be a
second commit of record k+1 while it is still the chain tail. No existing test exercises that re-issue. If a
check refuses a re-issued tail record, a desk that finishes after record k+1 is committed is a real deadlock.
The tests-only seat `w1-finality-tests` will establish this and the late-exclusion path by execution, on the W1
line, touching no bound file. The runbook is corrected once that result is in, so that it states the working
repair and not a guess.
