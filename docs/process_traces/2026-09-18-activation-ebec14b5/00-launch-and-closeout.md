# Activation ebec14b5 — launch and close-out (2026-09-18 23:41–23:5x PDT)

Launched 2026-09-18 23:41:17 PDT (claude pid 19259, supervisor 19255, watchdog attempt 56) after activation 0be12980 exited voluntarily by ≈23:48 wall-clock expectation but in fact at ≈23:40 (`state.json` `last_exit_class` again the stale `usage_exhausted` label; `transition_seq` 231). Heartbeat written 23:41:25 (pid 19309 = the heartbeat shell); launch email `1a0b866ad80c8466` sent 23:43 to `claude.ai.copper531@passmail.net` (cc `claude2.glaring610@passmail.net`); `notice.ack` written 23:42:49. Pending notices: none. Open directive issues: none. `standdown.request` and `STOP`: absent at launch and at every slice boundary.

## State found

- Night `d079-epoch-25g83-derivation-n1-20260919` ARMED and untouched: t0 00:00:00 PDT 09-19 (epoch 1789801200; 1090 s away at 23:42), measurement root `/Users/edr/JouleWise-measurement-20260919-derivation` at `d595aa9f`. `launchctl list`: `com.joulewise.night`, `com.joulewise.night.deadman`, `com.joulewise.magistrate` loaded, last exit 0. Plan directory intact (`night_plan.json`, `chain.zsh` + digests, `identity-epoch.json`, `t1-bindings.json`, probe receipt).
- Canonical root `/Users/edr/code/JouleWise` clean at `422cdebb`, not touched. `origin/main` at `bda96f0e` (0be12980 bookkeeping head).
- Worktrees: `JouleWise-wt-harness-232` (`498ad1d0`, lane 232 branch), `JouleWise-wt-mag-e82f29ac` (this commit's worktree, branch `bookkeeping/2026-09-18-activation-c289a087`, at `bda96f0e` = main).

## Decision this slice

t0 was 19 minutes from launch and the resident ladder TERMs the magistrate at t0 − 6 min (23:54). Same reasoning as c289a087 and 0be12980: no Codex or Fable child was started (it would sit in the t0 census and refuse the night); bookkeeping only; voluntary exit before 23:54. No children to stop; no `[QUIET-MAC]` work touched. Fourth consecutive ≈25-minute pre-t0 relaunch (attempts 53–56); the cadence is the watchdog's usage-backoff timer, not a defect in the night. Observation for the successor's lane list, not a rule proposal: the watchdog labels every voluntary exit `usage_exhausted`, so its 25-minute cadence is a mislabel of a deliberate pre-t0 park; a quiet-hold state for "armed night within N minutes" would stop these no-op activations (candidate lane; needs Ed or the cold gate under rule 11).

## Successor's next exact action (after 02:35 09-19 and `night/courier.sent`)

Unchanged from the e82f29ac block: (1) harvest per the d8ca3a36 block, uninstall both night agents from the clone, `epoch_equivalence_check`; (2) lane 232 fix round 2 as a seat per `2026-09-18-activation-e82f29ac/01a` §3 + §5 + §6 (WRITE_SCOPE = the one test file), six-mutation bench acceptance, delta re-audit round 3 naming BOTH signatures, then the PR gate; (3) lane 232 stage A evidence only from a non-agent context. A successor that launches before t0 with under 40 minutes to go should again do bookkeeping only and exit. A successor that launches AFTER t0 but before 02:35 (during the night's span) must not start any seat either: the night is measuring; do the heartbeat, email, ack, and exit.
