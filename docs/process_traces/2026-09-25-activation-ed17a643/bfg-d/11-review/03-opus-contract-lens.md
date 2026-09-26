# BFG-D review: Opus 5.5 contract lens on candidate `df33888f` (base `c6814dd8`)

Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), fresh reviewer, not the implementer. One foreground session, 2026-09-25. No subagents, no background jobs, no launchctl, powermetrics, sudo, installer runs or model inference. One read-only `ioreg` read, which the charge allows. The worktree `JouleWise-wt-ed17a643-bfgd-opus` sits at `6b5efdc3` (= `df33888f` + the charge file). All test runs and mutations ran in `/tmp/ed17a643/bfgd-review/opus-clone`, a clone at `df33888f`, and in `opus-merged`, a merge of that clone with `origin/main` `e9ed7a98`.

## 0. Contamination disclosure

- **Loaded by the harness, not by choice:** the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md` and the auto-memory index `MEMORY.md` (one-line pointers). Index lines that touch this subject: "#421 battery-float gate every window", "Pre-arm triple audit", "sensible gates", "threat-model prune (D-161)". I opened no memory file, no `RUN_STATE.md`, no `TASK_QUEUE.md` and no council log. I cite none of them as authority.
- **Read:** the charge `10-review-charge.md`, the sources `00-…` §3–§6 and `06-…` §3–§4, the lead rulings `03-…`, the seat report `08-…` (verified, not trusted) and the diff `c6814dd8..df33888f`.
- **Repository writes: one side effect.** I ran `git merge-tree --write-tree df33888f origin/main` in the worktree. That command writes a tree object into the shared object store; it changes no ref, index or working-tree file. Everything else ran under `/tmp`.

## 1. Verdict summary

| Tier | Count | Items |
|---|---|---|
| BLOCKER | 0 | — |
| MATERIAL | 1 | M-1: the ruled check 4 (§4.3 item 2) does not close the re-record route when the route goes through a merge. The implementation copies the ruled `git log` command exactly, so this is a defect in the ruled text. End to end, the issuer still refuses. |
| NIT | 8 | N-1 … N-8 |

**Lead bench items.** `ab431280` sets the t0 R1 liveness bound to **610 s, and 610 s is correct.** The 645 s figure applies the 45 s default to a site whose timeout is actually 10 s (§4). `df33888f` adds runbook §1.5 item 6; it conforms to §4.10 item 8.

**Verdict: MERGE.** M-1 should be routed to the magistrate as a text-and-code follow-up that lands before any issuance. That deadline is the one §4.11 item 2 already sets for items 3–5.

## 2. Obligation map (source → implementing line → driving test)

Line numbers are at `df33888f`.

### BATTERY-FLOAT-01 v1.1 §5

| Obligation | Implementation | Test (production call site) | Status |
|---|---|---|---|
| §5.1 probe argv, no shell, 10 s, raw bytes | `joulewise/battery_float.py:18-19,173-177` | `test_battery_float.py:102` (argv, `PROBE_TIMEOUT_S == 10`) | conforms, except that the t0 site runs with 30 s (N-1) |
| §5.1 object count = 1; top-level `"Key" = value` lines only; alias/nested rejection | `battery_float.py:24,91-108` | `:48` (dup, missing, `Amperage`-only, two objects, truncated, nested `ChargingCurrent`, `AppleRawExternalConnected`) | conforms |
| §5.1 signed conversion; reject n ≥ 2^64 and negative lexemes | `:73-84` | `:34` (−158, ±200 pass, ±201 fail) | conforms |
| §5.1 staleness > 180 s → probe error | `:114-118` | `:48,68`; gate `:158` (181 → `night_probe_error`, 179 → pass) | conforms. Negative age passes, as F-2 affirmed for W1. |
| §5.1 recorded-never-gated fields; `Amperage` never substituted | `:119-130` | `:102` | conforms |
| §5.1 one module, injectable runner | `battery_float.observe(runner=…)` | — | conforms |
| §5.2 code in `NIGHT_GATE_REASON_CODES`, `ORDER` after `not_quiet`, `COLD_GATE_CODES` text, `ZERO_CAPTURE_MACHINE_REFUSALS` | `night_gate.py:208,260`; `arm_retry.py:22,37` (text byte-identical to §5.2) | `test_night_gate.py:1587-1611`; `test_arm_retry.py:493` (zero-capture yes, after capture no, `night_probe_error` no) | conforms |
| §5.3-1 `_check_machine` after the AC block, before `PMSET_GENERAL`, both `legacy_load` branches | `night_gate.py:1510-1528` (outside every `legacy_load` branch) | `test_battery_float.py:144` (`evaluate_night` and `evaluate_dynamic_hard`, raw text in C3); probe sequence `test_night_gate.py:1333` | conforms |
| §5.3-2 unconditional `inspect("battery_float")` before `payload_kind` | `evidence_night.py:1364-1374` | `test_evidence_night` `test_charging_fails_arm_check_for_unknown_and_calibration_payloads` | conforms. Mutation M8 kills it. |
| §5.3-3 `publish_install` observation after the successor comparison, before `"publishing"`; journaled; `Refused` | `evidence_night.py:1788-1796` | `test_charging_at_publication_preserves_plan_and_successor_claim` | conforms |
| §5.3-4 `validate_install` predicate before render, `Refused(3)` | `night_agent_install.py:1217-1226` | `test_night_agent_install` / `test_install_night_agent` (+23/+10 lines) | conforms |
| §5.3-5 t0 power row `_fresh_probe`, `_underivable("battery not at float")`, evidence joins | `arm_readiness_evidence_t0.py:1871-1900` | `test_power_row_refuses_charging_and_stale_battery_and_records_float` | conforms |
| §5.3-6 writer pre-observation after `AFTER_CUSTODY_DIRECTORY_CREATION`; post-observation at function scope after the `with` block; neither inside the stamp interval; no new exit path | `validate_powermetrics_fiducial.py:2265-2267` (before `pre_spawn` `:2334`); `:2494-2495` (after `post_parse` `:2491` and the `with` exit); key `:2626` | test 9 `…derivation_only.py:324`; test 8 `:600` | conforms. Mutation M4 kills it. Test 8: see N-2. |
| §5.3-6 manifest and `artifact_sha256` key sets unchanged | no artifact added | `:344-347` | conforms |
| §5.3-7 four consumers | dry run `issuer:223-261`; issuer §4.4; `calibration_cadence_report.py:47-101`; `issue_epoch_continuation.py:86-107` | §4.10 item 4 tests | conforms. `issue_epoch_continuation` is gated only on Rev5 rows, as R1 requires. |
| §5.3-8 / §4.10-10 PR body | — | — | **open.** No PR exists yet (`gh pr list --head feat/2026-09-25-bfg-d` → `[]`). See N-7. |
| §5.4 record schema | `battery_float.py:193-215` | `test_battery_float.py:102` (exact ruled set plus `probe_error`) | conforms |
| §5.5 `validate_window` | `battery_float.py:235-331` | CustodyRuleTests, WindowTests | conforms, as superseded by §4.1 |
| §5.5 issuer contract items 1–6 | see §4.4 below | tests 6, 3(a)–(g) | conforms |
| §5.6 tests 1–11 | all present | test 1 uses a synthetic charging fixture (N-3); test 8's ruled branch is never reached (N-2) | see NITs |

### HARVEST-VERDICT-FINAL-01 v1.1 §4

| Obligation | Implementation | Test | Status |
|---|---|---|---|
| §4.1 E0–E6 order; `CustodyFailure(RuntimeError)` with `failures`, `str` format; slot dict gains three fields | `battery_float.py:40-55,235-331` | `test_battery_float.py:260-330`, (a)–(g) | conforms. M1 kills it. `_is_wall_time` also requires finiteness (seat F-7; a sound tightening, since a NaN age would otherwise pass). |
| §4.2 schema and path | `battery_float.py:376-397`, `:334-338` | 2(a) | conforms |
| §4.2 subcommand: six flags, steps 1–8 in order, `REFUSED:`/exit 3, one stdout line, `open(…, "x")` | `issuer:1329-1420`, parser `:2176-2195`, dispatch `:2311` | 2(a)–(e) | conforms, with one disclosed reading. "It never runs `git`" versus the required `tool_commit`: the tool runs read-only `git rev-parse HEAD` (seat F-4). The text contradicts itself, and this is the only sensible reading. |
| §4.3 checks 1–4, reasons verbatim | `battery_float.py:408-475` | 1(h) `:391-442` | conforms to the letter. M2 kills it. **Check 2 is literal but insufficient: M-1.** |
| §4.3 `compare_verdict` fields, null-aware, `reasons` excluded | `:478-492` | `:442` | conforms |
| §4.4 steps 1–7, order, refusal texts verbatim; A-7 exemption keyed on the computed set; notes fields | `issuer:1520-1597`, `:1681`, `:1930-1943` | 3(a)–(g) | conforms. M6 kills it. |
| §4.4 step 2 S with exemptions (i) and (ii); (ii) never for registration ids | `_battery_computed_set` `:1239-1271` | 3(f) N1 | conforms. M5 survives as an **equivalent mutant**, because `registration_ids` is unioned unconditionally at `:1271`. |
| §4.5 dry run / `report_window` / `derive_record` | `:223-261,312-341`; cadence `:62-79`; continuation `:86-107` | item 4 tests | conforms. `preregistration_sha256=None` in these three is disclosed as seat F-1. The issuer and `battery-verdict` always pass the digest. |
| §4.6 registry pin constant and refusal text | `issuer:469,1205-1219` | `test_acc_25g83_rev5.py:343,348,359` | conforms. M7 kills it. The tracked registry's sha256 equals `ba1ba3fc…` (asserted by the test, and I re-ran it). |
| §4.7 anchor line | `NIGHT_HANDBACK.md` template, runbook §2.2a (v), §1.5 item 6 | `test_docs_freshness` | conforms (N-5: step (v) prints a literal placeholder) |
| §4.8 A-R5b-1 verbatim | `docs/decision_log.md:12213-12219` | executed byte comparison, §3 below | **byte-exact** |
| §4.9 runbook §2.2a; §2.1 row; §2.3 sentence | runbook diff | `test_docs_freshness` | conforms |
| §4.10-6 fixture builder `verdict_records`, `rerecord_verdict` | `tests/fixtures/epoch_bootstrap/build.py` | used by items 2–5 | conforms |
| §4.10-11 pin regression | — | `…derivation_only.py:242`; my own diff check (§3) | conforms |

### Lead rulings `03`

| Ruling | Status |
|---|---|
| R1 applicability keyed on the resolved epoch, never a caller flag | `revision_five = target_epoch == REVISION_FIVE_EPOCH` is read from the rows of the registration sessions, `issuer:1497`. The dry run and continuation key on the rows' `identity_epoch`. A caller-named confounded session under a non-Rev5 registration refuses at the set check. Conforms. |
| R1 historical behaviour unchanged | Non-Rev5 tests (e.g. `test_a_registration_under_another_os_build_is_void`, 25H01) run without records and keep their assertions. Fixture epoch `TARGET_EPOCH` equals `REVISION_FIVE_EPOCH`, so adding `verdict_records=True` to the PrepareCandidateTest fixtures is a fixture update, as R1 anticipates. |
| R1 exact legacy receipt: only the C3 `battery_float` entry and the new probe | `test_night_gate.py:1772-1788`: `legacy_projection` strips exactly the C3 `battery_float` key, the ioreg citation and the ioreg refusal-evidence probe, as it already did for the C5 porcelain addition. Nothing else. Conforms. |
| R2 cadence CLI | `--calibration-ledger` and repeatable `--session` are required; mismatched labels exit 2 through `parser.error`. Conforms. |
| R3 docs scope | ARM-RETRY-POLICY block regenerated with the new row (runbook and handback). Conforms. |

## 3. Executed evidence

**Focused suites at `df33888f`** (clone, foreground, run to completion):
```
tests.test_battery_float tests.test_arm_retry tests.test_calibration_cadence_report tests.test_acc_25g83_rev5
tests.test_night_gate tests.test_validate_powermetrics_fiducial_derivation_only      Ran 213 tests in 218.041s  OK
tests.test_issue_calibration_acceptance_generation tests.test_epoch_continuation
tests.test_arm_readiness_evidence_t0                                                   Ran 275 tests in 554.525s  OK
```

**Merged with current `main` (`e9ed7a98`, #418 sealed the registration file):** `git merge-tree` is clean. On the merged tree:
```
tests.test_acc_25g83_rev5 tests.test_battery_float tests.test_issue_calibration_acceptance_generation
tests.test_calibration_cadence_report                                                  Ran 179 tests in 110.437s  OK
```

**A-R5b-1 byte check.** I extracted the §4.8 code block by program and compared it with the decision-log bytes:
```
block lines 5 sha ad1823ec89af9611ebf23797da8d4c4895f51818db5a154486f59908f2cc95dd
contained verbatim: True occurrences: 1
cand startswith base: True        added == '\n'+block: True
```
The diff to the decision log is exactly one separator newline plus the block. It sits at the end of the file, not "below A-R5b's entry", because A-R5b is not on this branch (seat F-8; N-6). The ratification pointer names `41-coldgate-packet-harvest-final/…`, a path absent from this tree (`git ls-tree … | grep -c` → 0). The text is verbatim as ruled; the path resolves once PR #423's traces land.

**Pin proof (my own).** All four `ESTIMATOR_CODE_PATHS` (`powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, `reduce.py`) are unchanged at the blob level. So are `protocol_v3.json`, `calibration_ledger.py` and `calibration_bracketing.py`. `git diff --name-only c6814dd8 df33888f -- configs` is empty. The writer adds no artifact key, so the test at `:344-347` holds. Two frozen `arm_readiness.sources` pins move:

| Changed file | `arm_readiness.sources` files pinning it |
|---|---|
| `scripts/validate_powermetrics_fiducial.py` | 18 (sanctioned by addendum X2) |
| `joulewise/arm_readiness.py` | **33** (the lead's `ab431280`, not covered by X2) |
| every other changed code file | 0 |

The only code that reads these files is `arm_readiness_evidence.py:46`, the transaction-pack authoring path. The derivation kind never reaches it, so W1 is unaffected (N-7).

**Live probe (read-only ioreg, through the module).** `exit_code 0, object_count 1, ExternalConnected Yes, IsCharging No, InstantAmperage 0, update_age_s 21.9, passed True, AppleRawCurrentCapacity 7591, FullyCharged True`; 11 property lines matched in 17 358 bytes.

**Mutations** (run in the /tmp clone only; each was reverted after its run):

| # | Mutation | Guarding tests | Result |
|---|---|---|---|
| M1 | E3 digest mismatch → `evidence_missing` instead of custody failure | CustodyRuleTests | **killed** (4 failures: a, b, e, g) |
| M2 | drop the single-adding-commit condition of check 2 | CommittedVerdictTests | **killed** (delete-and-re-add, modify-in-place) |
| M3 | night gate ignores a predicate failure | GateTests + `test_battery_float_charging_refuses_at_c3` | **killed** (both gate paths) |
| M4 | writer pre-observation moved to just after `pre_spawn = clock.stamp()` | test 9 | **killed** |
| M5 | exemption (ii) also for registration sessions | issuer module (132) | survived, **equivalent** (registration ids are unioned unconditionally) |
| M6 | A-7 no longer exempts computed non-pass sessions | issuer module | **killed** (4 failures) |
| M7 | registry digest check disabled | `test_acc_25g83_rev5` | **killed** (3 failures) |
| M8 | arm-check battery row replaced by a synthetic pass | charging arm-check test | **killed** (both kinds) |
| M9 | staleness bound 180 → 10^9 | `test_battery_float` | **killed** (6 failures) |

Eight of eight non-equivalent mutants were killed.

**Bypass probes.**
- A caller leaves a confounded zero-valid W1 open to keep it out of S and the bound: closed. Any open session adds `calibration_ledger_bracket_session_open` (`calibration_ledger.py:1732`), and the issuer refuses on `snapshot.refusal_reasons`.
- A caller names a clean window as confounded, or omits a confounded one: refused by the exact-set check (tests 3(f) and 6).
- An appended registry row: refused on the digest (M7).
- A forged record: must equal the recomputation from raw bytes (`compare_verdict`), and raw bytes are custody-pinned through the ledger row. So a forged record can only cause a refusal, never an exclusion, unless code drift makes the recomputation move (see M-1).
- Writer test flags: `--battery-probe-fixture-for-test` requires `--sampler-direct-for-test` with time scale ≠ 1 (`validate_powermetrics_fiducial.py:1894-1901`). The production chain is digest-pinned at t0 (C5), so the flags cannot reach a real slot without a chain-digest refusal.
- `BATTERY_PROBE_RUNNER` is a module global, reachable only in process.
- Recovery: test 8 shows that a writer killed before its post-observation leaves no finalized row (see N-2).

**Fail-closed.**
- `observe` converts every runner or parse exception into `probe_error` (`:186-191`; test `:82`).
- Every site maps `probe_error` to its refusal: `night_probe_error` at t0 through `ProbeError` inside the `try` whose `except` is at `night_gate.py:1679`; `Refused` at the arm check, at publication and in the installer; `_underivable` in the t0 power row.
- The writer records the failure and continues, as ruled.
- git errors: `_git` returns `None`, which becomes `NoRecord`.
- Malformed committed records (non-JSON, duplicate keys, NaN) each end in `NoRecord` (executed; see N-8).

## 4. Lead bench item: t0 R1 liveness bound, 610 s versus 645 s

**610 s is right.** The bound is the sum of the worst-case durations of the post-R1 probe sites plus the ruled 105 s margin.
- Every site runs through `_execute_probe`, which waits `timeout_s` and then `SIGKILL`s the process group (`arm_readiness_evidence_t0.py:444-465`).
- The new twelfth site, the ioreg probe in `_derive_power` (`:1871`), gets `timeout_s = 10` from `_PROBE_TIMEOUT_OVERRIDES` (`:58`, `:444`); `test_power_row_…` asserts `{IOREG: 10}`. The other eleven sites keep 45 s.
- So the worst case is 11 × 45 + 10 + 105 = 610 s.

The "literal" 12 × 45 + 105 = 645 s charges 45 s to a site that cannot run longer than 10 s. That would let an R1 batch 35 s staler than any honest schedule can produce. The census test now derives the constant from the per-site timeouts instead of from a uniform 45 s (`test_arm_readiness_evidence_t0.py:1146-1156`). That is a stronger assertion than before, not a weaker one. The three boundary tests moved from 600 s to 610 s at +1 ns, −1 ns and exact.

`arm_readiness.py` is frozen-pinned in 33 `arm_readiness.sources` files; see N-7.

## 5. Findings

### MATERIAL

**M-1. Check 4 (§4.3 item 2) does not close the re-record route when the route goes through a merge. The implementation is literal; the defect is in the ruled command.**

The ruling says a record is authentic only if "exactly one commit in `HEAD`'s history touches its path". It implements that with plain `git log --no-renames --format=%H -- <rel>`, which applies git's default history simplification. At a merge that matches one parent for the path, that command follows only that parent, so a side branch's re-record hides the honest add. `battery_float.py:439-444` copies the ruled command exactly.

Executed in a scratch repo: main adds the honest `pass` record; a side branch adds an `evidence_missing` record; an ordinary merge resolves the add/add conflict with `--theirs`.
```
honest on main -> pass
git log -- path       : ['6c29037 side: forged record']
git log --full-history: ['ed63cf0 merge side (take theirs)', '46d2faf harvest: honest record', '6c29037 side: forged record']
AFTER MERGE -> accepted, status = battery_float_evidence_missing commit 6c290375
```

**What this does and does not break.**
- End to end, issuance still refuses, because `compare_verdict` requires the record to equal the recomputation from custody-pinned raw bytes. The cure-1 guarantee (custody rule plus compare) holds.
- What fails is the ruling's statement that check 4 "closes the same route independently of the custody clause, so the two cures do not share a failure".
- Check 4 is the only barrier in one case: when the recomputation itself legitimately moves after harvest. Example: the BFG-S `|update_age_s| ≤ 180` change lands before the epoch issues, against §4.11 item 3. Then an honest `pass` record disagrees by design, and the epoch should wait. Through this route an operator can instead commit a matching re-record and silently re-decide a window after B was read.

That needs two faults (the sequencing violation and the merge), so this is MATERIAL, not BLOCKER.

**Suggested cure** (needs a ruling, because the command is ruled text):
- Use `git log --full-history --no-merges --no-renames` for both lists.
- Also require `git show <adding commit>:<rel>` to equal the `HEAD` blob. This catches an "evil merge" that rewrites the file inside the merge commit.

I ran the current implementation and the cure over four histories:
```
honest linear  | impl: record status=pass                         | cure: record
honest merge   | impl: record status=pass                         | cure: record
forged side    | impl: record status=battery_float_evidence_missing | cure: NoRecord (2,2)
evil merge     | impl: NoRecord: … (2 commits, 1 adding)           | cure: NoRecord (blob differs from adding commit)
```
The cure keeps both honest routes (linear and `--no-ff` merge) and rejects both hostile ones. It costs about five lines plus one test that builds these histories. Land it before any issuance: §4.11 item 2 already forbids issuance before items 3–5 are on `main`, so the fix does not hold W1.

### NIT

**N-1. The t0 ioreg probe runs with the night gate's 30 s runner timeout, not the ruled 10 s (§5.1).**
- `night_gate._check_machine` runs the probe through `probes.run`. In production that is `run_night._probe_runner` with `PROBE_TIMEOUT_S = 30` (`scripts/run_night.py:64`).
- On timeout that runner returns exit 124, so the record shows `timed_out: false` and `exit_code: 124`.
- Every other site honours 10 s: the arm check and publication pass `timeout=10`, the installer uses `observe`'s own `subprocess.run`, and the t0 power row uses the override.
- The outcome is fail-closed either way. The deviations are a slower t0 refusal and a less accurate `timed_out` field.
- Cure: pass a timeout through `Probes.run` for this argv, or document the exception.

**N-2. Test 8 never exercises its ruled assertion.**
- I instrumented the test in the clone. It takes the "no finalized row" branch: `TEST8-BRANCH: no-finalized-row aborted {}`. The `battery_float_evidence_missing` branch never runs end to end.
- The outcome is safe: a slot with no finalized row carries no obligation and no B.
- The ruled sentence ("followed by recovery finalization, yields `battery_float_evidence_missing`") is proven only through the unit path (E0/E2 tests), not at the production recovery call site.
- Either state in the PR that recovery never finalizes such a row, or add a recovery route that does.

**N-3. Test 1's charging fixture is synthetic.** `charging-synthetic-from-real.ioreg` is the real float capture with two lines edited (`IsCharging` No→Yes, `InstantAmperage` 0→739). The ruling asked for a real-format fixture captured while charging. The README discloses the edit, and the parser reads only top-level lines, so the risk is low. If the machine is ever seen charging again, capture a real one.

**N-4. Test-mode stamping of `UpdateTime`.** In `test_night_gate`, the green float fixture keeps `UpdateTime = 1790373525` against `now = 1005`, so its age is hugely negative and it passes only because of the F-2 allowance. Freshness in the green path is therefore not exercised there; it is covered separately by `GateTests.test_stale_is_probe_error_and_fresh_passes`. There is no defect; I record it so a later BFG-S `|age|` change expects these fixtures to break.

**N-5. Runbook §2.2a step (v) prints a literal placeholder.** `print -r -- "$SESSION_ID: battery=<pass|confounded|evidence_missing> …"` emits the angle-bracket text verbatim. The operator must substitute the status by hand from step (iii)'s stdout. Capturing (iii)'s line into a variable would make the notice line exact.

**N-6. Decision-log placement.** A-R5b-1 is byte-exact but appended at the end, after A-R5a-1, because A-R5b is on PR #423. Per §4.8 ("appends it below A-R5b's entry"), the magistrate must reorder when #423 lands. The ratification path `41-coldgate-packet-harvest-final/…` does not resolve on this branch until then.

**N-7. The PR body has not been written yet, and it should name `arm_readiness.py`.** No PR exists. It must carry the §5.3 item 8 statements and the §4.10 item 10 sentence. The X2 statement names only `scripts/validate_powermetrics_fiducial.py` (18 pins). BFG-D also moves `joulewise/arm_readiness.py`, which is pinned in 33 `arm_readiness.sources` files. The BFG-S re-freeze must cover both, so the PR body should name both files.

**N-8. `ingest_git_authentication_input(grammar="json")` does not reject malformed JSON.** Executed, each committed in a fresh repo: non-JSON → `NoRecord: identity mismatch: schema`; duplicate `schema` keys → `NoRecord: identity mismatch: session_id`; NaN → `NoRecord: identity mismatch: schema`. The ingest step passes all three bytes through. Every case still fails closed through the identity checks, and `compare_verdict` governs the outcome. But a duplicate-key record with otherwise valid identity would be read last-key-wins. Optional hardening: require the committed bytes to equal `render_verdict(json.loads(bytes))`.

## 6. Changed expected values in pre-existing tests (audited)

Each item below is either the ruled change or an index or setup shift. **No pre-existing assertion was weakened.**

- `test_battery_float.py:198` (A10): `evidence_missing` → `CustodyFailure`. This is ruled in §4.10 item 1(b); the `post=None` assertion is unchanged.
- `test_issue_calibration_acceptance_generation.py` dry-run template: every original line assertion is kept, with indices shifted by one for the new `battery=pass recorded=pass` line (`lines[2..6]` → `lines[3..7]`, plus the new `lines[2]`). The tampered-raw half becomes `CustodyFailure`, as §4.10 item 4 rules.
- `test_acc_25g83_rev5.py`:
  - both `invalid or duplicate` assertions are unchanged, now reached with the pin patched to the copy's own digest;
  - the empty-registry case adds a `digest mismatch` assertion and keeps the original A-7 assertion under the patched pin;
  - the sealed-text computation moved above the fixture, with identical text.
- `test_arm_readiness_evidence_t0.py`:
  - 600 → 610 s in the three boundary tests (§4);
  - site count 11 → 12, with the formula now per-site.
- `test_night_gate.py`:
  - the probe sequence gains `IOREG_BATTERY_ARGV` after `PMSET_BATT_ARGV`, as §5.3 item 1 rules;
  - the ORDER loop gains index 7 (the charging fixture), with boot moved to `index > 8`;
  - the legacy projection strips only the ruled C3 addition (R1).
- `test_arm_retry.py`: `COLD` gains the new code.
- `test_epoch_continuation.py`: the unanimity assertion is unchanged, now run on 25G99. On 25G83 the battery gate refuses first, and that case is added as a third subtest (seat item 6).
- `test_calibration_cadence_report.py`: the calls gain the R2-required `ledger`/`session_id` arguments; the `STOP` assertion is unchanged.
- `test_evidence_night.py`, `test_gen_evidence_night.py`, `test_evidence_arm_sequence.py`: runner setup only (the float fixture for the ioreg argv); no assertion changed.
- `custody_read_replay_allowlist.json`: insert-only, two rows.

## 7. Verdict

**MERGE.**
- No BLOCKER.
- Every §5 and §4 obligation is implemented at its named production site, and its test drives that site. Eight of eight non-equivalent mutations are killed.
- The pin proof holds, and the candidate merges cleanly with current `main` and stays green there.
- 610 s is the correct liveness bound.

Route M-1 to the magistrate as a ruled text-and-code follow-up that lands before any issuance. Record N-1 through N-8 in the PR body or the lane, and write the PR body per N-7 before merging.
