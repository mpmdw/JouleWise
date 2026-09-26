# Cold gate HARVEST-VERDICT-FINAL-01: ruling (Fable 5.1)

Judge: Claude Fable 5.1 (`claude-fable-5-1`), one non-interactive foreground session, no subagents, no background tasks, no watchers. Session 2026-09-25, about 17:40–18:05 PDT. Worktree `JouleWise-wt-ed17a643-cg-hv` at `c382b236`. Ruled code: `origin/feat/2026-09-25-bfg-d` at `06671b69`; ruled text: PR #423 at `ad7565a7`.

**Verdicts.** H1 AFFIRM (the route is real; MATERIAL). H2 ruled: one committed harvest verdict file per window, written by the issuer script, in the pin commit; the issuer refuses on any disagreement; decision-log text issued below; the A-R5b registration text is unchanged. H3: F-1 AFFIRM, F-2 AFFIRM for W1 (NIT, later amendment), F-6 AFFIRM, N1 REJECT the current behaviour (MATERIAL, cure in BFG-D). H4: eleven obligations, listed in §6.

## 0. Contamination disclosure

- **Loaded by the harness, not by choice:** the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (one-line pointers; I opened no memory file), plus the git status and five recent commit subjects.
- **Opened, read-only, inside the charge's read set:** the packet (charge and both exhibits); `docs/process/coldgate_charter.md`; the BATTERY-FLOAT-01 addendum ruling `../10-coldgate-packet-bfg/30-addendum/21-coldgate-fable-bfg-addendum-ruling.md` §5–§7 (sha256 `1047af22…3add`, matching the lens's citation); the registration file and `docs/decision_log.md` diff at `ad7565a7`; at `06671b69`: `joulewise/battery_float.py`, `joulewise/calibration_ledger.py` (targeted ranges), `scripts/issue_calibration_acceptance_generation.py` (targeted ranges), `scripts/calibration_cadence_report.py`, `scripts/issue_epoch_continuation.py` (diff), `scripts/validate_powermetrics_fiducial.py` (targeted ranges), `configs/calibration/observation_dispositions.json`, `configs/calibration/calibration_ledger_head.json`, `tests/fixtures/epoch_bootstrap/build.py`, and targeted ranges of three test files; `docs/phase_2/derivation_night_runbook.md` §2.0–§2.3 and two short ranges (procedure text, not status).
- **Contamination to disclose:** one `git grep -n -i harvest` over `scripts joulewise docs/process/*.md docs/runbooks` returned matching lines from `docs/process/NIGHT_HANDBACK.md` and `docs/process/MAGISTRATE_WATCHDOG.md`, including dated "Executed" night-status lines (arm times, harvest outcomes, message ids). I read those lines as grep output before I could stop; I opened neither file and used nothing from them in any finding. Their effect on this ruling: none that I can identify; every load-bearing conclusion below cites code or the registration text.
- **Not opened:** `RUN_STATE.md`, `TASK_QUEUE.md`, any council log, run report, memory file, or `docs/process_traces` file outside this packet other than the addendum ruling named above.
- **Write-scope deviation (disclosed):** I created a detached worktree `/tmp/cg-hv-bfgd` at `06671b69` (the charge permits this) and a scratch directory `/tmp/cg-hv-repro/` holding two reproduction scripts; fixture ledgers went to `tempfile.mkdtemp` under `/var/folders`. I removed the worktree after writing this file. I ran the Homebrew `python3` (3.14.7) with `PYTHONDONTWRITEBYTECODE=1`; no interpreter or file under `/Users/edr/code/JouleWise`, `/Users/edr/night-custody` or `~/Library/LaunchAgents` was touched. `git status --porcelain` in this worktree was empty before this file was written.

## 1. Verification before the merits

| Check | Expected | Observed | Method |
|---|---|---|---|
| Charter digest | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` (supplied in the charge, which is the only independent value this session received) | `099de884…c95d81` | `shasum -a 256 docs/process/coldgate_charter.md` at `c382b236` |
| ex-01 | `10d34333…a72b78` | identical | `shasum -a 256` |
| ex-02 | `3277bd17…668b186` | identical | `shasum -a 256` |
| Commits | `ad7565a7`, `06671b69` are commits | both `commit` | `git cat-file -t` |

The charter's expected value did not arrive from a source independent of the packet; the charge is the packet. I record that limitation and proceed, since the charge's own bytes are the convening instrument here.

## 2. Executed evidence

| # | What | Result |
|---|---|---|
| E1 | `python3 -m unittest tests.test_battery_float tests.test_issue_calibration_acceptance_generation.BatteryFloatRevisionFiveTests` at `06671b69` | 17 tests, OK, 14.9 s |
| E2 | M1 reproduction, `/tmp/cg-hv-repro/m1_repro.py`, using the seat's fixture builder and the production `prepare-candidate` entry point (`issuer.main`), disposition registry mocked to `{}` exactly as the seat's tests do. Step 1: ledger with W1 and W2, both windows passing the predicate on every slot. | `prepare-candidate --registration-session-id W1 W2` → exit 0, corpus n = 24. B values are now read. |
| E3 | Step 2: same ledger plus a fresh W2-prime (twelve valid rows, same epoch). `prepare-candidate W1 W2`. | Exit 3, `valid same-epoch observations outside this registration: W2-prime-d01 … d12; not issued (ruling 46 addendum A-7)`. Honest state refuses. |
| E4 | Step 3: delete one file, `runs/instrument_validation/W2-d03/raw/battery_float.post.ioreg`. Then `issuer._read_member_evidence(W2-d03)` and `validate_window(W2)`. | `_read_member_evidence` succeeds (no refusal). `validate_window(W2)` = `battery_float_evidence_missing`. `prepare-candidate W1 W2` → exit 3, `computed non-pass session omitted: W2`. |
| E5 | Step 4: `prepare-candidate --registration-session-id W1 --registration-session-id W2-prime --battery-confounded-session-id W2`. | **Exit 0.** `registration_session_ids = ['W1', 'W2-prime']`; `battery_confounded_sessions = [('W2', 'battery_float_evidence_missing')]`. |
| E6 | N1 reproduction, `/tmp/cg-hv-repro/n1_repro.py`: W1 has twelve `ordinary-invalid` rows with charging observations on every slot; W1-prime and W2 clean. `prepare-candidate W1-prime W2` with W1 unnamed. | **Exit 0**, `derivation_notes.battery_confounded_sessions = []`. The confounded window is absent from the claim-bearing candidate. |
| E7 | Same, with `--battery-confounded-session-id W1`. | Exit 3, `declared session is not a terminal derivation session of this registration or an A-7 foreign-row owner: W1`. The operator cannot disclose it even deliberately. |
| E8 | Where a harvest verdict is written to disk on the branch: `git grep` for `calibration_cadence_report` and `count-only` over `docs/phase_2 docs/process docs/calibration configs scripts` at `06671b69`; reading of `report_window`, `registration_dry_run`, `_prepare_candidate`. | No code writes a verdict anywhere. `report_window` returns a dict printed to stdout; `registration_dry_run` returns lines; `derivation_notes` is written only inside the candidate, at issuance, after B is read. The cadence report has no runbook step at `06671b69` (the only textual home of the harvest order is the sealed Revision 5 sentence at registration line 612). |
| E9 | Writer bracket sites at `06671b69` | pre-observation at `validate_powermetrics_fiducial.py:2266`, directly after `AFTER_CUSTODY_DIRECTORY_CREATION` (`:2265`); post-observation at `:2494`, after `active_sampler = None` (`:2492`); `pre_spawn = clock.stamp()` at `:2334`, `post_parse = clock.stamp()` at `:2491`. Matches the addendum's §5.3 item 6. |

## 3. H1 — Is the route real? AFFIRM. Severity MATERIAL.

Yes. E2–E5 execute the lens's five steps on the production entry point. The mechanism, verified in code:

- `joulewise/battery_float.py` `validate_window` reads `custody/raw/battery_float.{pre,post}.ioreg` directly and classifies an `OSError` as `battery_float_evidence_missing` (the inner `except (OSError, KeyError, TypeError, ValueError)` branch). The two battery raw files are deliberately outside `manifest.json.artifacts` (addendum §5.3 item 6: "byte-for-byte unchanged"), so `_read_member_evidence` (`issue_calibration_acceptance_generation.py:917-935`), which authenticates only `manifest.json` and `instrument_evidence.json`, never sees their loss (E4). That is the asymmetry the lens named: at `main`, a member's custody loss is a refusal; on BFG-D, the loss of one battery raw file is an exclusion.
- `_prepare_candidate` (`:1310-1367`) recomputes the verdict at issuance, removes the computed non-pass sessions from `session_ids` before the positional checks, and accepts a replacement in their place. There is no record of the harvest-time verdict to compare against, because none exists (E8).
- `prepare_candidate` (`:1213-1224`) writes `--out` unconditionally; nothing forbids re-preparation after B has been read.

The lens's E9–E11 are confirmed. Its severity (MATERIAL, not BLOCKER for #423) is right: the registration text supports the cure without an edit (§4 below), and the route needs an actor to act after B is seen or an honest custody loss, neither of which the text licenses.

## 4. H2 — The cure

### 4.1 Where the harvest verdict is recorded, and by what

**Ruling.** The harvest verdict is recorded in a committed, write-once JSON file per window:

`configs/calibration/battery_float_verdicts/<session_id>.json`, relative to the repository root the ledger belongs to (the measurement clone at harvest; the file then reaches `main` the same way `configs/calibration/calibration_ledger_head.json` does).

It is written by a new subcommand of the issuer script, `scripts/issue_calibration_acceptance_generation.py battery-verdict`, with the flags `--ledger`, `--head-pin`, `--repo-root`, `--session-id`, `--preregistration`, `--preregistration-sha256`. The subcommand: loads the ledger snapshot exactly as `prepare-candidate` does (`require_committed_pin=True`, `mode="read_replay"`); refuses unless the session is derivation-kind, terminal, and carries `REVISION_FIVE_EPOCH` on at least one finalized row; refuses if the registration digest does not match; refuses if the output file already exists; calls `battery_float.validate_window(session)`; writes the record; prints one line, `<session_id>: battery=<pass|confounded|evidence_missing>`, and nothing else (no count, no value). Exit 0 on a written record of any status; exit 3 on refusal.

Record schema `joulewise.battery_float_verdict.v1`:

```
schema, policy_id ("bfg-01"), session_id, session_kind, session_state,
identity_epoch (the six fields), preregistration_sha256,
ledger_head {sequence, head_digest} (the authenticated pin at computation),
computed_wall_time_s, tool_commit (git HEAD of --repo-root),
status, slots: [ {slot, attempt_id, verdict, reasons, pre_raw_sha256,
                  post_raw_sha256, delta_q_mah, instrument_evidence_sha256} ]
```

`instrument_evidence_sha256` is the ledger row's `artifact_sha256["instrument_evidence.json"]`, copied at computation; it binds every slot of the record to the ledger row it was judged against.

Why not the other three homes the charge names:

- **The ledger.** A new receipt kind changes the grammar that `load_calibration_ledger_snapshot`, both replay modes, the exact-set checks and `recover_calibration_ledger.py` parse. That is the largest blast radius available on the custody-critical component, days before W1, for no authentication the committed file does not already have (the ledger's own authority rests on the same Git-HEAD mechanism, `_committed_pin_bytes`, `calibration_ledger.py:1278-1300`).
- **The pin commit alone.** The pin records a sequence and a digest of receipts; it carries no verdict. The verdict file travels in the pin commit and inherits its authentication; that is the ruling above.
- **The cadence report output.** It is stdout, produced after the verdict should already exist, and at `06671b69` it recomputes rather than records.

### 4.2 Authentication

A consumer authenticates a record by three checks, all in one new function `battery_float.load_committed_verdict(repo_root, session_id)`:

1. The working-tree bytes equal `git show HEAD:configs/calibration/battery_float_verdicts/<session_id>.json` run in `repo_root`, through the existing `ingest_git_authentication_input(…, grammar="json", label="Git-committed battery-float harvest verdict")`. An uncommitted, modified or absent file is "no record".
2. The record's `session_id`, `identity_epoch` and `preregistration_sha256` match the session and the digest the consumer was invoked with.
3. The record's slot set equals the session's finalized-slot set, and each slot's `instrument_evidence_sha256` equals the ledger row's `artifact_sha256["instrument_evidence.json"]`.

`ledger_head` is documentation, not a check; the ledger head advances when the next window opens.

### 4.3 When it is written

At harvest, in this order, which the runbook must state as one block (obligation 9): (i) §2.0 rebuild and authenticate the ledger at head-equals-pin; (ii) any §2.3 desk recovery, so the session is terminal; (iii) `battery-verdict` for the night's session; (iv) the pin commit, `git add` of the head pin and the verdict file in one commit; (v) the cadence report; (vi) `check --session-ids` (the count-only dry run). The order is enforced mechanically at (v) and (vi), not only procedurally: `report_window` and `registration_dry_run` refuse or block, respectively, when a Revision 5 terminal session has no committed record (obligations 4 and 5). Because the cadence report on BFG-D already loads the ledger with `require_committed_pin=True`, it cannot run before the pin commit, and the pin commit is where the record lands.

The file may be regenerated before it is committed (the tool refuses to overwrite, so the operator deletes it first, which is visible); once committed it is final. The record is written before any B value is read; it prints none and contains none.

### 4.4 What the issuer does on disagreement

For every session in its computed set (registration sessions, A-7 foreign-row owners, and the N1 sweep of §5.4), `_prepare_candidate` loads the committed record and recomputes `validate_window`. It refuses with `PrepareRefusal` when:

- no committed record exists: `battery-float harvest verdict missing or uncommitted for <session_id>; not issued`;
- the recorded `status` differs from the recomputed status, or the slot sets differ, or any slot's `verdict`, `pre_raw_sha256`, `post_raw_sha256` or `instrument_evidence_sha256` differs: `battery-float harvest verdict for <session_id> cannot be re-established from raw bytes (recorded <s>, recomputed <s'>); custody failure; not issued`.

A refusal is never an exclusion: the session is not removed from `session_ids`, no replacement is accepted for it, and it is not counted toward the one replacement per epoch. Restoring the custody bytes byte-exact from the harvest archive, after which the recomputation agrees, clears the refusal; nothing else does. When record and recomputation agree, the existing exact-set rule, exclusion and replacement bound run unchanged. The same comparison, with the same outcomes, runs in `registration_dry_run` (as a `blocker:` line), in `report_window` (as an error), and in `issue_epoch_continuation.derive_record` (as a refusal), through the one shared function `battery_float.compare_verdict(record, recomputed)`.

Residual, stated plainly: a committed file can be rewritten by an operator who also rewrites Git history locally. That is the same class as rewriting the ledger head pin, an operator-only adversary outside the project's threat model; the honest-custody-loss half of M1 and the one-file-deletion half are both closed. To anchor the record outside the machine, the next arm notice names, for every harvested window of the epoch, the recorded status and the sha256 of its verdict file (obligation 10). A-R5b already requires the notice to name non-pass windows; naming the pass windows too is additive.

### 4.5 Decision-log record (exact text, for the magistrate to append below A-R5b's entry)

```
## ACCEPTANCE-25G83-02 amendment A-R5b, binding reading A-R5b-1 (2026-09-25): the harvest verdict is the window verdict

A-R5b-1 (2026-09-25, cold gate HARVEST-VERDICT-FINAL-01, from Opus contract lens finding M1 on PR #423): Under A-R5b "Window verdict" and "Consequences" in `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, a derivation window's battery verdict is the one computed at harvest from raw bytes, before the cadence report, before the count-only dry run and before any B value is read, and recorded in the committed file `configs/calibration/battery_float_verdicts/<session_id>.json` in the same commit as the ledger head pin. That recorded verdict, `pass` included, is final for the window. The issuer's own recomputation from raw bytes is a custody check of the record, not a second decision: a missing or uncommitted record, or any disagreement between the record and the recomputation, refuses issuance and is never an exclusion, never a replacement trigger and never counted toward the one replacement per epoch; restoring the custody bytes byte-exact from the harvest archive, so that the recomputation agrees, is the only cure. A window whose recorded verdict is `battery_float_confounded` or `battery_float_evidence_missing` is excluded and replaced exactly as A-R5b says. The one-replacement bound counts every recorded non-pass window of the epoch, whether or not it holds a valid row. The registration text is unchanged.

Ratification: docs/process_traces/2026-09-25-activation-ed17a643/41-coldgate-packet-harvest-final/20-coldgate-fable-harvest-final-ruling.md §4.
```

### 4.6 Does the A-R5b registration text need a change? No.

- "Window verdict" already fixes the moment of decision: "Before the cadence report, before the count-only dry run and before any B value is read". That is the harvest. The record makes that moment durable; it does not move it.
- "Either verdict is final for that window" covers the two non-pass verdicts; the reading extends finality to `pass` by construction of the record, which the text does not contradict.
- "The issuer computes the verdict itself from raw bytes" is still done, as the check in §4.4.
- A refusal on custody failure is not an exclusion, a top-up or a stop that Revision 5 or A-R5b enumerate; `main` already refuses issuance on a member's custody loss, and Revision 5 nowhere forbids that.
- "The harvest record … name[s] the window, the failing slots, the raw digests and the reasons": the verdict file is that naming, made machine-readable.

An edit would also change the whole-file digest the W1 notice must pin (A-R5b-1's decision-log form is the cheaper instrument, as A-R5a-1 was). I therefore disagree with nothing in the lens on this point and concur with the charge's expectation.

## 5. H3 — The four behaviours

### 5.1 Seat F-1: a slot whose writer died before the post-observation carries no battery obligation. AFFIRM. No change before W1.

A-R5b places the obligation on "every slot of the window that has a finalized ledger row". A killed writer's slot has none: E9 shows `instrument_evidence.json` is written after the post-observation, the seat's test 8 (`tests/test_validate_powermetrics_fiducial_derivation_only.py:600`) kills the real writer at `AFTER_SAMPLER_TEARDOWN` and asserts that no evidence file and no post file exist, and the writer's `abandon` (`validate_powermetrics_fiducial.py:1662-1673`) aborts the session rather than finalizing the slot. The test keeps the ruled branch for any future recovery path that does finalize such a row (`evidence_missing`). The science is unaffected: a slot with no finalized row has no B; a charging excursion confined to that slot's interval touches no member's endpoints; an excursion that reaches a neighbouring slot is caught by that slot's own two observations; and an excursion that begins and ends between two observations is already the disclosed limitation of the rule. The seat's alternative (treat a custody with `pre.ioreg` but no row as `evidence_missing`) would turn every mid-slot writer death into a window exclusion for no gain in member integrity, and I decline it.

### 5.2 Seat F-2: an `UpdateTime` in the future passes. AFFIRM for W1. NIT; tighten in a later amendment with a text change.

The registered predicate reads "`UpdateTime` is no more than 180 s before the observation's wall time". A future stamp is not "before" at all; the parser's `age > MAX_UPDATE_AGE_S` (`battery_float.py:76`) is the exact code of that sentence, so the code matches the registration. Rejecting future stamps is a stricter predicate, which changes which windows are excluded; that is a change to the registered rule, not an extra refusal, and needs the text to read "within 180 s of the observation's wall time". The realistic exposure is small: the wall clock and the gauge stamp derive from the same kernel clock, and a stamp more than a second ahead needs a clock step or a corrupt register, both of which also break the clock anchor that decides validity. Do not amend before W1. Carry `|update_age_s| ≤ 180` into the BFG-S packet as a text-and-code amendment; re-stamp the night-gate green fixture then.

### 5.3 Seat F-6: the issuer enforces the one-replacement bound. AFFIRM; it belongs in the issuer.

`issue_calibration_acceptance_generation.py:1357-1363` refuses when more than one computed non-pass window exists. A-R5b says a second non-pass window "stops the epoch and returns it to council"; a stopped epoch must not issue, and the issuer is the last gate, so the refusal is the mechanical form of the stop. Confirmed. Under §5.4 the count is over recorded non-pass windows of the epoch, not only the computed set, so a zero-valid window counts.

### 5.4 Lens N1: the one-replacement stop is not enforced for a failing window with zero valid rows. REJECT the current behaviour. MATERIAL. Cure lands in BFG-D.

E6 and E7 show the defect is wider than the lens's NIT: a confounded window with no valid row is not merely uncounted, it is omitted from `derivation_notes.battery_confounded_sessions` in the claim-bearing candidate, and the operator cannot declare it. The registered sentence "no confounded window can be omitted" is not held by the code for such a window. No B can be selected through it, so it is not a BLOCKER; it is a disclosure and stop-enforcement defect, MATERIAL.

The lens's cure as written ("every terminal derivation-kind session that has any finalized row in the target epoch") is too wide: the ledger already holds the D-126 sessions of 2026-09-19, whose rows carry the target epoch and predate the `battery_float` key; `validate_window` on them returns `evidence_missing` (KeyError), they would enter the count, and issuance would refuse. The registry (`configs/calibration/observation_dispositions.json`) lists eleven content ids, the valid rows only, so their invalid rows are not registry-disposed either.

**Cure, exact.** The issuer's computed set becomes `registration ∪ A-7 foreign owners ∪ S`, where S is every terminal derivation-kind session owning at least one finalized row of the target epoch, excluding (i) any session that owns a D-126 registry-disposed row, and (ii) any session all of whose finalized rows have an `instrument_evidence.json` that authenticates against its ledger row and lacks the `battery_float` key (a pre-A-R5b window with intact custody). Neither exclusion can be manufactured for an A-R5b window: removing the key breaks the ledger digest, which puts the session back in S; the registry's decision id and mechanism strings are fixed in code and the file is tracked. Every session in S needs a committed record (§4.4); every session in S with a non-pass record must be named in `--battery-confounded-session-id` (the existing exact-set rule now reaches it); the replacement bound counts recorded non-pass windows across S. `battery-verdict` refuses to write a record for a session that exclusion (ii) would exempt, printing `pre-A-R5b session`.

Timing: BFG-D merges before W1 arms (addendum §5.7 item 2), so this lands before W1 by construction; it is required before any issuance and before any second window is armed.

## 6. H4 — Implementation obligations for BFG-D

Line numbers at `06671b69`.

1. **`joulewise/battery_float.py`:** add `VERDICT_SCHEMA = "joulewise.battery_float_verdict.v1"`, `verdict_record(session, *, snapshot, preregistration_sha256, tool_commit, wall_time_s)` building the §4.1 record from `validate_window`, `load_committed_verdict(repo_root, session_id)` doing the three checks of §4.2 (reuse `calibration_ledger.ingest_git_authentication_input`), and `compare_verdict(record, recomputed)` returning the first difference or `None` over status, slot set, and per-slot `verdict`/`pre_raw_sha256`/`post_raw_sha256`/`instrument_evidence_sha256`. One home; nothing else re-implements these.
2. **`scripts/issue_calibration_acceptance_generation.py`, new subcommand `battery-verdict`** (parser next to `check`, `:1902-1906`): flags and refusals of §4.1; write-once; output path `configs/calibration/battery_float_verdicts/<session_id>.json` under `--repo-root`; prints exactly one status line.
3. **`_prepare_candidate` (`:1310-1367`):** compute S per §5.4; require and compare the committed record for every session in the computed set with the refusal texts of §4.4, placed before the exact-set check at `:1337`; count recorded non-pass windows over the computed set for the bound at `:1357`; keep the refusal distinct from exclusion (no change to `session_ids` on refusal). Extend `derivation_notes.battery_confounded_sessions` entries with `verdict_file_sha256`.
4. **`registration_dry_run` (`:176-228`):** for each named Revision 5 terminal session, print `<id>: battery=<status> recorded=<status|absent>`; `blocker:` on absent, uncommitted or disagreeing record; `blocker:` when recorded non-pass windows in the epoch exceed one. Still no value printed.
5. **`scripts/calibration_cadence_report.py` `report_window` (`:47-84`):** after `validate_window`, load the committed record; raise `ValueError` on absence or disagreement; `diagnostic_only` keyed off the recorded status.
6. **`scripts/issue_epoch_continuation.py` `derive_record` (`:86-93`):** same load-and-compare; refuse `battery_float_verdict_missing` or `battery_float_verdict_mismatch: <detail>` with exit 3.
7. **Tests, defect-shaped, at production call sites** (`tests/test_issue_calibration_acceptance_generation.py` `BatteryFloatRevisionFiveTests` and `tests/test_battery_float.py`):
   - (a) M1 closed: build W1, W2 clean; run `battery-verdict` for both and commit; `prepare-candidate W1 W2` → 0; add W2-prime; delete `W2-d03/raw/battery_float.post.ioreg`; `prepare-candidate W1 W2-prime --battery-confounded-session-id W2` → **3** with `cannot be re-established`; `prepare-candidate W1 W2` → 3 with the same text, not `omitted`. Restore the file byte-exact → `prepare-candidate W1 W2` → 3 on A-7 (honest state), proving the refusal cleared.
   - (b) Missing record: W1, W2 clean, records absent → `prepare-candidate` → 3 `missing or uncommitted`; record present but uncommitted → 3; committed → 0.
   - (c) Recorded non-pass agrees: the seat's existing `test_replacement_issues_without_reading_confounded_b_or_a7_refusal` gains a committed W1 record and still issues; recorded non-pass with the raw file later restored so recomputation passes → 3 `cannot be re-established`.
   - (d) N1 closed: the E6 fixture (W1 twelve `ordinary-invalid` rows, charging; W1-prime, W2 clean) with a committed W1 record → `prepare-candidate W1-prime W2` unnamed → 3 `computed non-pass session omitted: W1`; named → 0 with W1 in `battery_confounded_sessions`; add a second non-pass window with a record → 3 `more than one`.
   - (e) Pre-A-R5b exemption: a same-epoch session whose evidence lacks `battery_float` and authenticates is ignored by S and `battery-verdict` refuses it with `pre-A-R5b session`; the same session with its evidence file altered enters S and refuses issuance.
   - (f) `battery-verdict` write-once: second run → 3, file unchanged byte for byte; non-terminal session → 3; wrong registration digest → 3; stdout is exactly one line and contains no `b_fiducial_s`.
   - (g) `registration_dry_run` prints `recorded=absent` and the blocker; `report_window` raises on a missing record and labels from the record; `issue_epoch_continuation` refuses `battery_float_verdict_missing`.
8. **Fixture builder `tests/fixtures/epoch_bootstrap/build.py`:** an option `verdict_records: bool` that runs `verdict_record` per session and commits the files with the terminal pin, so tests exercise the committed path.
9. **Runbook `docs/phase_2/derivation_night_runbook.md`:** one new block §2.2a "Battery verdict, pin commit, cadence report" giving the §4.3 order (i)–(vi) as commands, with the `battery-verdict` invocation, the single-commit `git add` of pin and record, and the cadence report invocation, which has no runbook home today (E8). State that the committed record is the window verdict and that `check` blocks without it.
10. **`docs/process/NIGHT_HANDBACK.md` notice template and the arm record:** the next arm notice names, for every harvested window of the epoch, `<session_id>: battery=<status> verdict_sha256=<64 hex>`.
11. **PR body:** the two statements the addendum §5.3 item 8 requires, plus one line stating that A-R5b-1 is recorded in the decision log and that the harvest verdict file is the window verdict.

The seat's open NEEDS_SCOPE N-1 (the `arm_readiness.py` liveness constant and its census test) is not a question in this packet and is not ruled; the merge gate's green requirement reaches it.

### Plain summary for Ed (5 lines)

1. The reviewer was right: on the new code, if one battery file went missing from a window after the results had been read, that window could be dropped and swapped for a fresh one. On today's main the same loss simply blocks issuance.
2. Fix: at harvest, before anyone looks at a result, the tool writes each window's battery verdict to a small file and commits it with the ledger pin. That file is the verdict, pass included.
3. The issuer still re-checks the raw bytes, but only to confirm the file. Any mismatch blocks issuance until the bytes are restored from the archive; it never drops the window.
4. A confounded window with no valid slots was invisible to the issuer; it will now be counted and disclosed like any other. Three smaller points stand as built for W1.
5. The registration text does not change; one binding reading goes in the decision log, and the code lands in the BFG-D PR before W1 arms.

## 7. Packet hygiene

- Complete and neutral for H1–H4. Both exhibits are labelled arguments; the charge names them so. The lens's executed evidence reproduced under my own runs (E1–E5).
- One asymmetry: the charge frames N1 as a NIT (the lens's tier) while F-6 is framed as a confirmation; the executed E6/E7 show the two are one defect and I re-tiered it. No effect on decidability.
- The charge's expectation that the registration text "should not" change is a stated presumption; I tested it and it holds on the text (§4.6), not on the presumption.
- The charter's expected digest arrived only through the charge (§1). Not a defect of the packet's assembly; recorded as a limitation of the convening.

## 8. Disposition summary

| Question | Verdict | Severity | Lands by |
|---|---|---|---|
| H1 M1 route | AFFIRM, route real | MATERIAL | reading + record + refusing issuer before W1 (BFG-D) |
| H2 cure | Ruled: committed verdict file in the pin commit; issuer refuses on disagreement; A-R5b-1 text issued; registration unchanged | — | BFG-D, before W1 arms |
| H3 F-1 | AFFIRM | NIT (information) | no change |
| H3 F-2 | AFFIRM for W1 | NIT | BFG-S packet, with text amendment |
| H3 F-6 | AFFIRM, belongs in the issuer | — | already at `06671b69`; count widened per §5.4 |
| H3 N1 | REJECT current behaviour | MATERIAL | BFG-D, before W1 arms |
| H4 | eleven obligations, §6 | — | BFG-D |

Where I am silent I concur with the lens's labelled disposition (MERGE for #423, with M1 carried). Where I differ: N1's tier and its cure's scope (§5.4), and the specific home of the record (§4.1).
