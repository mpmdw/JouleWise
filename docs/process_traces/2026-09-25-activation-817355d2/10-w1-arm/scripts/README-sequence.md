# W1 Revision 5 derivation arm: bench sequence (not executed)

The candidate is a fresh v2 `DIAGNOSTIC_NO_PACK` derivation plan with 12 slots,
600 s settle, 600 s pitch, and a 9,000 s window. The candidate triple is
`(d079-epoch-25g83-derivation-w1-<NIGHT_DATE>, /Users/edr/night-custody/measurement/JouleWise-measurement-<NIGHT_DATE>-derivation-w1, __H__)`.
These are preparation scripts, not an arm record. The lead must review each
step, preserve its full output and exit code, and run it from a foreground
session. No script sends mail. Do not run a step before its inputs and earlier
manual acts are complete.

## Run order and manual acts

1. Merge and review the Revision 5 seal on main. At the scripts directory,
   replace `__H__` with the full reviewed post-seal main SHA and `__T0__`
   with the approved future minute-aligned W1 epoch in `arm-env.zsh`.
   `NIGHT_DATE` derives from that t0. Keep all scripts together outside the
   measurement clone. Source `./arm-env.zsh` in the bench shell as well,
   since child-script exports do not persist in the parent. Resolve the
   frozen calibration-plan source ruling below before step 2.
2. Run `zsh step0-discover.zsh`. It checks build 25G83, absence of loaded
   `com.joulewise.night*` labels and plists, and classifies every one-level
   custody plan through `joulewise.evidence_night.retained_roots` (which uses
   watchdog `plan_span_active`). Terminal roots may remain; ACTIVE or UNKNOWN
   stops. Its only mutation is creating the R16 custody parent.
3. Run `zsh step1-clone.zsh`. It requires the R16 clone prefix, remote main
   equals H, detached clean checkout, exact Python lock, byte-equal ledger
   copy, and authenticated ledger head equal to the committed pin.
4. Run `zsh step2-desk.zsh`. Read both epoch-watch reports, including their
   expected rc 3 and the registration sampler's `match`. It checks sealed
   Revision 5, PR-L template digests, frozen plan, v2 authoring, generated
   wrapper, preflight, schedule, and the two render-only plists. Review the
   reported render-context file and the proposed plan before sending notice.
   Record the clone's Spotlight state, display state, powerd assertions,
   brightness, power and load, and quit Wispr Flow at arm per R7.
5. Close foreign and delegated sessions through their own controls. Ping
   interactive seat `joulewise-4b` **at least 45 minutes before t0** and have
   it close before t0. Run `zsh step3-notice.zsh` to create attempt `000001`,
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
   calls `retry_allowed` on the exact notice and plan snapshot, atomically
   publishes with `os.replace`, runs the real 300-frame launchd probe,
   asserts its v2 receipt, then performs ordinary install from the clone.
   Consent prompts and any probe repeat follow the runbook. The probe is a
   live hardware gate; this script set has never executed it.
8. Run `zsh step5-verify-and-exit.zsh`. Record loaded labels, installed
   calendars and argv, plan/wrapper hashes, probe receipt and the post-install
   `night/` baseline. The lead records the frozen triple, accepted notice,
   R16 prefix, sealed registration, protocol-v3 and template digests, rendered
   plist digests, install/probe evidence and harvest pointer in its own arm
   record. The magistrate and all owned agents **exit before t0 minus 8
   minutes**. An announcement does not end a process.

## n1 -> W1 changes

| Change | W1 implementation | Source |
|---|---|---|
| C1 identity and roots | `w1`, unresolved H/t0 placeholders, R16 clone prefix, fresh plan/session/evidence IDs. | Revision 5 §Sample; R16; `night_gate.NightPlan`; `gen_derivation_night.py` inputs. |
| C1 frozen plan | Keeps n1's committed `configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json` pending lead ruling. | Runbook §0.2 says a frozen campaign-pack `calibration_plan.json`; Revision 5 and R1–R17 name no exact source; generator requires readable JSON `plan_id` but does not select a pack. |
| C2 discovery | Removes n1 retirement/moves; classifies sibling plans and checks no loaded/installed night agent, build 25G83; creates only the measurement parent. | `evidence_night.retained_roots`; `magistrate_watchdog.plan_span_active`; R16; PR-L final pass NIT-3. |
| C3 clone | Clones into custody measurement child and asserts prefix; preserves lock, ledger and clean-tree checks. | R16; n1 step 1. |
| C4 desk | Pins sealed Revision 5 digest and zero unresolved launch-context tokens, both PR-L template digests, render-only `Interactive`, and rc 3/3 with registration sampler match. | Seal `23dd9909`; Revision 5 §Operating condition; issuer `check()`; PR-L final pass L1; n1 step 2. |
| C5 notice | W1 derivation explanation and R14 sentence, all plan/input/template/protocol/render digests, current local/UTC boundaries, `joulewise-4b` close and NO instruction; retains attempt snapshot/template. | R14–R15; runbook §1.4–1.4a; Ed directive #417; scout Q2. |
| C6 publish/install | Fresh-plan `retry_allowed`, atomic publication, actual v2 cadence and `launch_context` fields, probe before ordinary install. No predecessor successor licence helper. | `arm_retry.retry_allowed`; `successor_arm_allowed` is for a terminal zero-capture predecessor; `night_agent_install.validate_probe_receipt`; runbook §1.4. |
| C7 exit | n1 installed-calendar/argv/byte checks with t0-derived exit boundary. | n1 step 5; runbook §1.5. |
| C8 sequence | Adds W1 run order, Gmail IDs, seat ping and exit boundary. | Scout Q4; runbook §1.4–1.5. |

**Frozen plan ruling needed before execution.** Neither Revision 5, the
acceptance rulings nor the generator identifies the precise W1 campaign-pack
file. The retained n1 choice is a reviewable draft, not a registered W1 input.
Confirm the exact committed path and digest before `step2-desk.zsh` copies it;
if different, update `FROZEN_PLAN_REL` and re-review the script set. The
`EVIDENCE_ROOT_ID="evidence-$PLAN_ID"` is also the n1 convention: generator
code checks that it is census-clean and pins it into the wrapper, with no
other hard-coded value. The runbook still calls for recording its registered
literal at arm.

The existing n1 `step4a-successor-evidence.py` is intentionally absent. It
proves D-182's one-successor licence after a named terminal zero-capture
refusal. W1 is a newly registered derivation window, with no such predecessor
in this plan; its initial attempt uses `retry_allowed(..., [], notice)`.
