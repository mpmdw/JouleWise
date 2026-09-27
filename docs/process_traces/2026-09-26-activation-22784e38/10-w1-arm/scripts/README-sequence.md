# W1 Revision 5 derivation arm: bench sequence (not executed)

The candidate is a fresh v2 `DIAGNOSTIC_NO_PACK` derivation plan with 12 slots,
600 s settle, 600 s pitch, and a 9,000 s window. The candidate triple is
`(d079-epoch-25g83-derivation-w1-<NIGHT_DATE>, /Users/edr/night-custody/measurement/JouleWise-measurement-<NIGHT_DATE>-derivation-w1, __H__)`.
These are preparation scripts, not an arm record. The lead must review each
step, preserve its full output and exit code, and run it from a foreground
session. No script sends mail. Do not run a step before its inputs and earlier
manual acts are complete.

## W1 prerequisites (cold ruling §5.7, in order)

- [ ] PR #418 merged; sealed Revision 5 placeholder check is zero.
- [ ] BFG-D merged to main with the battery-float producer, validator,
  cadence and issuer contracts; canonical checkout fast-forwarded. Because
  BFG-D changes `joulewise/night_gate.py`, the resident magistrate must exit
  so the watchdog's successor arms. Use a fresh supervisor for this arm.
- [ ] A-R5b v1.1 appended below the seal, landed with its decision-log entry;
  pin its whole-file sha256 in `PREREG_SHA256`.
- [ ] Periodic logger gone: `pgrep -fl battery-log` is empty. Scan `ps` for loops running `ioreg` or `pmset`; archive the former logger's JSONL.
- [ ] Two read-only `ioreg -r -c AppleSmartBattery` float observations at least 5 minutes apart, both connected, not charging, within 200 mA of zero current, and with `UpdateTime` no older than 180 s; retain raw values in the arm record.
- [ ] C9 gate runs at discovery and immediately before publication, in addition to BFG-D's code gate.
- [ ] Frozen plan is `configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json`, sha256 `9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072`.

## Run order and manual acts

1. Complete the prerequisites above from the fresh watchdog successor's
   supervisor. At the scripts directory, replace `__H__` with the full
   reviewed post-amendment main SHA, `__T0__` with the approved future
   minute-aligned W1 epoch, and `__PREREG__` with the whole-file A-R5b
   preregistration sha256 in `arm-env.zsh`.
   `NIGHT_DATE` derives from that t0. Keep all scripts together outside the
   measurement clone. Source `./arm-env.zsh` in the bench shell as well,
   since child-script exports do not persist in the parent.
2. Run `zsh step0-discover.zsh`. It checks build 25G83, absence of loaded
   `com.joulewise.night*` labels and plists, and classifies every one-level
   custody plan through `joulewise.evidence_night.retained_roots` (which uses
   watchdog `plan_span_active`). Terminal roots may remain; ACTIVE or UNKNOWN
   stops. It creates the R16 custody parent and opens W1 staging solely to
   retain the first timestamped, raw battery observation in
   `$STAGE/battery-gate.txt`. ExternalConnected must be Yes, IsCharging No,
   signed InstantAmperage within 200 mA of zero, and UpdateTime no older than
   180 s. It records seven additional gauge fields without gating them. A
   refusal postpones the arm; do not change the charge setting as a repair
   in this attempt.
3. Run `zsh step1-clone.zsh`. It requires the R16 clone prefix, remote main
   equals H, detached clean checkout, exact Python lock, byte-equal ledger
   copy, and authenticated ledger head equal to the committed pin.
4. Run `zsh step2-desk.zsh`. Read both epoch-watch reports, including their
   expected rc 3 and the registration sampler's `match`. It checks amended
   Revision 5, the A-R5b heading, PR-L template digests, frozen plan, v2
   authoring, generated wrapper, preflight, schedule, and the two render-only
   plists. Review the
   reported render-context file and the proposed plan before sending notice.
   Record the clone's Spotlight state, display state, powerd assertions,
   brightness, power and load, and quit Wispr Flow at arm per R7.
5. Close foreign and delegated sessions through their own controls. Before
   t0 − 45 min, confirm with `ps` that no interactive Claude session other
   than this magistrate is running; if one is, email Ed and do not arm.
   Run `zsh step3-notice.zsh` to create attempt `000001`,
   exact plan snapshot, empty attempt history, census observations, body and
   unaccepted `notice.json`. Review raw PIDs, descendants, stop channels and
   owner directives. The body is a proposed `NIGHT_HANDBACK` notice.
6. Lead manually sends the generated body through Gmail. Record actual
   acceptance epoch, message ID, thread ID, accepted body/digest/H, readable
   NO relays and any unreadable thread limitation in
   `$ATTEMPT_DIR/notice-evidence.txt`. Fill `notice.json` only from observed
   acceptance and fresh prerequisites/veto checks: replace the three
   placeholders, make the epoch a JSON number, and set the booleans true only
   when justified. Preserve any observed NO on any thread. No reply is needed
   for an accepted notice, but any NO stops publication. A later attempt needs
   a new notice and chronological `attempts.json` under runbook §1.4a.
7. Refresh owner directives, stop files, census and desk checks; then run
   `zsh step4-publish-install.zsh` strictly before t0 minus 10 minutes. It
   repeats the battery gate immediately before publication and appends its raw
   timestamped observation to `$STAGE/battery-gate.txt`; it then calls
   `retry_allowed` on the exact notice and plan snapshot, atomically
   publishes with `os.replace`, runs the real 300-frame launchd probe,
   asserts its v2 receipt, then performs ordinary install from the clone.
   Consent prompts and any probe repeat follow the runbook. The probe is a
   live hardware gate; this script set has never executed it.
8. Run `zsh step5-verify-and-exit.zsh`. Record loaded labels, installed
   calendars and argv, plan/wrapper hashes, probe receipt and the post-install
   `night/` baseline. The lead records the frozen triple, accepted notice,
   R16 prefix, amended registration, protocol-v3 and template digests, rendered
   plist digests, install/probe evidence and harvest pointer in its own arm
   record. The magistrate and all owned agents **exit before t0 minus 8
   minutes**. An announcement does not end a process.

## n1 -> W1 changes

| Change | W1 implementation | Source |
|---|---|---|
| C1 identity and roots | `w1`, unresolved H/t0 placeholders, R16 clone prefix, fresh plan/session/evidence IDs. | Revision 5 §Sample; R16; `night_gate.NightPlan`; `gen_derivation_night.py` inputs. |
| C1 frozen plan | Pins n1's `configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json` by sha256 in desk and notice. | Cold ruling §5.7 item 7. |
| C2 discovery | Removes n1 retirement/moves; classifies sibling plans and checks no loaded/installed night agent, build 25G83; creates only the measurement parent. | `evidence_night.retained_roots`; `magistrate_watchdog.plan_span_active`; R16; PR-L final pass NIT-3. |
| C3 clone | Clones into custody measurement child and asserts prefix; preserves lock, ledger and clean-tree checks. | R16; n1 step 1. |
| C4 desk | Pins the A-R5b whole-file digest and amendment heading, zero unresolved launch-context tokens, both PR-L template digests, render-only `Interactive`, and rc 3/3 with registration sampler match. | Cold ruling §5.7 item 3; Revision 5 §Operating condition; issuer `check()`; PR-L final pass L1; n1 step 2. |
| C5 notice | W1 derivation explanation and R14 sentence, all plan/input/template/protocol/render digests, current local/UTC boundaries and NO instruction; retains attempt snapshot/template. | R14–R15; runbook §1.4–1.4a; Ed directive #417; scout Q2; cold ruling §5.7. |
| C6 publish/install | Fresh-plan `retry_allowed`, atomic publication, actual v2 cadence and `launch_context` fields, probe before ordinary install. No predecessor successor licence helper. | `arm_retry.retry_allowed`; `successor_arm_allowed` is for a terminal zero-capture predecessor; `night_agent_install.validate_probe_receipt`; runbook §1.4. |
| C7 exit | n1 installed-calendar/argv/byte checks with t0-derived exit boundary. | n1 step 5; runbook §1.5. |
| C8 sequence | Adds W1 run order, Gmail IDs, fresh supervisor and exit boundary. | Scout Q4; runbook §1.4–1.5; cold ruling §5.7; seat-4b closure. |
| C9 charge state | Read-only ioreg gate at discovery and immediately before publication, including freshness and recorded gauge fields; raw timestamped evidence in staging; notice and harvest verdict. | Issue #420; cold ruling §5.4–5.5, §5.7. |

## HARVEST CHECK — battery-float window verdict

Before using cadence numbers or running the count-only dry run, invoke the
merged cadence reporter:

```sh
"$PY" -B scripts/calibration_cadence_report.py --calibration-ledger "$CALIBRATION_LEDGER" --session "W1=$SESSION_ID"
```

It calls
`joulewise.battery_float.validate_window` first, authenticating every
finalized slot's `raw/battery_float.pre.ioreg` and
`raw/battery_float.post.ioreg` against `instrument_evidence.json` and the
ledger. Retain the per-slot reasons and raw digests. Only `status=pass` admits
W1's cadence and count checks. For `battery_float_confounded` or
`battery_float_evidence_missing`, keep the diagnostic report, exclude W1
from derivation and replace it once under A-R5b §Replacement, preserving
six-hour spacing. A second non-pass window stops the epoch. At issuance,
name every excluded session with the issuer's repeatable
`--battery-confounded-session-id` flag; its computed set must match exactly.
Neither a stored `passed` flag nor a single `is_charging` field substitutes
for this verdict. The BFG-D implementation must be present before W1 arms.

The `EVIDENCE_ROOT_ID="evidence-$PLAN_ID"` is the n1 convention: generator
code checks that it is census-clean and pins it into the wrapper, with no
other hard-coded value. The runbook still calls for recording its registered
literal at arm.

The existing n1 `step4a-successor-evidence.py` is intentionally absent. It
proves D-182's one-successor licence after a named terminal zero-capture
refusal. W1 is a newly registered derivation window, with no such predecessor
in this plan; its initial attempt uses `retry_allowed(..., [], notice)`.
