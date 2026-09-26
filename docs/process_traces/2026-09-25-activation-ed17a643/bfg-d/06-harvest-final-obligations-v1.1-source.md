# Cold gate HARVEST-VERDICT-FINAL-01-ADD: addendum ruling (Fable 5.1)

Judge: Claude Fable 5.1 (`claude-fable-5-1`), one non-interactive foreground session, no subagents, no background tasks, no watchers. Session 2026-09-25, about 18:05–18:35 PDT. Worktree `JouleWise-wt-ed17a643-cg-hv-add` at `0fbce962`. Ruled code: `origin/feat/2026-09-25-bfg-d` at `ab431280` (the only change after the ruling's `06671b69` is `joulewise/arm_readiness.py` and its test, A2 below). Ruled text: PR #423 at `ad7565a7`.

**Verdicts.** Y1: P2-E1 BLOCKER AFFIRM (executed, A3). MATERIAL (a) custody clause AFFIRM, and the clause is an admissible reading of A-R5b "Window verdict" without a text change, with its exact form AMENDED in §3.2. MATERIAL (b) last-window anchor AFFIRM; cure is anchoring at harvest. MATERIAL (c) two sentences AFFIRM in substance, wording AMENDED and issued final in §4.8. MATERIAL (d) unpinned registry AFFIRM (executed, A4). R4 AFFIRM (pre-existing, MATERIAL, lands in BFG-D). R5 AMEND: the record carries the module digest; issuance refuses only on verdict disagreement, never on module drift alone. Y2: obligations v1.1 issued in §4; it supersedes the ruling's §4.2, §4.4 residual, §4.5 and §6.

## 0. Contamination disclosure

- **Loaded by the harness, not by choice:** the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (one-line pointers; I opened no memory file). Three index lines touch the subject matter: one on the threat model ("operator-only-adversary refusals are over-engineering; fail-closed only for physics/evidence/pre-registration"), one on sensible gates, one on the orchestration goal. I reason from code and the registration text below and cite none of them as authority. The harness also supplied the git status and five commit subjects.
- **Opened, read-only, inside the charge's read set:** the packet (this charge, `../00-charge.md`, the ruling, the refuter); `docs/process/coldgate_charter.md`; the BATTERY-FLOAT-01 addendum ruling `../../10-coldgate-packet-bfg/30-addendum/21-coldgate-fable-bfg-addendum-ruling.md` §5 (sha256 `1047af22…3add`); the registration's last section and the decision log's A-R5a-1/A-R5b headings at `ad7565a7`; at `ab431280`: `joulewise/battery_float.py` in full, targeted ranges of `scripts/issue_calibration_acceptance_generation.py`, `scripts/calibration_cadence_report.py`, `scripts/issue_epoch_continuation.py`, `scripts/validate_powermetrics_fiducial.py`, `joulewise/calibration_ledger.py`, `configs/calibration/observation_dispositions.json`, `tests/fixtures/epoch_bootstrap/build.py`, `tests/test_acc_25g83_rev5.py`, `tests/test_battery_float.py`, `tests/test_issue_calibration_acceptance_generation.py`; `docs/phase_2/derivation_night_runbook.md` §2.0–§2.3 (procedure text; the harvest section contains no night status).
- **Contamination to disclose:** none beyond the index lines above. I did not grep outside `joulewise`, `scripts`, `tests`, `configs` and the runbook's §2 range; I did not open `docs/process/NIGHT_HANDBACK.md` (obligation 13 names it without reading it).
- **Not opened:** `RUN_STATE.md`, `TASK_QUEUE.md`, any council log, run report, memory file, or `docs/process_traces` file outside this packet other than the BFG addendum named above.
- **Write-scope deviation (disclosed):** a detached worktree `/tmp/cg-hv-add-bfgd` at `ab431280`, a scratch git repository `/tmp/cg-hv-add-p2e1` (removed within the same command), and a scratch directory `/tmp/cg-hv-add-repro/` holding one probe script whose fixture ledgers went to `tempfile.mkdtemp` under `/var/folders`. Interpreter: Homebrew `python3` 3.14.7 with `PYTHONDONTWRITEBYTECODE=1`. Nothing under `/Users/edr/code/JouleWise`, `/Users/edr/night-custody` or `~/Library/LaunchAgents` was touched; no `sudo`, `launchctl`, `powermetrics`, installer or inference ran. `git status --porcelain` in this worktree was empty before this file was written. The worktree and scratch directory are removed after this file is written (§7).

## 1. Verification before the merits

| Check | Expected | Observed | Method |
|---|---|---|---|
| Charter digest | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` (supplied in this charge; no value reached me independently of the packet) | identical | `shasum -a 256 docs/process/coldgate_charter.md` at `0fbce962` |
| `20-…ruling.md` | `3f3e9c0f…8b2f` | identical | `shasum -a 256` |
| `21-opus-contract-refuter.md` | `633a84ec…d56e2e` | identical | `shasum -a 256` |
| `00-charge.md` | `d0cbd53e…d4ea5` | identical | `shasum -a 256` |
| Branch tip | `ab431280` | `origin/feat/2026-09-25-bfg-d` = `ab431280ba91…`, type `commit`; merge-base with `origin/main` = `c6814dd8` | `git rev-parse`, `git cat-file -t`, `git merge-base` |

As in the ruling, the charter's expected digest arrived only through the charge. Recorded as the same limitation; I proceed on the charge's bytes.

## 2. Executed evidence

| # | What | Result |
|---|---|---|
| A1 | `python3 -m unittest tests.test_battery_float tests.test_issue_calibration_acceptance_generation.BatteryFloatRevisionFiveTests` at `ab431280` | 17 tests, OK, 14.8 s |
| A2 | `git diff --stat 06671b69 ab431280` | only `joulewise/arm_readiness.py` (+3/−1) and `tests/test_arm_readiness_evidence_t0.py`; nothing this packet rules is changed |
| A3 | **P2-E1 reproduction** in a scratch git repository: commit `W2.json` (`status: pass`); `git rm`; commit a new `W2.json` (`status: battery_float_evidence_missing`). Three ordinary commits, no history rewrite. | `cmp <(git show HEAD:$F) $F` → PASS (ruling §4.2 check 1 accepts it). `git log --no-renames --format=%H -- $F` → **3** commits; with `--diff-filter=A` → **2**. Controls: an honest single add → 1 and 1; an in-place modification committed on top → 2 and 1. The pair "exactly one touching commit, and it is the adding commit" separates all three. |
| A4 | **R4 reproduction**, `/tmp/cg-hv-add-repro/r4_probe.py`, production `issuer.main` with the seat's fixture builder; ledger holds W1, W2, W2-prime, all twelve slots clean. | `prepare-candidate W1 W2` with registry `{}` → exit 3, A-7 on W2-prime (honest). `prepare-candidate W1 W2-prime`, registry `{}` → exit 3, A-7 on W2 (honest). `prepare-candidate W1 W2-prime` with W2's twelve content ids returned by `_registered_dispositions` under `DISPOSITION_DECISION_ID` → **exit 0, corpus n = 24**. The real `_registered_dispositions` on a copy of the tracked registry plus two appended rows carrying the fixed decision id and mechanism string → **13 rows accepted, no refusal**. |
| A5 | Custody state in the same fixture: the authenticated `instrument_evidence.json` of `W2-d03`, key `battery_float.post` | `{raw_path: raw/battery_float.post.ioreg, exit_code: 0, timed_out: False, probe_error: False, passed: True}` with a 64-hex `raw_stdout_sha256`. The ledger row's `artifact_sha256` keys: `events.jsonl`, `instrument_evidence.json`, `manifest.json`, `raw/powermetrics.plist` (the battery raw files are not among them). After deleting the post raw file: `validate_window(W2)` = `battery_float_evidence_missing`; `_read_member_evidence(W2-d03)` raises nothing. |
| A6 | Writer order at `ab431280` | `observe_battery("pre")` then `write_bytes(battery_pre_raw)` at `validate_powermetrics_fiducial.py:2266-2267`; post at `:2494-2495`; `evidence_payload["battery_float"] = {...}` at `:2626`. `write_bytes` is unconditional, so a raw file exists (possibly empty) for every recorded phase, and `observe` records `raw_stdout_sha256` of exactly those bytes (`battery_float.py`, `observe`, `raw_stdout_sha256`). |
| A7 | B before harvest | The fixture ledger's finalized rows carry `"exact_bound_lexeme_s":"0.0300"` … in plain text (`grep` on `runs/calibration_observation_ledger.jsonl`). Runbook §2.1 lists `derivation-chain.log` (slot dispositions) and "the night's own ledger rows" among the harvest reads, before §2.2's dry run. The refuter's E6 holds. |
| A8 | Registry pin inputs | `configs/calibration/observation_dispositions.json` at `ab431280` and at `origin/main`: sha256 `ba1ba3fc596c9ef7f4014131e5cbc2012559f72bab41cafb89e004056790a63c`, 11 rows. The only reader is `issue_calibration_acceptance_generation.py` (`grep -rl` over `joulewise scripts`). `tests/test_acc_25g83_rev5.py:59-73` binds the 11 ids to the decision-log table by test only; the issuer checks the decision-id and mechanism strings only (`:1149,1151`). |
| A9 | Helper location | `ingest_git_authentication_input` is defined in `joulewise/authentication_io.py:626` and imported by `calibration_ledger.py:51`; `_committed_pin_bytes` (`calibration_ledger.py:1278-1300`) is the `git show HEAD:<relative>` pattern the ruling's check 1 copies. The ruling's obligation 1 named the wrong module; corrected in §4.10 item 1. |
| A10 | Existing tests that assert `evidence_missing` on tampered bytes | `tests/test_battery_float.py:198-203` (`write_bytes(b"tampered")` on the pre raw) and `tests/test_issue_calibration_acceptance_generation.py:2348-2356` (`+ b"tampered"` on the pre raw). Both become custody failures under §4.1 and must be re-asserted (§4.10 item 1 tests). The `post=None` case at `:200` (phase absent from the evidence) stays `evidence_missing`. |

## 3. Y1 — Each finding, verified and ruled

### 3.1 P2-E1: HEAD-only authentication accepts a re-recorded verdict. AFFIRM. BLOCKER against the ruling as written.

A3 executes the refuter's route. The ruling's §4.2 check 1 (working-tree bytes equal `git show HEAD:`), check 2 (identity fields) and check 3 (slot set and `instrument_evidence_sha256`) all pass on the re-recorded file, because the evidence file was never touched and the new record was produced by the tool. The §4.4 residual ("an operator who also rewrites Git history") was wrong: `git rm` plus a fresh commit is ordinary history. M1 stayed open under the ruling.

Two cures, both issued, in this order of importance:

1. The custody clause (§3.2) makes the re-recorded verdict unobtainable: after a raw file whose digest the ledger chain vouches for is deleted, `battery-verdict` refuses to write anything, so there is no second record to commit.
2. Check 4 (§4.3): a record is authentic only if exactly one commit in `HEAD`'s history touches its path and that commit added it. A3 shows this separates the honest add (1, 1) from delete-and-re-add (3, 2) and from modify-in-place (2, 1). It is one `git log` per session and closes the same route independently of the custody clause, so the two cures do not share a failure.

### 3.2 MATERIAL (a): the custody clause. AFFIRM. Admissible as a reading, without a text change. Form AMENDED.

**The defect.** The ruling's record is written at step (iii) of harvest, but B is plain text in the ledger rows from finalization (A7) and the chain log names dispositions; the runbook's §2.1 reads both before §2.2. A raw file deleted after that reading and before the record is faithfully recorded as `evidence_missing` and excluded (the refuter's R1, R2). "Regenerate before commit is visible" was also untrue: an uncommitted file leaves no trace. Both gaps are real.

**Is the clause an admissible reading of "Window verdict"?** Yes. The text says a slot "with a missing, stale, unparseable or unauthenticated observation" makes the window `battery_float_evidence_missing`. Read alone, "unauthenticated" would include raw bytes that no longer match their recorded digest. But the same amendment says, three times, what the exclusion is: "one outcome-independent, mechanism-named exclusion decided from instrument state alone" (preamble), "checked from its raw bytes alone" (Window verdict), and "Replacement is admissible because the verdict is decided from instrument state alone, before any B value or disposition is read, so it cannot select on outcome" (Replacement). A raw file that the writer wrote and whose digest it recorded into the ledger-hashed `instrument_evidence.json` (A5, A6) is instrument state that was fixed before any human could act; its later absence is a fact about custody, not about the instrument. Reading "missing or unauthenticated" as "the writer did not record it, or recorded it as failed" keeps every exclusion a function of instrument state, which is the only reading under which the Replacement paragraph's own justification is true. A refusal on custody failure is not an exclusion, a replacement, a top-up or a stop, so it adds nothing to the enumerated outcomes; the sealed Revision 5 already refuses issuance when a member's custody bytes do not match its ledger row (`_read_member_evidence`, `:917-935`), so the outcome class exists. The reading never moves a window from refusal toward issuance or exclusion, only from exclusion toward refusal, and the restoring cure re-establishes the very bytes the text asks to be checked. It is therefore a reading, recorded as A-R5b-1 in the decision log, as A-R5a-1 was for R5(a) (`docs/decision_log.md:12207-12209` at `ad7565a7`). Because it narrows the literal reach of one word, the next registration amendment that touches "Window verdict" (BFG-S carries the F-2 text change) must carry the clause into the text so the reading is not relied on indefinitely (§4.11 item 3).

**Form, amended.** The refuter keys custody on "a completed probe (exit 0, not timed out, digest present)". I key it on one fact only, which is simpler to implement, to test and to explain: **a digest was recorded for the bytes before finalization.** The ledger row records a digest for `instrument_evidence.json`; the authenticated evidence records `raw_stdout_sha256` for each phase, for every probe the writer ran, including failed ones (A6). Any bytes with a recorded digest that are absent or differ from it are a custody failure. Everything else (no phase recorded, wrong `raw_path`, non-zero exit, timeout, stale or unparseable bytes that match their digest, predicate failure) is instrument state and yields the text's verdicts unchanged. The exact rule is §4.1. Deleting the raw file of a probe that failed at write time is then also a custody failure, though the window was `evidence_missing` either way; that costs one restore and buys a rule with no second clause.

### 3.3 MATERIAL (b): the last window of an epoch has no external anchor. AFFIRM.

Obligation 10 anchored records in "the next arm notice". W2 (or W3) is followed by issuance, not by an arm, so its record was never anchored outside the machine before B is read; obligation 10 protected exactly the windows M1 does not target. Cure: the anchor is sent at harvest, in the harvest notice, as soon as the pin commit lands, and the next arm notice repeats every window's line (§4.7). With check 4 in place the external anchor is disclosure, not a gate; I keep it because it costs one line per window.

### 3.4 MATERIAL (c): A-R5b-1 needs two more sentences. AFFIRM in substance; wording AMENDED.

Both of the refuter's sentences are adopted in substance. Sentence (i) becomes the check-4 sentence; sentence (ii) becomes the custody sentence in the digest-recorded form of §3.2. The complete final text is §4.8 and replaces the ruling's §4.5 in full.

### 3.5 MATERIAL (d): exemption (i) rests on an unpinned registry. AFFIRM. Cure: the digest pin (§4.6).

A4 shows the real parser accepts appended rows under the fixed id and mechanism, and that with such rows the issuer drops a clean window at exit 0. Being tracked is not being pinned. With the ruling's exemption (i), one appended row removes a session from S, so a confounded zero-valid window could be hidden again (N1 regressing). The pin closes both.

### 3.6 R4: the registry route drops a clean window. AFFIRM. MATERIAL, pre-existing (present at `c6814dd8`; not introduced by A-R5b). Lands in BFG-D before any issuance.

A4 is the executed route. The cure is one constant and one comparison (§4.6). I place it in BFG-D because the issuer's Revision 5 branch is being changed there anyway and no issuance may run before it.

### 3.7 R5: `battery_float.py` is unpinned. AMEND.

Verified: no `configs/**` file, no registration pin and no `ESTIMATOR_CODE_PATHS` entry names the module (refuter E11, re-checked by grep). The refuter's cure (record the module digest; the issuer refuses on mismatch) is amended as follows. The record carries `battery_float_module_sha256` for disclosure and for reconstructing which code judged the window. The issuer does **not** refuse on that digest alone. Reason: under A-R5b-1 the harvest verdict is final; issuance recomputes only to confirm it and refuses on any disagreement, in either direction (§4.4). Post-harvest code drift can therefore only cause a refusal, never a changed verdict, and drift that changes nothing on the window's bytes changes nothing about the claim. Refusing on the digest alone would strand an epoch on a comment edit. What drift does require is sequencing: a predicate change (the F-2 `|update_age_s| ≤ 180` amendment in BFG-S) lands only after the Revision 5 epoch has issued or stopped, or issuance refuses on disagreement (§4.11 item 3). Adding the module to the registration's code pins is a text change for that same amendment.

### 3.8 Other items in the refuter that bear on v1.1

- **E8, two-window tamper → the sanctioned epoch stop.** Closed by ordering: custody failures and record checks run per session before the exact-set check and before the one-replacement bound (§4.4 step order). Test in §4.10 item 3(b).
- **F-1 NIT (a zero-finalized-slot session would be recorded `pass`).** Adopted: `battery-verdict` refuses to record a session with no finalized slot (§4.2). Such a session cannot enter S (S needs a finalized row) and, if named as a registration session, refuses for want of a record. `validate_window`'s empty-session return is unchanged.
- **F-2 (future `UpdateTime`).** Unchanged from the ruling: affirmed for W1; `|update_age_s| ≤ 180` is a BFG-S text-and-code amendment; the seat's `0 ≤ age` form is never adopted because wall time is stamped before the probe runs (`battery_float.py`, `observe`: `wall = time.time()` before `subprocess.run`). The record now carries `update_age_s` per phase for disclosure.
- **R3 (custody root moved after harvest).** Under §4.1 every window refuses as custody failure until the bytes are restored; §4.9 forbids moving the custody root of an unissued epoch.
- **The ruling's H1, §4.1 home, §4.4 refusal-not-exclusion, §5.1, §5.3, §5.4 (tier, narrowing, exemption (ii)):** the refuter agrees and I re-affirm them; they are restated, not changed, in §4.

## 4. Y2 — Harvest-verdict final obligations v1.1

This section is complete on its own. It supersedes the ruling's §4.2, the §4.4 residual paragraph, §4.5 and §6 in full, and restates whatever of §4.1, §4.3, §4.4 and §5.4 an implementer needs. Line numbers are at `ab431280`. Where a text is in a code block it is exact.

### 4.1 The custody rule (one home: `joulewise/battery_float.py`)

`validate_window(session)` evaluates every finalized slot in this order, per slot, with row `obs` and custody directory `C = Path(obs.custody_locator)`:

| Step | Condition | Result |
|---|---|---|
| E0 | `"instrument_evidence.json"` not in `obs.artifact_sha256` | slot `battery_float_evidence_missing` (instrument state; hypothetical, kept for any recovery path that finalizes such a row) |
| E1 | `C/instrument_evidence.json` unreadable, or its sha256 ≠ `obs.artifact_sha256["instrument_evidence.json"]` | **custody failure** (`instrument_evidence.json`) |
| E2 | evidence not valid JSON; `battery_float` absent or not a dict; phase `pre`/`post` absent or not a dict; `raw_path` ≠ `raw/battery_float.<phase>.ioreg`; `raw_stdout_sha256` not a 64-character lowercase hex string; `wall_time_s` absent or not numeric | slot `battery_float_evidence_missing` for that phase (instrument state) |
| E3 | `C/raw/battery_float.<phase>.ioreg` unreadable, or its sha256 ≠ `raw_stdout_sha256` | **custody failure** (`<phase>`) |
| E4 | `exit_code` ≠ 0 or `timed_out` true | slot `battery_float_evidence_missing` for that phase |
| E5 | `parse(raw, float(wall_time_s))` raises `ProbeError` (stale, malformed, object count) | slot `battery_float_evidence_missing` for that phase |
| E6 | parsed `passed` is false | slot `battery_float_confounded` |

Window status: if any slot has a custody failure, `validate_window` **raises** `battery_float.CustodyFailure` (a `RuntimeError` subclass, deliberately outside the `(OSError, KeyError, TypeError, ValueError)` arms so no existing consumer can swallow it as `evidence_missing`); the exception carries `failures: list[{slot, attempt_id, artifact, expected_sha256, observed_sha256|None}]` and `str(exc)` is `custody failure: <slot>/<artifact> expected <sha> observed <sha|absent>; …`. Otherwise `battery_float_confounded` if any slot is confounded, else `battery_float_evidence_missing` if any slot is missing, else `pass`; zero finalized slots still returns `pass` with `slots: []` (unchanged; see §4.2 for why that never becomes a record). Each slot dict gains `instrument_evidence_sha256` (the row's digest), `pre_update_age_s` and `post_update_age_s` (null when not parsed). No consumer treats `CustodyFailure` as a verdict; every consumer refuses (§4.4, §4.5).

Consequence in one sentence: every verdict that can exclude a window is a function of bytes whose digests were recorded before finalization, so no action after finalization can produce an exclusion.

### 4.2 The record and its writer

Path: `configs/calibration/battery_float_verdicts/<session_id>.json`, relative to `--repo-root` (the measurement clone at harvest; it reaches `main` with the head pin). Schema `joulewise.battery_float_verdict.v1`:

```
schema, policy_id ("bfg-01"), session_id, session_kind, session_state,
identity_epoch (the six fields), preregistration_sha256,
ledger_head {sequence, head_digest}, computed_wall_time_s,
tool_commit (git HEAD of --repo-root, 40 hex),
battery_float_module_sha256 (sha256 of joulewise/battery_float.py under --repo-root),
status ("pass" | "battery_float_confounded" | "battery_float_evidence_missing"),
slots: [ {slot, attempt_id, verdict, reasons, pre_raw_sha256, post_raw_sha256,
          pre_update_age_s, post_update_age_s, delta_q_mah, instrument_evidence_sha256} ]
```

Writer: a new subcommand `scripts/issue_calibration_acceptance_generation.py battery-verdict` with exactly the flags `--ledger`, `--head-pin`, `--repo-root`, `--session-id`, `--preregistration`, `--preregistration-sha256`. It, in order:

1. reads the registration bytes; refuses unless their sha256 equals `--preregistration-sha256`;
2. loads the ledger snapshot exactly as `prepare-candidate` does (`require_committed_pin=True`, `verify_custody=False`, `mode="read_replay"`, `repo_root=--repo-root`); refuses on `snapshot.refusal_reasons`;
3. refuses unless the session exists, is `SESSION_KIND_DERIVATION`, is in `TERMINAL_SESSION_STATES`, has at least one finalized slot (`no finalized slot; nothing to record`), and has at least one finalized row whose `identity_epoch` equals `REVISION_FIVE_EPOCH`;
4. refuses with `pre-A-R5b session` when every finalized row's `instrument_evidence.json` authenticates against its row and lacks the `battery_float` key;
5. refuses with `record exists` if the output path exists;
6. calls `validate_window`; on `CustodyFailure` refuses with `custody failure: <detail>; restore the custody bytes byte-exact from the harvest archive` and writes nothing;
7. builds the record with `verdict_record(...)` and writes it with `open(path, "x")` (create-exclusive) under `configs/calibration/battery_float_verdicts/`, creating the directory if needed;
8. prints exactly one line to stdout, `<session_id>: battery=<pass|confounded|evidence_missing>`, and exits 0.

Every refusal prints `REFUSED: <reason>` and exits 3. The subcommand never prints a count, a value or a slot. It never runs `git`; the operator commits (§4.9).

### 4.3 Authentication: `battery_float.load_committed_verdict(repo_root, session_id, *, session, preregistration_sha256)`

Returns the record or raises `battery_float.NoRecord(reason)`. Let `rel = configs/calibration/battery_float_verdicts/<session_id>.json`.

1. `git -C <repo_root> show HEAD:<rel>` succeeds; its bytes pass `joulewise.authentication_io.ingest_git_authentication_input(rel, bytes, grammar="json", label="Git-committed battery-float harvest verdict")`; and the working-tree file's bytes equal them. Else `NoRecord("absent or uncommitted")` or `NoRecord("working tree differs from HEAD")`.
2. `git -C <repo_root> log --no-renames --format=%H -- <rel>` lists exactly one commit, and `git -C <repo_root> log --no-renames --diff-filter=A --format=%H -- <rel>` lists exactly that commit. Else `NoRecord("path history is not a single adding commit (<n> commits, <m> adding)")`. (A3: honest add 1/1; delete-and-re-add 3/2; modify-in-place 2/1.)
3. `schema == "joulewise.battery_float_verdict.v1"`, `session_id` equal, `identity_epoch` equal to the epoch of every finalized row of `session`, `preregistration_sha256` equal to the caller's pinned digest. Else `NoRecord("identity mismatch: <field>")`.
4. The record's slot names equal `session.finalized_slots` keys, and each slot's `instrument_evidence_sha256` equals that row's `artifact_sha256["instrument_evidence.json"]`. Else `NoRecord("slot binding mismatch: <slot>")`.

Not checked, documentation only: `ledger_head`, `tool_commit`, `battery_float_module_sha256`, `computed_wall_time_s`. Not checked: that the adding commit also touched the head pin (a runbook rule, §4.9, not an authentication check).

`battery_float.compare_verdict(record, recomputed) -> str | None` returns the first difference, or `None`, over: `status`; the slot-name set; and per slot `verdict`, `pre_raw_sha256`, `post_raw_sha256`, `instrument_evidence_sha256` (null-aware). `reasons` are not compared.

### 4.4 The issuer (`_prepare_candidate`, replacing `:1315-1364`)

Inside `if revision_five:`, in this order:

1. `dispositions = _registered_dispositions()` (now pinned, §4.6).
2. Computed set = `registration_ids ∪ foreign_owners ∪ S`, where `foreign_owners` is as today (`:1319-1326`) and **S** is every session that is derivation-kind, terminal, and owns at least one finalized row whose `identity_epoch` equals the target epoch, excluding (i) any session owning a row whose `content_id` is in the pinned registry, and (ii) any session all of whose finalized rows have an `instrument_evidence.json` that authenticates against its row and lacks the `battery_float` key. Exemption (ii) never applies to a session in `registration_ids`.
3. For each session in the computed set, in sorted order, skipping (as today) any that is not derivation-kind or not terminal:
   - `recomputed = validate_window(session)`; on `CustodyFailure` → `PrepareRefusal("battery-float custody failure for <id>: <detail>; restore the custody bytes byte-exact from the harvest archive; not issued")`;
   - `record = load_committed_verdict(...)`; on `NoRecord` → `PrepareRefusal("battery-float harvest verdict missing or uncommitted for <id>: <reason>; not issued")`;
   - `diff = compare_verdict(record, recomputed)`; if not `None` → `PrepareRefusal("battery-float harvest verdict for <id> cannot be re-established from raw bytes (<diff>); custody failure; not issued")`;
   - `battery_results[id] = record` (the recorded status governs everything below).
4. `computed_confounded = {id for id, r in battery_results.items() if r["status"] != "pass"}`.
5. The exact-set check against `--battery-confounded-session-id`, text unchanged (`:1337-1356`).
6. The bound: `len(computed_confounded) > 1` → the unchanged text `more than one battery-float non-pass window in this epoch: …; the epoch stops and returns to council`. Because step 3 precedes it, a tampered pair refuses as custody, never as the sanctioned stop.
7. `session_ids` minus `computed_confounded`, as today (`:1364`).

A refusal in step 3 changes `session_ids` in no way, accepts no replacement, and is not counted at step 6. The A-7 sweep (`:1447-1458`) is unchanged. `derivation_notes` gains `battery_verdict_records: [{session_id, status, verdict_file_sha256, verdict_commit}]` for every session in `battery_results`, and each `battery_confounded_sessions` entry gains `verdict_file_sha256` and `verdict_commit`; no B value appears in either.

### 4.5 The other consumers

- **`registration_dry_run` (`:176-228`).** For each named session that is terminal and has a Revision 5 row: `validate_window`; `CustodyFailure` → `blocker: session <id>: battery custody failure: <detail>`; `load_committed_verdict` → `NoRecord` → line `<id>: battery=<status> recorded=absent` and `blocker: session <id>: battery harvest verdict missing or uncommitted (<reason>)`; disagreement → `blocker: session <id>: battery harvest verdict cannot be re-established (<diff>)`; else line `<id>: battery=<status> recorded=<status>` and, on non-pass, the existing `valid=0 excluded=battery_<status>` line and blocker. After the loop: `blocker: more than one battery-float non-pass window in this epoch: …` when the recorded non-pass sessions among (named ∪ S) exceed one, S computed by the same helper `_battery_computed_set(snapshot, registration_ids, target_epoch, dispositions)` the issuer uses. Still no value printed.
- **`calibration_cadence_report.report_window` (`:47-84`).** After the ledger load: `validate_window`; `CustodyFailure` → `ValueError("battery-float custody failure: <detail>")`; `load_committed_verdict(root, …)` → `NoRecord` → `ValueError("battery-float harvest verdict missing or uncommitted: <reason>")`; disagreement → `ValueError("battery-float harvest verdict cannot be re-established: <diff>")`; `diagnostic_only` keyed off the recorded status. The report cannot run before the pin commit (it already loads with `require_committed_pin=True`), and now cannot run before the record.
- **`issue_epoch_continuation.derive_record` (`:86-93`).** Same three outcomes as refusals `battery_float_custody_failure: <detail>`, `battery_float_verdict_missing: <reason>`, `battery_float_verdict_mismatch: <diff>`, exit 3; a recorded non-pass refuses as today.

### 4.6 The registry pin

In `scripts/issue_calibration_acceptance_generation.py`, beside `DISPOSITION_DECISION_ID` (`:398`):

```
DISPOSITION_REGISTRY_SHA256 = "ba1ba3fc596c9ef7f4014131e5cbc2012559f72bab41cafb89e004056790a63c"
```

`_registered_dispositions` (`:1133`) reads the file as bytes, and before parsing refuses with `PrepareRefusal("observation disposition registry digest mismatch: <observed> != pinned <pinned>; not issued")` when the sha256 differs. Any future registry change updates the constant in the same reviewed PR. Exemption (i) in §4.4 is keyed to the pinned file's content ids, so it can no longer be manufactured.

### 4.7 The anchor

At harvest, as soon as the pin commit of §4.9 step (iv) lands, the harvest notice carries, for the harvested window and for every earlier harvested window of the epoch, one line each:

```
<session_id>: battery=<pass|confounded|evidence_missing> verdict_sha256=<64 hex of the committed file> verdict_commit=<40 hex>
```

The next arm notice repeats every line. Because the last window's harvest is followed by issuance, the harvest notice is the anchor that matters; check 4 (§4.3) is the mechanical guarantee, and the notice is disclosure.

### 4.8 Decision-log record (exact final text; replaces the ruling's §4.5; the magistrate appends it below A-R5b's entry)

```
## ACCEPTANCE-25G83-02 amendment A-R5b, binding reading A-R5b-1 (2026-09-25): the harvest verdict is the window verdict; custody failure is never a verdict

A-R5b-1 (2026-09-25, cold gate HARVEST-VERDICT-FINAL-01 and its addendum, from Opus contract lens finding M1 on PR #423 and the paired refuter's P2-E1): Under A-R5b "Window verdict", "Consequences" and "Replacement" in `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, a derivation window's battery verdict is the one computed at harvest from raw bytes and recorded in the committed file `configs/calibration/battery_float_verdicts/<session_id>.json` in the same commit as the ledger head pin, before the cadence report, before the count-only dry run and before any B value is read. That recorded verdict, `pass` included, is final for the window. A record is authentic only if its working-tree bytes equal the `HEAD` blob and exactly one commit in `HEAD`'s history touches its path, the commit that added it; any later modification, deletion or re-addition makes it no record. The issuer's own recomputation from raw bytes is a custody check of the record, not a second decision: a missing, uncommitted or inauthentic record, or any disagreement between the record and the recomputation in either direction, refuses issuance and is never an exclusion, never a replacement trigger and never counted toward the one replacement per epoch. An observation is "missing or unauthenticated" in the sense of "Window verdict" only when the capture writer did not record it (no phase, wrong raw path, no digest) or recorded it as failed (non-zero exit, timeout) or its retained bytes match the recorded digest but are stale or unparseable; bytes whose digest the ledger-authenticated evidence or the ledger row records, and which are now absent or differ from that digest, are a custody failure at harvest exactly as at issuance: no verdict is computed, no record is written, and every consumer refuses. Restoring the custody bytes byte-exact from the harvest archive, so that the recomputation agrees, is the only cure. A window whose recorded verdict is `battery_float_confounded` or `battery_float_evidence_missing` is excluded and replaced exactly as A-R5b says; the one-replacement bound counts every recorded non-pass window of the epoch, whether or not it holds a valid row, and custody refusals are checked before that bound. The observation disposition registry the issuer consults is pinned by digest in the issuer; any other registry content refuses issuance. The registration text is unchanged; the next amendment that edits "Window verdict" carries this reading into the text.

Ratification: docs/process_traces/2026-09-25-activation-ed17a643/41-coldgate-packet-harvest-final/20-coldgate-fable-harvest-final-ruling.md §4 as amended by 30-addendum/21-coldgate-fable-harvest-final-addendum-ruling.md §3–§4.
```

### 4.9 Harvest order (runbook §2.2a, one block, commands)

(i) §2.0 rebuild and authenticate the ledger at head-equals-pin. (ii) Any desk recovery the existing subcommands provide, so the session is terminal; the custody root of an unissued epoch is never moved, relocated or offloaded. (iii) `battery-verdict --session-id "$SESSION_ID"` with the harvest's `--ledger`, `--head-pin`, `--repo-root "$MEASUREMENT_ROOT"`, `--preregistration` and `--preregistration-sha256` (the digest the arm notice pinned); on `REFUSED: custody failure` restore the bytes from the byte-exact preservation copy §2.1 requires and re-run; nothing else is done until it exits 0. (iv) One commit: `git add configs/calibration/calibration_ledger_head.json configs/calibration/battery_float_verdicts/$SESSION_ID.json && git commit -m "Harvest $SESSION_ID: ledger head pin and battery-float verdict"`. (v) The harvest notice line of §4.7. (vi) The cadence report. (vii) `check --session-ids "$SESSION_ID"`. (viii) Only now the §2.1 reads of `derivation-chain.log` slot lines, ledger rows and evidence files; `night.log`, `result.json`, the receipt or refusal and the launchd files may be read before (iii) because they hold no B and no disposition. The block states that the committed record is the window verdict, that the cadence report and `check` refuse without it, and that the reading order is procedure while §4.1 is the guarantee.

### 4.10 Implementation obligations (numbered; tests are defect-shaped, at production call sites)

1. **`joulewise/battery_float.py`.** `CustodyFailure(RuntimeError)`, `NoRecord(ValueError)`, `VERDICT_SCHEMA`, the §4.1 slot order in `validate_window`, `verdict_record(session, *, snapshot, preregistration_sha256, tool_commit, module_sha256, wall_time_s)`, `load_committed_verdict` (§4.3, reusing `joulewise.authentication_io.ingest_git_authentication_input`), `compare_verdict`. One home; nothing re-implements them. Tests (`tests/test_battery_float.py`): (a) a recorded probe's raw file deleted → `CustodyFailure` naming `<slot>/post`; (b) one byte appended to a recorded raw file → `CustodyFailure` (this re-asserts `:202-203`, A10); (c) the evidence file itself altered → `CustodyFailure` naming `instrument_evidence.json`; (d) a phase absent from the evidence → `evidence_missing` (keeps `:200-201`); (e) `exit_code` 1 with an empty raw file present → `evidence_missing`, and with that empty file deleted → `CustodyFailure`; (f) stale bytes that match their digest → `evidence_missing` (keeps `test_stale_at_harvest`); (g) confounded and a custody failure in different slots → `CustodyFailure` (custody precedes every verdict); (h) `load_committed_verdict` in a scratch git repo: honest add → record; delete-and-re-add → `NoRecord("path history…3 commits, 2 adding")`; modify-in-place → `NoRecord("…2 commits, 1 adding")`; uncommitted edit → `NoRecord("working tree differs")`; absent → `NoRecord("absent or uncommitted")`; wrong `preregistration_sha256` → identity mismatch; altered `instrument_evidence_sha256` → slot binding mismatch.
2. **`battery-verdict` subcommand** (§4.2; parser beside `check`, `:1905`). Tests (`tests/test_issue_calibration_acceptance_generation.py`, through `issuer.main`): (a) clean W1 → exit 0, stdout exactly one line, no `b_fiducial_s`, file present with every §4.2 field; (b) second run → exit 3 `record exists`, file byte-identical; (c) a recorded raw file deleted before the first run → exit 3 `custody failure`, no file written; (d) non-terminal session → 3; wrong registration digest → 3; zero finalized slots → 3 `no finalized slot`; (e) a same-epoch session whose authenticating evidence lacks `battery_float` → 3 `pre-A-R5b session`.
3. **`_prepare_candidate`** (§4.4). Tests through `issuer.main`, with records written by the fixture builder (item 6) and committed with the terminal pin: (a) M1 closed: W1, W2 clean with records, `prepare-candidate W1 W2` → 0; add W2-prime; delete `W2-d03/raw/battery_float.post.ioreg`; `prepare-candidate W1 W2-prime --battery-confounded-session-id W2` → 3 `custody failure for W2`; `prepare-candidate W1 W2` → 3 with the same text, not `omitted`; restore the file byte-exact → `prepare-candidate W1 W2` → 3 on A-7 (the honest state), proving the refusal cleared; (b) E8 closed: one raw file deleted in each of W1 and W2, both declared, W2-prime registered → 3 `custody failure`, not `more than one`; (c) P2-E1 closed: W2's committed record `git rm`'d and a new `evidence_missing` record committed (built directly, since the tool would refuse) → 3 `missing or uncommitted for W2: path history…`; (d) missing record → 3 `missing or uncommitted`; present but uncommitted → 3; committed → 0; (e) recorded non-pass agrees: the seat's `test_replacement_issues_without_reading_confounded_b_or_a7_refusal` gains a committed W1 record and still issues; a recorded non-pass whose raw bytes are then replaced so recomputation passes → 3 `custody failure` (the digest no longer matches); (f) N1 closed: W1 twelve `ordinary-invalid` charging rows with a committed record, W1-prime and W2 clean with records: `prepare-candidate W1-prime W2` unnamed → 3 `computed non-pass session omitted: W1`; named → 0 with W1 in `battery_confounded_sessions` carrying `verdict_file_sha256`; a second recorded non-pass window → 3 `more than one`; (g) `derivation_notes.battery_verdict_records` lists every computed-set session and contains no `b_fiducial_s`.
4. **`registration_dry_run`, `report_window`, `derive_record`** (§4.5). Tests: dry run prints `recorded=absent` and the blocker on a session with no record, `recorded=pass` with one, and a custody blocker on a deleted raw file; the seat's tampered-raw assertion at `tests/test_issue_calibration_acceptance_generation.py:2348-2356` re-asserts `CustodyFailure`; `report_window` raises on a missing record and on a custody failure and labels `diagnostic_only` from the record; `issue_epoch_continuation` refuses `battery_float_verdict_missing` and `battery_float_custody_failure`.
5. **Registry pin** (§4.6). Tests (`tests/test_acc_25g83_rev5.py`): the tracked file's sha256 equals `DISPOSITION_REGISTRY_SHA256`; a copy with one appended row under the fixed id and mechanism → `PrepareRefusal("…digest mismatch")` from the real `_registered_dispositions`; and, through `issuer.main` with `DISPOSITION_REGISTRY` patched to that copy, the A4 route (`prepare-candidate W1 W2-prime` with W2's ids appended) → 3 `digest mismatch`, while with the tracked file it → 3 on A-7.
6. **Fixture builder `tests/fixtures/epoch_bootstrap/build.py`.** An option `verdict_records: bool = False` that, per session, runs `verdict_record` and commits the file with the terminal pin in the same commit; a helper `rerecord_verdict(fixture, session_id, status)` that performs the `git rm` and re-add of test 3(c).
7. **Runbook `docs/phase_2/derivation_night_runbook.md`.** New §2.2a with the §4.9 block, placed between §2.2 and §2.3; §2.1's table gains one row for the verdict file; §2.3 gains one sentence that the battery verdict is recorded before any slot line, ledger row or evidence file of the session is read.
8. **Harvest notice and arm notice** (§4.7): the template in `docs/process/NIGHT_HANDBACK.md` and the arm record carry the per-window line.
9. **Decision log:** A-R5b-1 as in §4.8, verbatim.
10. **PR body:** the two statements the BFG addendum §5.3 item 8 requires, plus: "A-R5b-1 is recorded in the decision log; the committed harvest verdict file is the window verdict; a custody failure refuses and never excludes; the disposition registry is digest-pinned."
11. **Pin regression** (unchanged from the BFG addendum §5.6 test 5): `SAMPLERS`, `protocol_v3.json`, the `ESTIMATOR_CODE_PATHS` digests and the chain digest are unchanged by BFG-D; `manifest.artifacts` and `instrument_evidence.artifact_sha256` key sets are byte-identical.

### 4.11 Timing

1. Items 1–11 land in BFG-D, which merges to `main` under the full gate before W1 arms (BFG addendum §5.7 item 2). A W1 harvested without item 2 would have no record and could never issue.
2. No issuance and no second window of the epoch before items 3–5 are on `main`.
3. The BFG-S predicate change (`|update_age_s| ≤ 180`), the carrying of the custody clause into "Window verdict", and the addition of `joulewise/battery_float.py` to the registration's code pins are one text-and-code amendment that lands only after the Revision 5 epoch has issued or stopped; if it lands earlier, issuance refuses on disagreement by design and the epoch waits.
4. The seat's open N-1 (`arm_readiness.py` liveness constant, A2) is not a question here and is not ruled.

### 4.12 Plain summary for Ed (5 lines)

1. The reviewer found a hole in the fix: with plain git, a person could delete a battery file, remove the committed verdict and commit a fresh "evidence missing" one, and the window would still be dropped and swapped.
2. Two repairs close it. First, any battery file the writer recorded a fingerprint for must be present and unchanged; if not, every tool stops and says "restore from the archive" instead of calling the window unusable. Second, a verdict file only counts if it was added once and never touched again.
3. The verdict is still written at harvest, before results are read, and committed with the ledger pin; the harvest email names each window's verdict and file fingerprint so the last window is anchored too.
4. A second, older hole is closed: the list of "disposed" captures is now fingerprint-locked in the tool, so no one can quietly add a window's captures to it.
5. The registered text does not change; one binding reading goes in the decision log; all the code lands in the BFG-D PR before W1 arms.

## 5. Packet hygiene

Complete and neutral for Y1 and Y2. The charge labels both inputs as arguments and names the code revision. It states that the only change since `06671b69` is the liveness constant; A2 confirms it. One imprecision: the charge summarises the refuter's Phase 1 R4 as "the registry route drops a clean window; pre-existing" without saying the refuter tiered it MATERIAL; I verified and tiered it myself (§3.6). No effect on decidability. The charter digest again arrived only through the charge (§1).

## 6. Disposition summary

| Item | Verdict | Severity | Cure lands |
|---|---|---|---|
| P2-E1 HEAD-only authentication | AFFIRM (executed A3) | BLOCKER against the ruling as written | §4.1 custody rule + §4.3 check 4, BFG-D |
| (a) pre-record / regenerate-before-commit window | AFFIRM; custody clause admissible as a reading, form amended to digest-recorded | MATERIAL | §4.1, §4.2 step 6, BFG-D |
| (b) last window unanchored | AFFIRM | MATERIAL | §4.7 harvest notice, BFG-D |
| (c) two sentences for A-R5b-1 | AFFIRM in substance, wording amended | MATERIAL | §4.8, decision log |
| (d) unpinned registry under exemption (i) | AFFIRM (executed A4) | MATERIAL | §4.6, BFG-D |
| R4 registry route | AFFIRM, pre-existing | MATERIAL | §4.6, BFG-D, before any issuance |
| R5 module drift | AMEND: record the digest, refuse only on verdict disagreement; sequence BFG-S after issuance | NIT after the record | §4.2 field, §4.11 item 3 |
| Refuter F-1 NIT, R3, E8 | adopted (§3.8) | NIT | §4.2 step 3, §4.9, §4.4 order |
| Ruling §4.1, §4.4 core, §5.1–§5.4 | re-affirmed | — | restated in §4 |

Where I am silent I concur with the ruling; where I differ from it: the authentication (four checks, not three), the custody rule (new), the anchor timing (harvest, not next arm), the registry pin (new), the helper's module (`authentication_io`), and the A-R5b-1 text (§4.8 replaces §4.5). Where I differ from the refuter: the custody rule keys on a recorded digest rather than on a completed probe; R5 does not refuse on the module digest alone.

## 7. Cleanup

After writing this file: `git worktree remove --force /tmp/cg-hv-add-bfgd`, `rm -rf /tmp/cg-hv-add-repro` and the `mkdtemp` fixture directory; `git status --porcelain` in this worktree then lists only this file. The scratch git repository of A3 was removed inside the command that created it.
