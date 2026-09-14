# Exhibit E — governing text at main 4b9a34111d33a04727a09127a1c1fbd8aab87052

## Contract/runbook lines that define the browser class or the process census
```
docs/phase_2/window_runbook.md:37:- [ ] Close Claude, Codex, browser automation, periodic monitors, and every
docs/phase_2/window_runbook.md:438:- [ ] Close every agent and browser-automation session.
docs/phase_2/window_runbook.md:1119:   agent, browser, `caffeinate`, monitor, maintenance, or other polling
docs/phase_2/window_runbook.md:1732:`caffeinate` is the one reviewed keep-awake process for the window. The T-0
docs/phase_2/derivation_night_runbook.md:2368:| census substring | §1.1b, §5 | The three strings the night's own 30 s process census matches; the generator refuses to bake any of them into an emitted literal. |
```

## Kernel lane ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01
```json
{
 "acceptance": {
  "evidence": [
   "docs/process_traces/2026-09-13-activation-24b9d3dd/05-coldgate-packet-night-census-chatgpt/12-opus-pairing-refuter-on-ruling-10.md section 5: the arm-time browser probe (the pgrep alternation over Safari, Google Chrome, Chromium, Firefox and browser automation) matched five always-present Apple XPC services with no browser open; _expect_absent refuses on any match; row t0.no_stray_keepawake is ALWAYS-applicable and required in all three profiles",
   "joulewise/arm_readiness_evidence_t0.py:1720-1735 (_derive_process_census) and scripts/run_night.py:1498-1511 (TRANSACTION_PACK path): the census is evaluated at a pack night's t0 and by the desk tool, not for DIAGNOSTIC_NO_PACK or REHEARSAL_STUB"
  ],
  "pointer": {
   "json_pointer": "/tasks/ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01/acceptance",
   "label": "ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01 acceptance",
   "path": "docs/process/state_kernel.json"
  },
  "summary": "A written ruling (cold gate or Ed) decides how the arm-time browser class distinguishes a running browser from Apple's always-present Safari XPC services (ancestry- or bundle-aware matching, or a narrowed pattern); the ruled cure is installed in joulewise/arm_readiness_evidence_t0.py with a defect-shaped regression on the recorded live argv (the five service names above must not refuse; a real Safari, Chrome or Firefox process must), and a desk run of scripts/author_arm_evidence_t0.py on this machine with no browser open no longer refuses on t0.no_stray_keepawake."
 },
 "authority": {
  "label": "2026-09-13 activation 24b9d3dd packet 05 synthesis 13 (magistrate registration from pairing refuter 12 section 5; rule change needs a ruling)",
  "path": "docs/process_traces/2026-09-13-activation-24b9d3dd/05-coldgate-packet-night-census-chatgpt/13-magistrate-synthesis-ruling-10-with-opus-amendments.md"
 },
 "dependencies": [],
 "fallback": null,
 "fences": [],
 "flags": [],
 "goal": "Ruling-first: the arm-time process census's browser probe matches Apple's always-present Safari XPC services (SafariBookmarksSyncAgent, SafariPlatformSupport helpers, com.apple.Safari.SafeBrowsing.Service, SafariLaunchAgent, SafariConfigurationSubscriber) even with no browser open, and _expect_absent refuses on any match, so the first TRANSACTION_PACK night would refuse at t0 on this macOS; decide the cure, then install it with a regression on the recorded argv.",
 "id": "ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01",
 "lane": "agent",
 "priority": "p2_next_slice",
 "rank": 193,
 "status": "queued",
 "status_note": "2026-09-13: registered from activation 24b9d3dd after the Opus pairing refuter on cold-gate ruling 05/10 probed the browser argv live. Blocks the first pack night, not the 09-15 DIAGNOSTIC_NO_PACK equivalence night (that class never evaluates the arm-readiness census). Blocked on a ruling; not started.",
 "stop_card": null
}
```

## Pairing refuter 12 §5 (packet 05), verbatim
```
## 5. The browser probe — a live blocker, not just an observation

`_expect_absent` (`joulewise/arm_readiness_evidence_t0.py:1312-1314`) raises
`_underivable` unless `exit_code == 1` **and** stdout is empty, and it is
applied unconditionally to all four probes including `browser` (`:1725`,
`:1728-1729`), producing row `t0.no_stray_keepawake` (`:1731`, deriver bound at
`:1954`). That row is `applicability_rule: ALWAYS` and in the
`required_row_ids` of all three plan profiles ALPHA/BETA/GAMMA
(`configs/arm_readiness/d117_row_registry_v2.json`, verified by parse).

The live browser probe returned rc=0 with `995 …/SafariBookmarksSyncAgent`,
`1457/24791/25700 …SafariPlatformSupport…Helper`, `1794 …Safari.SafeBrowsing.
Service`, `3644 …/SafariLaunchAgent` and more — system XPC services, present
with no Safari window open.

So: **yes, today, for `TRANSACTION_PACK` plans only.**
`author_arm_readiness_evidence_t0` is reached from `scripts/run_night.py:1509`
inside the `is_pack = plan.receipt_class == "TRANSACTION_PACK"` branch
(`:1498-1511`), and from desk entry point `scripts/author_arm_evidence_t0.py:43`
whenever run. `DIAGNOSTIC_NO_PACK` (the 09-15 successor's class) and
`REHEARSAL_STUB` never reach it at t0. Register the lane: the first pack night
refuses on Apple's own Safari daemons unless the browser class is made
ancestry- or bundle-aware.

## 6. What else the ruling gets wrong
```
