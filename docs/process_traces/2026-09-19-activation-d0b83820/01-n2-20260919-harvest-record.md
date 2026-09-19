# 01 — Harvest record: `d079-epoch-25g83-derivation-n2-20260919` (GO, 12/12 slots finalized, EPOCH_EQUIVALENCE **FAIL**, m = 7)

Activation `d0b83820` (watchdog attempt 63, claude pid 30921, supervisor 30917), launched 07:37:59 PDT 2026-09-19, three minutes after the plan's completion boundary (07:35:00) and 32 minutes after `night/courier.sent`; launch email `1a0ba1bb8f71f127` (to `claude.ai.copper531@passmail.net`, cc `claude2.glaring610@passmail.net`) carried the pending notice `transition-260-hold_census` (the night chain itself in the production census inside the span, the expected shape of a night that ran; released at event 261 when the census emptied); `notice.ack` written 07:39; no directive issues; no `standdown.request` and no `STOP` at launch or at any slice boundary through this record. Runbook `docs/phase_2/derivation_night_runbook.md` §2.0–§2.5 at H and NIGHT_HANDBACK §Next lane at H. Preconditions: completion boundary passed; `night/courier.sent` present (07:05:47 PDT, Gmail `1a0b9fc98dcd292e`, courier pid 30714, verdict GO, chain exit 0).

Copies of everything quoted below are in `01-harvest-evidence/`.

## §2.0 Coordinates rebuilt from the frozen triple

| Value | Result |
|---|---|
| `PLAN_ID` / `MEASUREMENT_ROOT` / `H` | `d079-epoch-25g83-derivation-n2-20260919` / `/Users/edr/JouleWise-measurement-20260919-derivation-n2` / `22b92ec764f445b01c6e1cc110ca93c6679a27d5` (H is on `origin/main`) |
| `PY` executable; clone HEAD = H; tree clean | yes (`.venv`, Python 3.13.1); `22b92ec7` detached; `git status --porcelain` empty before every step below (the pin advance later in this record is the one deliberate change) |
| `night_plan.json` `custody_root` = `NIGHT_ROOT` | yes (`joulewise.night_plan.v2`, `measurement_head` = `repo_head` = H, `t0_epoch_s` 1789819200, `window_max_s` 9000, `receipt_class DIAGNOSTIC_NO_PACK`) |
| Sidecar check | `chain.zsh: OK` against `chain.zsh.sha256` (`355dc18d…bb51cb`); chain-source sidecar `b5beea46…bead6fb` (= the revision-3 chain source digest) |
| Exports read from the wrapper | `SESSION_ID` = plan id; `EVIDENCE_ROOT_ID` = `evidence-d079-epoch-25g83-derivation-n2-20260919`; `PLAN` = `<night root>/calibration_plan.json` (`PLAN_SHA256` `9ab4776f…`); `RUNS_ROOT` = `<night root>/runs`; `LEDGER_HEAD_PIN` = the clone's `configs/calibration/calibration_ledger_head.json` |
| Pre-registration re-hash at H | `git show "${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md" \| shasum -a 256` = `06ac72ba5542cf176732a4360568abe0da49f50a697fe3f7725b395a334dafac` = the night-one arm record's digest (braced `${H}` as the runbook warns; the unbraced form did eat the colon on the first try and hashed nothing) |
| Identity epoch | `Mac15,9`, `25G83`, `ac_high_power`, `powermetrics_pulse_fiducial_v3`, `sampling_interval_ms 100`, estimator `joint_loss_sublevel_interval_branch_v2` |

## §2.1 What was read

- `night.log` (535 bytes): `05:00:03.807 night driver started`; `05:00:03.861 night gate verdict=GO`; `night chain digest verified`; `07:03:40 night result verdict=GO`; `durable record pushed branch=night-results/…-n2-20260919` (07:03:48 and 07:05:50); `07:05:48 courier attempt=1 heartbeat=True sent=True`. No dead-man line (08:35 not reached before the uninstall).
- `night/result.json`: verdict `GO`, `aborted_reason null`, `chain_exit_code 0`, `chain_sha256 355dc18d…` (= the wrapper), `census_count 247`, `census_hits []`, `calibration_refusal null`, `refusal_documents []`, started 1789819203.808 / ended 1789826620.462 (7416.7 s); `receipt_class DIAGNOSTIC_NO_PACK`; seven artifacts with digests.
- `night/receipt.json` (v2): C1 PASS (D-166 registration hash `dfe55f8d…`); C2 `NOT_APPLICABLE` / `no_pack_by_design`; C3 PASS — agent census exit 1 EMPTY, load `{0.46 0.92 1.27}`, AC attached (battery 80 %, not charging), HID idle 0, displaysleep 0, no thermal warning; C4 and C5 PASS (measurement HEAD `22b92ec7` = plan head, chain digest equal).
- Chain log `<night root>/operator_logs/derivation-chain.log`: `session_open kind=derivation slots=12` at 12:00:05Z; `chain_start … settle_s=600 slot_cadence_s=600 slot_capture_budget_s=480` (realized Δ = 5 s after t0); `settle_complete` 12:10:06Z; twelve `slot_start` lines each answered by one `slot_end`; `derivation_night_complete slots=12` at 14:03:39Z. **No `slot_refused`, no `slot_unused`, no `session_abort`** (grep count 0).
- Slot dispositions (chain log = ledger = `instrument_evidence.json`): **d01, d03, d05, d07, d09, d11, d12 `valid`** (7); d02, d04, d06, d08, d10 `ordinary-invalid` (`not_all_pulses_detected`, `pulse_detection_incomplete`) (5). **No `clock_anchor_unresolved` capture this night** (night one had two). `night/chain.stderr.log` 314 lines, none naming an anchor failure. Valid rate 7/12 against the pre-registration's projected ≈ 30/38.
- `night/chain.started` (05:00:03.86), `chain.exited` (exit 0, 07:03:40.46), `censuses.jsonl` (247 censuses, all empty).
- launchd streams: `launchd.night.err` **0 bytes** (required EMPTY: met); `launchd.night.out` 2126 bytes (the courier's closing summary, which reports the same 7/5 split and that it read no member value). `night-probe.out`/`.err` 0 bytes from the arm. No dead-man streams.
- `night/courier.sent` (JSON): `sent_epoch_s 1789826747`, `gmail_message_id 1a0b9fc98dcd292e`, courier pid 30714, verdict GO, chain exit 0. `courier.json`: attempted 1, sent true, heartbeat seen, no error.
- Results branch `origin/night-results/d079-epoch-25g83-derivation-n2-20260919` = `b4697e6e` (on `d9ec2ad9` on `9edc85fd`); `results-clone` HEAD = the same; all nine files under `docs/process_traces/night-results/<plan id>/` are BYTE-IDENTICAL to `night/` (`cmp`, this activation).
- Captures: twelve bundles under `<night root>/runs/instrument_validation/<session>-dNN/` (`events.jsonl`, `instrument_evidence.json`, `manifest.json`, `power_trace.csv`, `raw/`); custody passes 2 per slot, `custody_elapsed_s` ≈ 4.3 s on d12 (inside the 120 s budget).

## Byte-exact preservation and inventory

- `lstat` inventory (size, mtime, path; `results-clone/` excluded), taken FIRST at 07:40:16: `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919.lstat-inventory.txt` (86 files; copy in `01-harvest-evidence/lstat-inventory.txt`).
- `cp -Rp` of the whole night root (781 MB with `results-clone/`) to `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919`; `SHA256SUMS` (86 files) written from the copy and checked against the LIVE root: **86 OK, 0 non-OK** (`01-harvest-evidence/SHA256SUMS`, `SHA256SUMS-check-against-live-root.txt`). Bench note: the first digest pass listed its own temporary file (written inside the copy before the rename) and reported it unreadable; that line was removed and the check re-run to the 86/86 result above; the digest list also sits inside the copy as `SHA256SUMS`.
- Nothing in the night root was moved, altered or deleted. Per NIGHT_HANDBACK §Next lane the clone and the night root are production custody (a session opened) and are RETAINED; no retirement.

## Uninstall (documented post-completion step)

`scripts/install_night_agent.sh --plan <night root>/night_plan.json --uninstall` run FROM the clone at H at 07:41:02 PDT: **rc 0 on the first invocation** (captured this time; no output, as night one recorded), `launchctl list | grep -c joulewise.night` → 0; `~/Library/LaunchAgents` holds only `com.joulewise.magistrate.plist`; clone tree clean. Done before the 08:35 dead-man minute. **NOTHING IS ARMED.**

## §2.2 Ledger dry run (counts and states only)

`check --session-ids d079-epoch-25g83-derivation-n2-20260919` from the clone at H (`01-harvest-evidence/22-check.txt`): epoch watch `os_build 25F84 → 25G83 MISMATCH`, `powermetrics_sha256 → b762e5bf… MISMATCH`, `mlx_version → 0.31.2 MISMATCH`, hardware model match; `ledger: calibration_ledger_head_mismatch` before the pin advance (physical 176 rows ahead of the committed pin 126 — expected after a night that appended); registration dry run: `kind=derivation state=finalized terminal=yes declared=12 filled=12 excluded=none`, prefix pending 0, `admissible for prepare-candidate: yes`; **rc 0**.

## Desk pin commit before §2.5 (runbook §3 item 4; contract `calibration_ledger_append.md` §head pin)

Executed from the clone, as night one's record did:

- `recover_calibration_ledger.py inspect`: state `clean`, `needs_pin_commit true`, candidate 176 / `0f7609aeaecd9ef191947b91ebb2b7d12bef9fb7bf4b95b690bbedfeaede2512`, residue 0. `terminal-pin --session-id <session>`: the same candidate (= the chain's `ledger_head_pin_candidate` on d12).
- `advance-head-pin` dry run (no `--execute`): candidate accepted, `executed false`, previous 126 / `ffd12051…`. Then `--execute` with `--expected-sequence 176 --expected-digest 0f7609ae… --operator-identity magistrate-d0b83820 --attestation-reason "n2-20260919 session terminal 12/12; runbook s3 item 4 desk pin commit"`: `executed true`, 126 → 176.
- Reviewed diff: `configs/calibration/calibration_ledger_head.json` sequence 126 → 176, digest as above, schema unchanged. `readiness --phase terminal` immediately after refused with `calibration_ledger_head_uncommitted` (the pin must be in Git, not only on disk). Committed in the clone on branch `ledger/2026-09-19-n2-20260919-head-pin-176` as `1278b9f7` and pushed; readiness then `pin_relation exact`, `needs_pin_commit false`, `status ready`, `authorizes_arm false` (`01-harvest-evidence/32-readiness-terminal.txt`). The 176-row ledger file (sha256 `95d152f042bb58db0d5a90c12e1961d77d1bd77101f74c26ffbe1cdaaac85302`, `01-harvest-evidence/ledger-176-sha256.txt`) is untracked (`runs/` is ignored) and lives in the n2 clone and byte-exact in the harvest archive.
- The pin commit is carried onto `main` by this activation's bookkeeping branch (fast-forward of `9edc85fd` through `1278b9f7`), the landing shape night one's pin used.

## §2.5 The equivalence rule applied (desk tool, two checkouts)

Run 1 from the clone at `1278b9f7` (H + the pin commit), run 2 from a second detached checkout at `1278b9f7` (`/Users/edr/code/JouleWise-wt-eqcheck-b165c535`, moved from `d595aa9f`; same interpreter, same ledger file, that checkout's own committed pin); records `01-harvest-evidence/epoch-equivalence-record-{1,2}.json` are **byte-identical** (sha256 `9e73cfd0656afe3d8573887e37df3cdae1a0199e63229ee7e35679d2067ceae6`), stdout identical except the `record written:` path. Envelope authenticated: `d079_calibration_acceptance_v2_n17_r6`, artifact sha256 `0227bca3…`, screen rule `range_equals_screen`, n 17, OPERATIVE level screen `0.032898493715362`, OPERATIVE bracket screen `0.009724`, budget ceiling `0.010164834757777545`.

Retained values (ledger lexeme = evidence lexeme, checked by the tool), all seven `valid+resolved`:

| Slot | `b_fiducial_s` | vs level screen `0.032898493715362` |
|---|---|---|
| d01 | `0.04103035733376445` | above |
| d03 | `0.04337273381948624` | above |
| d05 | `0.028250396657612444` | inside |
| d07 | `0.035576770468514644` | above |
| d09 | `0.03487995875720681` | above |
| d11 | `0.13333095801710004` | above (4.05× the screen) |
| d12 | `0.036897960254235855` | above |

**Retained m = 7 ≥ 6**, so the comparisons are evaluated. LEVEL screen: maximum `0.13333095801710004` (d11) ≤ `0.032898493715362` → **VIOLATED**. BRACKET screen: range `0.105080561359487596` (d11 − d05) ≤ `0.009724` → **VIOLATED**. **`EPOCH_EQUIVALENCE: FAIL (m=7)`, rc 4**, both runs. The tool issued nothing, continued nothing, wrote no addendum, and appended nothing.

Read for the record, deciding nothing: six of the seven retained values sit above the level screen; the bracket screen is exceeded by an order of magnitude (10.8×) even with d11 set aside (range without d11 ≈ 0.015122 s, 1.56× the screen). Night one's four retained values (`0.041133514338919874`, `0.04200278099548145`, `0.172710636067422`, `0.03255031906139217`) show the same shape. Across both nights on 25G83, 10 of 11 retained values exceed the 25F84 corpus maximum. The night-one diagnostic (b165c535 record 03, read-only Astra seat) measured the `powermetrics` sample cadence on 25G83 at a median ≈ 0.244–0.250 s against r6's ≈ 0.120 s under the same 100 ms setting, with a changed anchor-estimator version, and ranked coarser cadence/sample phase first among causes while calling binary-only causation unproven. None of this is an input to the verdict; the rule was fixed before the night.

## The one action the outcome names, and why it goes to Ed instead

Runbook §2.5 and issue 316 §4 on FAIL: the pre-registered three-night derivation proceeds as revision 1 writes it, "THIS night counts as registration night one, so §3 runs for nights two and three". That text was written for a single equivalence night. What actually happened is two equivalence nights: n1-20260919 (INCONCLUSIVE, m = 4, four retained values) and n2-20260919 (FAIL, m = 7). Issue 316 does not say whether an INCONCLUSIVE night's retained observations count toward the registration, and night one's harvest record already flagged that question for Ed before night two ran ("issue 316 fixes no answer to whether, if the second equivalence night FAILS, both nights count as registration nights one and two; that needs Ed's written answer before §3 could run"). The durable pointer for this activation (4ca26e9c → dea50831) fixes the action for exactly this outcome: **email Ed for a written answer; no §3 action.** Under rule 11 a magistrate does not reinterpret a ruling; so §3 has NOT been run, no plan has been authored, nothing is armed, and the question is put to Ed with the arithmetic pre-computed (email sent from this activation; see the RUN_STATE block).

The arithmetic Ed's answer turns on (pre-registration §Stopping: retained n ≥ 19 required for issuance, or exactly 17 under a written ruling; fewer than 19 after the third night → not issued, shortfall recorded, further capture is Ed's ruling; no outcome-driven extra nights):

| Reading | Registration nights so far | Retained so far | Nights still owed by revision 1 | Projected retained after them (at 4/12, 7/12 observed; 5.5/night mean) | Reaches 19? |
|---|---|---|---|---|---|
| (a) both n1 and n2 count (nights one and two) | 2 | 4 + 7 = 11 | 1 | ≈ 16.5 (needs ≥ 8 valid from one night; best so far is 7) | unlikely |
| (b) only n2 counts (night one) | 1 | 7 | 2 | ≈ 18 (needs ≥ 12 valid across two nights) | borderline |
| (c) neither; the instrument question is answered (FAIL) and the derivation route is reconsidered | — | — | — | — | — |

Under either (a) or (b) the projection falls at or below the 19 floor because the 25G83 valid rate (11/24) is far below the 30/38 the pre-registration projected from; a shortfall after the third night is "not issued, shortfall recorded" with any further capture Ed's written ruling — so the answer Ed gives now decides how many nights are spent before that ruling is needed anyway. The magistrate's recommendation, offered not decided: (c) — treat the FAIL as the instrument answer it is (the clock-anchor bound moved by a factor ≈ 1.1–4 and its spread by ≈ 10 on 25G83, with the cadence finding as the leading mechanism), and before spending three more quiet nights on a derivation that the observed valid rate cannot fill, resolve the instrument lane (QUIET-PREDICATE-EVIDENCE-01 / the cadence attribution) so the derivation characterises a stable instrument rather than a moving one. If Ed prefers (a) or (b), the magistrate runs §3 as written from the next quiet slot.

## Findings for the successor and for Ed (registration, not rulings)

1. **Canonical-ledger propagation** (night one's finding 1 stands): the authenticated 176-row ledger exists only in the n2 clone and the harvest archive; the next clone must start from it with the committed pin 176 on main (this activation lands the pin) or its §0.4 check refuses. Copy the ledger byte-exact into the next clone as the n2 arm did (`rsync` + `cmp` + sha256 `95d152f0…`).
2. **`--uninstall` rc captured on the first invocation** this time (rc 0, silent): night one's finding 3 is answered by procedure; the arm-scripts README note remains a bench item.
3. The two equivalence nights are both retained, discoverable, inert roots (09-16, n1-20260919 and n2-20260919 plus their clones): the §0.7 "expect no output" wording versus retention (lane NIGHT-ROOT-RETENTION-DISCOVERY-01, rank 230) now has three instances.
4. Hosted CI on main `9edc85fd`: not re-checked this activation (docs-only landings since `22b92ec7`).

## Addendum (07:58 PDT) — the action taken

Decision email to Ed sent as Gmail `1a0ba221b52d3e38` (to `claude.ai.copper531@passmail.net`, cc `claude2.glaring610@passmail.net`, subject "DECISION NEEDED: equivalence night two FAILED (m=7) — does night one count toward the registration? (a)/(b)/(c)"), carrying the verdict, the seven retained values, the two-night context, the arithmetic table above and the (c) recommendation. Bookkeeping landed on main `2f79e633` (record, evidence, RUN_STATE block, and the pin merge). Hosted CI run 35449733694 on that head was in progress at send time (post-merge confirmation per Ed's 09-16 ruling). Lane 232 fix round 2 launched next (brief 06) as the decision-independent work slice.
