# Opus contract-lens refuter: cold gate HARVEST-VERDICT-FINAL-01

Refuter: Claude Opus 5.5 (`claude-opus-5-5`). One foreground session, no subagents, no background tasks. Worktree `JouleWise-wt-ed17a643-cg-hv-ref` at `c382b236`. Code under review: BFG-D `origin/feat/2026-09-25-bfg-d` at `06671b69`. Registration text: PR #423 at `ad7565a7`. Phase 1 was written on 2026-09-25, at about 17:35–17:52 PDT. (Corrected during Phase 2: my first draft said 18:00–18:25, which was wrong. The poll's `date` read 17:55 PDT when the ruling appeared.)

## 0. Contamination disclosure

- **Loaded by the harness, not chosen by me:** global `~/.claude/CLAUDE.md`, project `CLAUDE.md`, and the `MEMORY.md` index (one-line pointers only). I opened no memory file. The harness also supplied the git status and five commit subjects.
  - Two index lines touch this question. One says custody roots are never offloaded to iCloud. The other is D-161 ("operator-only-adversary refusals are over-engineering; fail-closed only for physics/evidence/pre-registration"). I cite both below, and I flag them as memory-derived.
- **Not opened:** `RUN_STATE.md`, `TASK_QUEUE.md`, council logs, run reports, any memory file, and any `docs/process_traces` file outside this packet. That includes the BFG-D branch's own `bfg-d/` trace directory; I saw its file names in a `git diff --stat`.
- **Opened, read-only:**
  - The charge and both exhibits. Their sha256 values match the manifest (E0).
  - The A-R5b text at `ad7565a7`.
  - At `06671b69`: `joulewise/battery_float.py` in full; the issuer and cadence-report diffs against `c6814dd8`; the issuer's dry run, member reads, registration helpers and positional checks; the writer's battery diff; `recover_calibration_ledger.py` subcommands; `calibration_ledger.py` `abort_calibration_session` and `normalize_calibration_custody_path`; `issue_epoch_continuation.py:80-100`; the harvest section (§2.0–2.3) of the derivation-night runbook; the BFG-D battery tests in `tests/test_issue_calibration_acceptance_generation.py:2212-2345`.
- **Write-scope deviation (disclosed):**
  - I extracted `git archive 06671b69` into `/tmp/ed17a643-cg-hv-ref-probe/tree`. I did this because the live BFG-D worktree has uncommitted edits (`joulewise/arm_readiness.py`, `tests/test_arm_readiness_evidence_t0.py`), so I did not run anything there.
  - I added two scratch probe modules to that extracted copy only. The fixtures wrote temp directories under `$TMPDIR` (`m1probe-*`, `routeprobe-*`).
  - Interpreter: `/opt/homebrew/bin/python3` 3.14.7, with `PYTHONDONTWRITEBYTECODE=1`. I did not use the canonical checkout's venv, because the charge forbids touching `/Users/edr/code/JouleWise`.
  - I remove all of this scratch material at the end of Phase 1 (§6).

## 1. Executed evidence

| # | What was run | Result |
|---|---|---|
| E0 | `shasum -a 256` of the exhibits and the charter | ex-01 `10d34333…`, ex-02 `3277bd17…`, charter `099de884…`. All match the charge. |
| E1 | `python3 -m unittest tests.test_issue_calibration_acceptance_generation -k attery` (extracted tree) | `Ran 5 tests … OK`. The BFG-D issuer battery tests pass as shipped. |
| E2 | `git grep -n -i harvest 06671b69 -- joulewise scripts` | No battery-related hit. No code path writes a harvest verdict anywhere. `report_window` (`calibration_cadence_report.py:62`) and `registration_dry_run` (`issuer:217`) each **recompute** the verdict and print it to stdout. Neither persists it. The ledger has no verdict event. The head-pin commit carries only the ledger head. |
| E3 | **M1 reproduction**, `tests/probe_m1_ref.py`, real `issuer.main` with the real fixture builder. W1 has 12 clean slots. W2 has 12 clean slots, one with B = 0.9990 s. W2′ has 12 clean slots. The registry is mocked empty, as the shipped tests do. | See the table below. |
| E4 | The same fixture: the tampered slot's `instrument_evidence.json`, which the ledger authenticates | `battery_float.post = {raw_path: raw/battery_float.post.ioreg, exit_code: 0, timed_out: False, passed: True, probe_error: False}`, with the raw digest recorded. **The writer's own authenticated record says this observation was taken and passed; only the copy of its bytes is gone.** |
| E5 | Writer order (`validate_powermetrics_fiducial.py` at `06671b69`) | `:2267` and `:2495` write the raw ioreg bytes immediately after each probe. `:2626` records `battery_float` into the evidence payload later. `write_bytes` raises on failure, so if the evidence records a digest, the raw file existed when the writer finished. |
| E6 | Ledger rows in the E3 fixture | Finalized rows carry `"exact_bound_lexeme_s":"0.0300"` and so on (B in plain text) plus `classification_disposition`. **B and dispositions can be read from the ledger as soon as a slot finalizes, before any battery verdict exists.** Runbook §2.1 also has the harvester read `derivation-chain.log`, whose `slot_end … disposition=valid|non-valid` lines reveal the valid count, before §2.2's dry run. |
| E7 | **Disposition-registry route**, `tests/probe_routes_ref.py`. The same B fixture; W2's content ids are returned from `_registered_dispositions` under the fixed id `D-126-disposition-25G83-v3-2026-09-25`; the registration is `W1, W2-prime` with no battery flag. | `(0, 'candidate written (NOT ISSUED)', 'corpus n: 24')`. A clean W2 is dropped **with no battery verdict computed and no A-7 refusal**, because `foreign_owners` (`issuer:1319`) and `foreign` (`:1448`) both skip disposed content ids. |
| E8 | **Two-window tamper**: delete one raw pre file in W1 and one in W2; declare both; register `W2-prime` | `REFUSED: more than one battery-float non-pass window in this epoch: W1, W2; the epoch stops and returns to council`. Tampering can therefore also produce the *sanctioned* epoch stop. |
| E9 | `abort_calibration_session` (`calibration_ledger.py:6235-6239`) | It refuses with `CUSTODY_COMPLETE_USE_RESUME` when the next slot's custody is complete. Recovery cannot abort a slot that holds a B. `resume-finalize` finalizes only complete custody. No subcommand un-finalizes a row. |
| E10 | `normalize_calibration_custody_path` (`calibration_ledger.py:315-324`) | Custody locators are absolute. There is no working-directory route to `evidence_missing`. |
| E11 | `git grep battery_float 06671b69 -- 'configs/**' joulewise/calibration_bracketing.py` | No hit. `battery_float.py` is pinned nowhere: not in `ESTIMATOR_CODE_PATHS`, the registration, or any config. |
| E12 | `battery_float.observe` (`:125-126`) and `parse` (`:75-76`) | Wall time is stamped **before** the probe runs. Only `age > 180` fails. |
| E13 | `issue_epoch_continuation.py:86-93` | A non-pass verdict **refuses** (exit 3). It never excludes. There is no route here. |
| E14 | `tests/test_acc_25g83_rev5.py:64-73` | The registry's 11 content ids are bound to the decision-log table **by a test only**. The issuer checks only the decision-id string and the mechanism string (`issuer:1133-1156`). |

E3 detail:

| Step | Result |
|---|---|
| A. `check` dry run on W1, W2 | `0 ['W1: battery=pass', 'W2: battery=pass']` |
| A. `prepare-candidate` W1, W2 | `REFUSED: member B exceeds PLATEAU_INSET_S = 0.25 s: W2-d01`. The caller has now seen an outcome that kills issuance. |
| B. Before tampering, declare W2 excluded and register W1, W2′ | `REFUSED: … clean session declared confounded: W2` |
| Delete `W2-d06/raw/battery_float.post.ioreg` (not even the slot with the high B) | — |
| B. Dry run after tampering | `W2: battery=evidence_missing … valid=0 excluded=battery_evidence_missing` |
| B. W1, W2 with no flag | `REFUSED: … computed non-pass session omitted: W2` |
| B. Declare W2 excluded and register W1, W2′ | **`0`: candidate written, corpus n = 24.** The window whose B killed issuance is gone, and a fresh window replaces it. |

## 2. H1: Is M1 real?

**Yes. I reproduced it end to end (E3).** No harvest verdict is recorded durably anywhere (E2). The issuer recomputes the verdict from whatever bytes exist at issuance. A missing raw file becomes `evidence_missing`, and that becomes an exclusion plus a replacement (`issuer:1359-1364`). At `c6814dd8`, the same loss on a member refuses in `_read_member_evidence`. The asymmetry is new, as the lens said.

The route is wider than the lens described. Its cure (b), a durable harvest record, does **not** close all of it:

- **R1: the tamper can come before the record.** B sits in plain text in ledger rows from finalization onward, and dispositions sit in the chain log that harvest §2.1 reads first (E6). A harvest-time record fixes whatever state exists at harvest. If the file was deleted before harvest (after B was read from the ledger), the record faithfully says `evidence_missing`, and the window is excluded. Revision 5 blindness forbids that read, but only as procedure. The route is nevertheless mechanically closable (§3), so it should be closed.
- **R2: B is not the only outcome that can be selected on.** The two stops that run *at harvest*, before any B, are driven by outcomes:
  - the 150 ms cadence stop (the cadence report shows it);
  - the W1 "fewer than 6 valid of 12" futility stop (the chain log and the dry run show it).
  If W1 is futile, deleting one raw file makes W1 `evidence_missing`. Then W1′ "faces that window's stops afresh" (A-R5b Replacement), which is a second try at a stop the registration made final. The text's own justification, "decided … before any B value **or disposition** is read", is false under harvest §2.1's reading order unless the verdict is fixed before the chain log is read.
- **R3: honest custody moves have the same effect.** Relocating or offloading a night-custody root after harvest turns every window into `evidence_missing` at issuance. With two windows, that is the sanctioned "epoch stops" outcome (E8). The iCloud memory line says custody roots are never offloaded, but nothing in code enforces it.

## 3. H2: the cure

My recommendation has two layers. Layer 1 closes every timing mechanically and needs no new durable store. Layer 2 is the harvest record the text already requires. It guards against code drift and serves disclosure.

### Layer 1: provenance split. This is the operative cure, and it needs a decision-log reading, not a text change.

The writer records each observation's outcome in `instrument_evidence.json`. The ledger authenticates that file at finalization. This happens before any agent can read anything, because the writer is unattended code (E4, E5). An observation can therefore fail in one of two ways that the code can tell apart:

| Class | What the code sees | Verdict |
|---|---|---|
| **Instrument-state** (fixed at write time) | The authenticated evidence lacks the `battery_float` key or a phase. Or it records `probe_error`, a nonzero `exit_code` or `timed_out`. Or its `raw_path` is not the ruled one. Or the raw bytes exist, **match the recorded digest**, and re-parse as stale, malformed or predicate-failing. | `battery_float_evidence_missing` or `battery_float_confounded`, as the text says. Excluded, with one replacement. |
| **Custody-state** (something happened after the write) | `instrument_evidence.json` is unreadable or does not match its ledger digest. Or the authenticated evidence records a completed probe (exit 0, not timed out, digest present), and the raw file is absent or its bytes do not match that digest. | **Custody failure: issuance refuses**, as `_read_member_evidence` does for members at main. This is never an exclusion and never a replacement. The only cure is to restore bytes that authenticate, from the byte-exact preservation copy that harvest §2.1 already requires. |

Why the text admits this reading: A-R5b licenses replacement "because the verdict is decided from instrument state alone". A lost file is custody state, not instrument state. Under this split, every verdict that leads to an exclusion is a deterministic function of bytes the ledger authenticated before anyone could see B or a disposition. No deletion at any time, before or after harvest, can produce an exclusion. That closes M1, R1, R2 and R3 together, and it also removes the E8 tamper-to-stop, because both tampered windows refuse as custody failures first.

The judge must rule whether "a missing … or unauthenticated observation" in "Window verdict" may be read as "an observation the writer did not complete". If the judge rules that it may not, the text needs a one-sentence amendment before W1. I believe it may: an observation whose authenticated record exists has not gone missing when a later copy of its bytes is lost.

Proposed decision-log text (A-R5b-1, a reading):

> **A-R5b-1 (reading, 2026-09-25).** Under A-R5b "Window verdict", an observation is *missing or unauthenticated* only when the capture writer's ledger-authenticated `instrument_evidence.json` does not record it as a completed probe (key or phase absent; `probe_error`, nonzero exit, or timeout recorded; ruled `raw_path` not recorded), or when its raw bytes match the recorded digest but do not re-parse to a fresh reading. When that authenticated record shows a completed probe but the raw bytes are absent or do not match the recorded digest, or when `instrument_evidence.json` does not match its ledger row, that is a custody failure. It is not a battery verdict: every tool that computes the verdict refuses, at harvest and at issuance. It never excludes and never licenses a replacement. The only remedy is to restore bytes that authenticate. A custody-failure refusal is checked before, and takes precedence over, the one-replacement stop. The verdict computed at harvest (A-R5b-2) is final: issuance recomputes it and refuses on any disagreement, in either direction.

### Layer 2: the harvest record (text: "The harvest record … name the window, the failing slots, the raw digests and the reasons")

- **Where:** one git-tracked JSON file per window: `configs/calibration/battery_float_harvest/<session_id>.json`.
- **Which code writes it:** a new issuer subcommand `record-battery-verdict --session-id S`. Only the tool writes the file; it is never hand-authored.
  - It opens the file with create-exclusive semantics, so it refuses if the file exists.
  - It refuses unless the session is terminal and derivation-kind.
  - It records: the head-pin sequence and digest; for each finalized slot, the `attempt_id`, the `instrument_evidence.json` sha256, the pre and post raw sha256s, the slot verdict and its reasons; the window status; the sha256 of `joulewise/battery_float.py`; and the tool's own commit SHA.
- **When:** harvest's **first** act, before the chain log (§2.1) is read, before the cadence report and before the `check` dry run. It is committed in the same commit as the session's terminal head pin.
- **Authentication (at issuance):**
  - The issuer requires the file to be tracked at `HEAD`.
  - `git log --format=%H -- <path>` must show **exactly one** commit that touched it, so a deletion followed by a re-creation shows as two commits and refuses.
  - The recorded head-pin sequence must be at or below the candidate's cutoff.
  - The recorded `battery_float.py` sha256 must equal the running module's; this closes the code-drift route R5 (§5).
- **Disagreement:** if the issuer's recomputation (Layer 1) disagrees with the record in either direction (a pass that became non-pass, or the reverse), or a record is absent for a covered session, issuance **refuses**. The cadence report and the dry run do the same for Revision 5 sessions, and they print the recorded verdict only after checking that it equals the recomputed one.
- **Registration text:** no change is needed, provided the judge admits the A-R5b-1 reading (Layer 1). If the reading is not admitted, "Window verdict" needs one added sentence carrying A-R5b-1's custody clause, landed before the W1 notice cites the digest.

## 4. H3

| Item | Refuter's position | Before W1? |
|---|---|---|
| **F-1** (writer died before the post-observation, so there is no finalized row and no obligation) | **AFFIRM.** No custody means no B. `abort-session` refuses on complete custody (E9), so no operator path can turn a B-bearing slot into an unfinalized one. The selection is impossible. NIT: the harvest record should give a zero-finalized-slot session the status `no_finalized_slots` rather than `pass`, so that the record does not claim a check that never ran. | No |
| **F-2** (a future `UpdateTime` passes) | **AFFIRM the current behaviour; reject the seat's `0 ≤ age` proposal.** The text says "no more than 180 s **before**". A future stamp is a literal pass, so bounding it would exclude windows by a rule the registration lacks. Worse, wall time is stamped *before* the probe runs (E12), so a gauge update during the up-to-10 s probe gives a legitimately negative age, and `0 ≤ age` would falsely fail honest readings. If a bound is ever wanted, it needs a text amendment, and its form is `age ≥ −PROBE_TIMEOUT_S`. The harvest record should carry `update_age_s`, so any negative age is disclosed. | No change. Any predicate change must land before W1's harvest, or R5 applies. |
| **F-6** (the issuer enforces "at most one replacement") | **AFFIRM, with an ordering obligation.** Custody failures and harvest-record disagreements must refuse **before** the `len(computed_confounded) > 1` check (`issuer:1359`). Otherwise tampering with two windows yields the sanctioned "epoch stops and returns to council" (E8), which is a B-driven reset. | Before any issuance |
| **N1** (a failing window with zero valid rows escapes the stop) | **RULE A CHANGE.** The computed set must be every terminal derivation-kind session that has any finalized row carrying the target epoch, whatever its disposition and whether or not the caller names it, instead of `session_ids ∪ owners of valid foreign rows` (`issuer:1319`). Every such session must also have a harvest record. | The recording tool before W1's harvest; the issuer change before any issuance |

## 5. Further routes found

| ID | Tier | Route | Cure |
|---|---|---|---|
| R1 | MATERIAL | A tamper before harvest, after B or dispositions are read from the ledger or chain log (E6). A harvest record alone does not close it. | Layer 1 |
| R2 | MATERIAL | Evading the futility or cadence stop at harvest by flipping W1 to `evidence_missing` | Layer 1, plus the record as harvest's first act |
| R3 | NIT | A custody relocation or offload flips every window | Layer 1 turns it into a refusal. The harvest procedure should forbid moving the custody root of an unissued epoch. |
| R4 | MATERIAL (pre-existing; not introduced by A-R5b) | **Disposition-registry route (E7).** Appending W2's content ids under the fixed decision id silently drops a clean window. The route computes no battery verdict and triggers no A-7 refusal, and only a CI test binds the registry to the decision log (E14). | The issuer pins the registry: its exact 11-id set, or the file's sha256, as a constant beside `DISPOSITION_DECISION_ID`. Any other content refuses. One line plus a defect-shaped test. Before any issuance. |
| R5 | MATERIAL | **Code drift.** `battery_float.py` is unpinned (E11). A reviewed predicate edit after harvest, such as F-2's proposal, changes the verdicts computed at issuance. | The record carries the module's sha256, and the issuer refuses on mismatch (Layer 2). |
| R6 | NIT | `report_window` recomputes and silently labels a window `diagnostic_only` | It reads the record and refuses on disagreement (Layer 2) |
| — | Checked, no finding | Re-preparing candidates: `prepare-candidate` is deterministic in the ledger and its arguments, and every argument is constrained except the registry (R4). Recovery (E9). Working directory (E10). Continuation (E13). Naming extra or fewer sessions: a clean unnamed session triggers A-7, a clean session declared confounded refuses, and naming out of ledger order refuses (`issuer:1389-1393`). | — |

I did not examine `recover_calibration_ledger.py abandon-tail` beyond its help text ("authenticate residue after the maximal valid chain"). I believe it acts only on a torn tail, not on finalized rows, but that is unverified.

## 6. H4: implementation obligations for BFG-D

1. **`joulewise/battery_float.py` `validate_window`.** Split the `except` arms into instrument-state and custody-state, as in the Layer 1 table. Custody-state raises a new `CustodyFailure` or returns the status `custody_failure`, which is never a battery verdict.
   - Test: a probe-completed raw file deleted gives `custody_failure`.
   - Test: a probe-completed raw file with one byte flipped gives `custody_failure`.
   - Test: a recorded `probe_error` gives `evidence_missing`.
   - Test: raw bytes that match the digest but are stale give `evidence_missing`.
2. **`scripts/issue_calibration_acceptance_generation.py` `_prepare_candidate`.**
   - (a) Any `custody_failure` refuses, before the set comparison and before the `> 1` check at `:1359`.
   - (b) The computed set is every terminal derivation-kind session with any finalized target-epoch row (N1).
   - (c) Each computed session must have an authenticated harvest record (Layer 2), and the record's verdict must equal the recomputation; otherwise refuse.
   - (d) The registry is pinned (R4).
   - Tests at `issuer.main`:
     - (i) The E3 sequence, a clean pass followed by deleting a non-B slot's raw file, must REFUSE and must not issue with W2′.
     - (ii) The E8 double tamper refuses as custody, not as "epoch stops".
     - (iii) A zero-valid failing session that the caller omits is still counted.
     - (iv) The E7 registry append refuses.
     - (v) A recorded pass that recomputes as non-pass refuses, and so does the reverse.
     - (vi) A record touched by two commits refuses.
     - (vii) A mismatched `battery_float.py` sha256 refuses.
3. **New subcommand `record-battery-verdict`** (Layer 2). It is create-exclusive, refuses on a non-terminal or non-derivation session, and writes the fields listed in Layer 2.
   - Test: a second invocation refuses.
   - Test: its output equals `validate_window` field for field.
4. **`registration_dry_run` (`issuer:217`) and `report_window` (`calibration_cadence_report.py:62`).** For Revision 5 sessions, each refuses without a committed record, or on a disagreement with it, or on a custody failure.
   - Test: dry run and cadence report on a session with no record, and on a tampered one.
5. **Runbook, the Revision 5 harvest.** `record-battery-verdict` plus the pin commit is step 1, before §2.1's reads, the cadence report and `check`. Custody roots of an unissued epoch are never moved. Restoring from the byte-exact preservation copy is the only response to a custody refusal.
6. **Decision log:** A-R5b-1 (§3), in the judge's final wording, plus A-R5b-2 recording where the harvest record lives and how it is authenticated.
7. **Timing.**
   - Items 1, 3, 5 and 6 must be merged before W1's harvest. A W1 harvested without them has no authenticable record.
   - Item 2's refusal tests must be merged before any issuance.
   - The F-2 predicate stays as it is.

## 7. Plain summary for Ed

- The hole is real. I showed it end to end: after seeing a result it disliked, a caller deleted one small battery file, and the tool then dropped that window and accepted a fresh one.
- The fix is to treat a lost file as lost evidence, which stops issuance until the file is restored from the backup. Only a probe that genuinely failed when the measurement was taken can exclude a window.
- A durable harvest record is still written first thing at each harvest. It guards against later code changes and gives the disclosure the text requires.
- I also found a second, older route: adding a window's rows to the "disposed" list silently drops it. The fix is a one-line pin in the tool.
- None of this changes the registered text, provided the judge accepts the reading in §3. W1 must not be harvested until the recording tool and the reading have landed.

## Phase 1 cleanup

The `/tmp/ed17a643-cg-hv-ref-probe` tree and the `$TMPDIR` `m1probe-*` and `routeprobe-*` directories were removed after this section was written (the listing and removal are shown in the session transcript).

---

# Phase 2: refutation of the judge's ruling

The ruling appeared at `/Users/edr/code/JouleWise-wt-ed17a643-cg-hv/…/20-coldgate-fable-harvest-final-ruling.md` on poll iteration 8, at about 17:54 PDT. Its size was unchanged across a 45 s wait (32165 bytes). Its sha256 is `3f3e9c0f7745884ac30c71682c4d97676f0769ea67d8fa21e7380650d298bb2f`. I read it in full once. Section references like "§4.2" are to the ruling; "E3" and "R1" refer to my Phase 1 above.

**New executed evidence for Phase 2:**

- **P2-E1.** A scratch git repo at `/tmp/ed17a643-cg-hv-ref-git` (removed afterwards; the final `ls` shows it absent). I made three ordinary commits, none rewriting history:
  1. commit `W2.json` with `status: pass`;
  2. `git rm` it;
  3. commit a new `W2.json` with `status: battery_float_evidence_missing`.
- **Result:** `cmp <(git show HEAD:$F) $F` gives **PASS**, and `git log --format=%H -- $F | wc -l` gives **3**. The ruling's §4.2 check 1 (working-tree bytes equal the `HEAD` blob) accepts a re-recorded verdict, while a path-history check would see three commits.

## Item-by-item

| Ruling item | Refuter verdict | Evidence and reasoning |
|---|---|---|
| **H1 AFFIRM, MATERIAL** (§3) | **AGREE** | This is independent of my E3. Two paths differ (the judge deleted `W2-d03`; I deleted `W2-d06`, the slot without the high B), and they reach the same exit-0 exclusion. The judge's point that the raw ioreg files sit outside `manifest.json.artifacts`, so `_read_member_evidence` never sees their loss, is correct and sharper than my Phase 1 wording. |
| **§4.1 home: committed per-window file, written by `battery-verdict`** | **AGREE** | Same conclusion as my Layer 2, and the rejection of a new ledger receipt kind is well argued. The difference in path name (`battery_float_verdicts/` versus my `battery_float_harvest/`) is immaterial. |
| **§4.2 authentication: check 1 "working-tree bytes equal `git show HEAD:`"** | **BLOCKER to the ruling as written (M1 stays open)** | P2-E1. An operator who has seen B deletes one raw file, `git rm`s the committed record, re-runs `battery-verdict` (which now writes `evidence_missing`, and its create-exclusive check passes because the file is gone), and commits. That is ordinary git: no history rewrite, no force-push. All three §4.2 checks pass: the bytes equal HEAD, the identity fields match, and the slot set and `instrument_evidence_sha256` values are unchanged, because the evidence file was never touched. §4.4's recomputation agrees with the new record, so the issuer excludes W2 and accepts W2′. That is M1 exactly. The §4.4 "Residual" paragraph says only local history rewriting remains; that is not so. **Cure:** add a check 4 to `load_committed_verdict`: `git log --format=%H -- <path>` from HEAD lists **exactly one** commit, and that commit **adds** the file (`--diff-filter=A`). Any other history makes it "no record", and issuance refuses. Add test 7(h): a record removed and re-added, or modified, in a later commit refuses. Better still, adopt Layer 1 (next row), which makes the re-recorded verdict unobtainable in the first place. |
| **§4.3 order; "the file may be regenerated before it is committed … which is visible"** | **MATERIAL** | Two gaps. (a) "Visible" is not true: a file that was never committed leaves no trace in git or the ledger. (b) The record is only as early as step (iii), but B is plain text in ledger rows from finalization on, and dispositions are in the chain log (my E6). The judge's own sentence "the record is written before any B value is read" is procedural. A raw file deleted before step (iii), after reading B or a futile valid count, is faithfully recorded as `evidence_missing` and excluded (my R1, R2). **Cure:** the custody clause of my Phase 1 Layer 1, applied inside `battery-verdict` and `compare_verdict`. Suppose the ledger-authenticated `instrument_evidence.json` records a completed probe (exit 0, not timed out, digest present), and the raw file is absent or its bytes do not match that digest. Then that is custody state: `battery-verdict` **refuses to write a record**, and the issuer refuses. Only write-time failures produce `evidence_missing`. My E4 and E5 show the distinction is mechanically available: the writer writes raw bytes before recording their digest (`validate_powermetrics_fiducial.py:2267, :2495, :2626`). This closes the pre-record window and the regenerate-before-commit window together. |
| **§4.4 disagreement means refusal, never exclusion; restore is the only cure; the refusal is not counted toward the replacement** | **AGREE** | This matches my Phase 1. The placement "before the exact-set check at `:1337`" also puts it before the `> 1` bound at `:1357`, so my E8 two-window tamper becomes a custody refusal, not the sanctioned epoch stop. The ordering obligation I raised under F-6 is satisfied. |
| **§4.4 residual and obligation 10 (external anchor = the *next arm notice*)** | **MATERIAL** | The last window of an epoch, W2 (or W3), has no next arm notice before issuance, so its record is never anchored outside the machine before B is read. Obligation 10 therefore protects exactly the windows the M1 scenario does not target. **Cure:** check 4 above is the mechanical anchor. If an external anchor is still wanted, send it at harvest (the harvest handback or notice carries `<session_id>: battery=<status> verdict_sha256=…` as soon as the pin commit lands), not at the next arm. |
| **§4.5 decision-log text A-R5b-1** | **MATERIAL: amend before recording** | Add two sentences. (i) "A record is authentic only if exactly one commit, the one that added it, has touched its path; any later modification, deletion or re-addition makes it no record." (ii) "An observation whose ledger-authenticated evidence records a completed probe but whose raw bytes are absent or do not match the recorded digest is a custody failure at harvest as at issuance; no record is written for that window and issuance refuses; it is never `battery_float_evidence_missing`." Everything else in the text is agreed. |
| **§4.6 no registration text change** | **AGREE, with a condition** | This holds provided sentence (ii) is admitted as a reading of "missing … or unauthenticated". I argued in Phase 1 §3 that it is admissible, on the text's own ground: "decided from instrument state alone"; a lost copy is custody state, not instrument state. If the judge rules otherwise, the choice is between a one-sentence text amendment before the W1 notice pins the digest, and accepting R1 and R2 as procedural residue. I recommend the amendment over the residue. |
| **§5.1 F-1 AFFIRM** | **AGREE** | Corroborating evidence the ruling does not cite: `abort_calibration_session` refuses with `CUSTODY_COMPLETE_USE_RESUME` when the next slot's custody is complete (`calibration_ledger.py:6235-6239`, my E9). No recovery path can turn a B-bearing slot into an unfinalized one. |
| **§5.2 F-2 AFFIRM for W1; `\|age\| ≤ 180` in BFG-S with a text change** | **AGREE** + NIT | The judge's future form `\|age\| ≤ 180` is correct. The seat's form `0 ≤ age` must never be adopted, because wall time is stamped before the probe runs (`battery_float.py:125-126`, my E12), so honest readings can have negative ages of up to about 10 s. NIT on timing: if BFG-S changes the predicate after an epoch's harvest and before its issuance, §4.4's recomputation disagrees and issuance refuses. That is the safe direction, but it would strand an epoch. Sequence BFG-S's predicate change after the Revision 5 epoch issues, or have `compare_verdict` evaluate under the recorded `tool_commit`'s `battery_float.py`. |
| **§5.3 F-6 AFFIRM** | **AGREE** | See the §4.4 row for the ordering. |
| **§5.4 N1 REJECT, MATERIAL; the lens's cure is too wide** | **AGREE** on the tier and on narrowing. **I withdraw my Phase 1 H3 N1 wording**, which repeated the lens's over-wide set. The judge's point about the D-126 sessions is correct, and I missed it. | |
| **§5.4 exemption (i): "a session owning a D-126 registry-disposed row"** | **MATERIAL** | The judge justifies it as unmanufacturable because "the decision id and mechanism strings are fixed in code and the file is tracked". Being tracked is not being pinned. My E7 appended W2's content ids under the fixed id, and `_registered_dispositions` accepted them. Only a CI test binds the registry to the decision log's 11 ids (my E14). With exemption (i), appending **one** row for a window removes that whole session from S. A confounded zero-valid window can then be hidden again, which is N1 regressing. The pre-existing E7 route, which silently drops a clean window with a B, stays open regardless. **Cure (one line):** the issuer pins the registry to its exact 11-content-id set (or the file's sha256) as a constant beside `DISPOSITION_DECISION_ID`, and any other content refuses. Key exemption (i) to that pinned set's owning sessions. Add test 7(i): an appended registry row refuses. |
| **§5.4 exemption (ii): pre-A-R5b sessions lacking the `battery_float` key with intact custody** | **AGREE** | The writer writes the key in every mode at `06671b69` (`:2626`; seat F-7). Removing the key breaks the ledger digest. It cannot be manufactured. |
| **§6 obligations 1–11** | **AGREE, with additions** | Add: 1a. `validate_window`, `battery-verdict` and `compare_verdict` implement the custody clause (§4.3 row). 1b. `load_committed_verdict` check 4 (single-commit history). 3a. The registry pin (§5.4 (i) row). Add tests 7(h), a re-recorded record refuses; 7(i), a registry append refuses; 7(j), a raw file deleted **before** `battery-verdict` makes `battery-verdict` refuse with a custody failure, writing no record, and makes `prepare-candidate` refuse. Change obligation 10 to "at harvest" (§4.4 residual row). |
| **§6 plain summary for Ed** | **AGREE, with one change** | Line 2 should add "and it cannot be replaced once committed". Line 3 should add "the same holds if a file goes missing before harvest". |
| **§7 packet hygiene; §1 charter-digest limitation** | **AGREE** | — |
| **Judge's disclosure: read dated "Executed" night-status lines via grep** | **AGREE**, no effect | No conclusion of the ruling depends on them. I checked each load-bearing claim against code. |

## Refuter's bottom line

- **One BLOCKER against the ruling as written.** §4.2's HEAD-only authentication lets an ordinary re-commit re-record a verdict after B is seen (P2-E1), which reopens M1. The cure is small: a single-commit history check.
- **Four MATERIAL items:**
  - the pre-record and regenerate-before-commit window (§4.3), cured by the custody clause;
  - the last window has no external anchor (obligation 10);
  - the A-R5b-1 text needs the two sentences above;
  - exemption (i) rests on an unpinned registry, cured by a one-line pin.
- **Everything else is AGREED:** H1; the home of the record; refusal on disagreement; no text change, conditional on the reading; F-1; F-2; F-6; N1's tier and narrowing.
- **Cleanup:** all scratch material is removed. The only file written in this worktree is this one.
