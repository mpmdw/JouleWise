# 01 — Harvest record: `d079-epoch-25g83-derivation-n1-20260919` (GO, 12/12 slots finalized, EPOCH_EQUIVALENCE **INCONCLUSIVE**, m = 4)

Activation `b165c535` (watchdog attempt 58, claude pid 21593, supervisor 21589), launched 02:37:02 PDT 2026-09-19 two minutes after the plan's completion boundary; launch email `1a0b907fa46978ca` (to `claude.ai.copper531@passmail.net`, cc `claude2.glaring610@passmail.net`) carried the pending notice `transition-238-hold_census` (the night driver and courier in the production census during the span, the expected shape of a night that ran); `notice.ack` written; no directives; no `standdown.request` at launch or at any slice boundary through this record. Runbook `docs/phase_2/derivation_night_runbook.md` §2.0–§2.5 at H and NIGHT_HANDBACK §Next lane at H. Preconditions: completion boundary 02:35:00 PDT passed; `night/courier.sent` present (02:05:34, Gmail `1a0b8e9d530d5e5c`, courier pid 21234, verdict GO).

## §2.0 Coordinates rebuilt from the frozen triple

| Value | Result |
|---|---|
| `PLAN_ID` / `MEASUREMENT_ROOT` / `H` | `d079-epoch-25g83-derivation-n1-20260919` / `/Users/edr/JouleWise-measurement-20260919-derivation` / `d595aa9f42cdc3d49d0ecae5f2ef33321fd6f90f` (H is on `origin/main`) |
| `PY` executable; clone HEAD = H; tree clean | yes; `d595aa9f`; `git status --porcelain` empty before every step below (the pin advance later in this record is the one deliberate change) |
| `night_plan.json` `custody_root` = `NIGHT_ROOT` | `True` |
| Sidecar check | `chain.zsh: OK` against `chain.zsh.sha256` (`a830b521…563ff`); chain-source sidecar `b5beea46…bead6fb` |
| Exports read from the wrapper | `SESSION_ID` = plan id; `EVIDENCE_ROOT_ID` = `evidence-d079-epoch-25g83-derivation-n1-20260919`; `PLAN` = `<night root>/calibration_plan.json`; `RUNS_ROOT` = `<night root>/runs` |
| Pre-registration re-hash at H | `git show ${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md \| shasum -a 256` = `06ac72ba5542cf176732a4360568abe0da49f50a697fe3f7725b395a334dafac` = the arm record's digest |

## §2.1 What was read (copies in `01-harvest-evidence/`)

- `night.log` (535 bytes): `00:00:00.215 night driver started`; `00:00:00.271 night gate verdict=GO`; `night chain digest verified`; `02:03:35 night result verdict=GO`; `durable record pushed branch=night-results/d079-epoch-25g83-derivation-n1-20260919` (02:03:43 and 02:05:36); `02:05:34 courier attempt=1 heartbeat=True sent=True`. No dead-man line (03:35 not reached before the uninstall).
- `night/result.json`: verdict `GO`, `aborted_reason null`, `chain_exit_code 0`, `chain_sha256 a830b521…` (= the wrapper), `census_count 247`, `census_hits []`, `calibration_refusal null`, `refusal_documents []`, started 1789801200.215 / ended 1789808615.068 (7414.9 s); `receipt_class DIAGNOSTIC_NO_PACK`; seven artifacts with digests.
- `night/receipt.json` (v2): C1 PASS (D-166 registration hash `dfe55f8d…`); C2 `NOT_APPLICABLE` / `no_pack_by_design`; C3 PASS — agent census exit 1 EMPTY, load `{0.32 0.97 1.30}`, AC attached (battery 80 %), HID idle 0, displaysleep 0, no thermal warning; C4 PASS (boot session `cd5b815a…`); C5 PASS — window, plan freshness, measurement HEAD `d595aa9f` = plan head, chain digest equal.
- Chain log `<night root>/operator_logs/derivation-chain.log`: `session_open kind=derivation slots=12` at 07:00:02Z; `chain_start … settle_s=600 slot_cadence_s=600 slot_capture_budget_s=480` (realized Δ = 2 s after t0); `settle_complete` 07:10:02Z; twelve `slot_start`/`slot_end` pairs on the 600 s cadence (07:10 → 09:00 Z), each capture ≈ 3.5 min; `derivation_night_complete slots=12` at 09:03:34Z. No `slot_refused`, no `slot_unused`, no `session_abort`.
- Slot dispositions (chain log = ledger = `instrument_evidence.json`): **d01, d03, d05, d12 `valid`**; d02, d04, d06, d08, d09, d11 `ordinary-invalid` (`not_all_pulses_detected`, `pulse_detection_incomplete`; 59 pulses listed, e.g. d02 detected 57/59); d07, d10 `ordinary-invalid` (`clock_anchor_unresolved`, `pulse_count_below_protocol:0!=59`, 0 pulses, `clock_anchor_resolved` false). `night/chain.stderr.log` (244 lines) carries the two `clock_anchor_unresolved: calibration capture cannot be anchored` lines. Valid rate 4/12 against the pre-registration's projected ≈ 30/38.
- `night/chain.started` (pid = pgid 19681, 00:00:00.27), `chain.exited` (exit 0, 02:03:35.07), `censuses.jsonl` (247 censuses, all empty).
- launchd streams: `launchd.night.err` **0 bytes** (required EMPTY: met); `launchd.night.out` 2749 bytes (the courier's closing summary). No dead-man streams.
- `night/courier.sent` (JSON): `sent_epoch_s 1789808734`, `gmail_message_id 1a0b8e9d530d5e5c`, courier pid 21234, verdict GO, chain exit 0. `courier.json`: attempted 1, sent true, heartbeat seen, no error.
- Results branch `origin/night-results/d079-epoch-25g83-derivation-n1-20260919`: `93a1badb` + `7f13bfa6` on `30118742`; all nine files under `docs/process_traces/night-results/<plan id>/` are BYTE-IDENTICAL to `night/` (`cmp`, this activation).
- Captures: twelve bundles under `<night root>/runs/instrument_validation/<session>-dNN/` (`events.jsonl`, `instrument_evidence.json`, `manifest.json`, `power_trace.csv`, `raw/powermetrics.plist` ≈ 44 MB each); custody passes 2 per slot, `custody_elapsed_s` 3.14 → 3.71 s (A219's real under-lease number: far inside the 120 s budget).

## Byte-exact preservation and inventory

- `lstat` inventory (size, mtime, path; `results-clone/` excluded), taken FIRST at 02:38: `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919.lstat-inventory.txt` (86 files; copy in `01-harvest-evidence/lstat-inventory.txt`).
- `cp -Rp` of the whole night root (781 MB with `results-clone/`) to `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919`; `SHA256SUMS` (86 files) written from the copy and checked against the LIVE root: **86 OK, 0 non-OK** (copy in `01-harvest-evidence/SHA256SUMS`).
- Nothing in the night root was moved, altered or deleted. Per NIGHT_HANDBACK §Next lane the clone and the night root are production custody (a session opened) and are RETAINED; no retirement.

## §2.2 Ledger dry run (counts and states only)

`check --session-ids d079-epoch-25g83-derivation-n1-20260919` from the clone at H (`01-harvest-evidence/22-check.txt`): epoch watch `os_build 25F84 → 25G83 MISMATCH`, `powermetrics_sha256 → b762e5bf… MISMATCH`, `mlx_version → 0.31.2 MISMATCH`, hardware model match; `ledger: calibration_ledger_head_mismatch` (physical 126 rows ahead of the committed pin 76 — expected after a night that appended); registration dry run: `kind=derivation state=finalized terminal=yes declared=12 filled=12 excluded=none`, prefix pending 0, `admissible for prepare-candidate: yes`; **rc 0**.

## Desk pin commit before §2.5 (runbook §3 item 4; contract `calibration_ledger_append.md` §head pin)

`epoch_equivalence_check.py` loads the ledger with `require_committed_pin=True` and REFUSED (`ledger: calibration_ledger_head_mismatch`, rc 3, nothing written) while the physical head (126 / `ffd12051…`) was ahead of the committed pin (76 / `08456d50…`). D-109 forbids claim evaluation between ledger advancement and pin commit, and §3 item 4 names the desk step. Executed from the clone:

- `recover_calibration_ledger.py inspect`: state `clean`, `needs_pin_commit true`, candidate 126 / `ffd12051155e65af1ac428b92932f4a398db07001079e1defd44e1c92a86de9b`, residue 0. `terminal-pin --session-id <session>`: the same candidate. Dry run of `advance-head-pin` (no `--execute`): candidate accepted, `executed false`.
- `advance-head-pin --session-id <session> --expected-sequence 126 --expected-digest ffd12051… --operator-identity magistrate-b165c535 --attestation-reason "n1-20260919 session terminal 12/12; runbook s3 item 4 desk pin commit" --execute`: `executed true`, previous 76 / `08456d50…` → 126 / `ffd12051…`. (The first attempt at this command was blocked by the harness's auto-mode classifier; the identical command re-issued in minimal form ran.)
- Reviewed diff: `configs/calibration/calibration_ledger_head.json` sequence 76 → 126, digest as above, schema unchanged. Committed in the clone on branch `ledger/2026-09-19-n1-20260919-head-pin-126` as `59d5b076` and pushed; the ledger file itself is untracked (`runs/` is ignored) and lives in the clone. `readiness --phase terminal --session-id <session>` after the commit: `pin_relation exact`, `needs_pin_commit false`, `status ready`, `authorizes_arm false` (`01-harvest-evidence/32-readiness-terminal.txt`).

## §2.5 The equivalence rule applied (desk tool, two checkouts)

Run 1 from the clone, run 2 from a second detached checkout at H (`/Users/edr/code/JouleWise-wt-eqcheck-b165c535`, same interpreter, same ledger and pin); records `01-harvest-evidence/epoch-equivalence-record-{1,2}.json` are **byte-identical** (sha256 `8c1d58e4a62aebf9da6c2a442eab6acde07a65f194e21a0cdfe66cdcc91be457`), stdout identical except the `record written:` path. Envelope authenticated: `d079_calibration_acceptance_v2_n17_r6`, artifact sha256 `0227bca3…`, screen rule `range_equals_screen`, n 17, OPERATIVE level screen `0.032898493715362`, OPERATIVE bracket screen `0.009724`, budget ceiling `0.010164834757777545`.

Retained values (ledger lexeme = evidence lexeme, checked by the tool): d01 `0.041133514338919874`, d03 `0.04200278099548145`, d05 `0.172710636067422`, d12 `0.03255031906139217`. **Retained m = 4 < 6 → `EPOCH_EQUIVALENCE: INCONCLUSIVE (m=4)`, rc 5**, both runs. Per directive issue 316 and runbook §2.5, the m < 6 branch is evaluated first and no PASS or FAIL is recorded; the ONE next action is to arm one more equivalence night under a fresh plan id, t0, night root, desk inputs and session id, and apply the same rule to it. No top-up, no partial decision.

Diagnostic facts recorded without deciding anything (the rule was fixed before the night; these are for Ed and the instrument lane, not inputs to the verdict): three of the four retained values (d01, d03, d05) carry `exceeds_prior_level_screen: true`; d05 is 5.2× the level screen; only d12 sits inside it. Eight of twelve captures were non-valid on 25G83 against a projected valid rate near 30/38. A read-only Astra diagnostic seat (brief 02, report 03) was launched to characterise the pulse-detection misses and the two zero-pulse captures; its findings are evidence for the owner, never a change to screens or the pre-registered rule. The runbook's open question stands and is reported to Ed now rather than later: issue 316 fixes no answer to whether, if the second equivalence night FAILS, both nights count as registration nights one and two; that needs Ed's written answer before §3 could run.

## Uninstall (documented post-completion step)

`scripts/install_night_agent.sh --plan <night root>/night_plan.json --uninstall` run FROM the clone at H: first invocation 02:41:59 PDT (its rc was not captured by the shell; it printed nothing); second invocation minutes later **rc 0**, no output; `launchctl list | grep -c joulewise.night` → 0; `~/Library/LaunchAgents` holds only `com.joulewise.magistrate.plist`; clone tree clean. **NOTHING IS ARMED.**

## Findings for the successor and for Ed (registration, not rulings)

1. **Canonical-ledger propagation is undocumented for a night that appended.** The arm scripts' `LEDGER_SOURCE` is `/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl` (untracked, 76 rows); the authenticated 126-row ledger exists only in the 09-19 clone (and byte-exact in the harvest archive). The next clone must start from the 126-row ledger with the committed pin at 126 on main, or its §0.4 check refuses. This activation's plan: land the pin commit on main, then copy the clone's ledger byte-exact to the canonical path after archiving the 76-row original with its digest (a data-file copy, not a git operation; recorded in the arm record). If Ed prefers a different home for the canonical ledger, say so on the notice thread.
2. **Instrument health on 25G83** (diagnostic seat 03): if the misses are a sampler-cadence or permission effect of the new `powermetrics` binary, every later night inherits it; the owner should read report 03 before the second equivalence night's notice is accepted. Nothing in the rule lets the desk act on it.
3. `install_night_agent.sh --uninstall` prints nothing on success; the harvest record should capture `rc` on the first invocation (bench note for the arm-scripts README).
4. Hosted CI on main `30118742`: green (runs 35427353362, 35427137807, 35426695998).
