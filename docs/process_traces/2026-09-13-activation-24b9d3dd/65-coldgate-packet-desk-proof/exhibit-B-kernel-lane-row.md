# Exhibit B — kernel row `ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01` at main 3b53478a (verbatim JSON)

```json
{
  "acceptance": {
    "evidence": [
      "docs/process_traces/2026-09-13-activation-24b9d3dd/05-coldgate-packet-night-census-chatgpt/12-opus-pairing-refuter-on-ruling-10.md section 5: the arm-time browser probe (the pgrep alternation over Safari, Google Chrome, Chromium, Firefox and browser automation) matched five always-present Apple XPC services with no browser open; _expect_absent refuses on any match; row t0.no_stray_keepawake is ALWAYS-applicable and required in all three profiles",
      "joulewise/arm_readiness_evidence_t0.py:1720-1735 (_derive_process_census) and scripts/run_night.py:1498-1511 (TRANSACTION_PACK path): the census is evaluated at a pack night's t0 and by the desk tool, not for DIAGNOSTIC_NO_PACK or REHEARSAL_STUB",
      "docs/process_traces/2026-09-13-activation-24b9d3dd/34-coldgate-packet-arm-census-browser-probe/10-coldgate-fable-ruling.md (ruling), 12-opus-pairing-refuter-on-ruling-10.md (A1-A4), 13-magistrate-synthesis-ruling-10-with-opus-amendments.md (adopted; decoy-control addendum); PR #335 merge 58edfa29 (head 7909cf2e); bench run 40; refuter 41; counter-review 42; delta 43; terminal review 44"
    ],
    "pointer": {
      "json_pointer": "/tasks/ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01/acceptance",
      "label": "ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01 acceptance",
      "path": "docs/process/state_kernel.json"
    },
    "summary": "RULED (cold gate packet 34 ruling 10, pairing refuter 12, synthesis 13): the browser probe anchors to real top-level executables (the path fragment /Contents/MacOS/ followed by exactly Safari, Google Chrome, Chromium or firefox and then a space or end of line) and the monitor probe anchors its watch token (watch only at the start of the line or after a slash, followed by a space or end of line); installed in joulewise/arm_readiness_evidence_t0.py with regressions G1-G4 (PR #335). REMAINING for closure, an Ed-hands step (refuter 12 A3): run scripts/author_arm_evidence_t0.py against a TRANSACTION_PACK pack root built from this checkout plus a window-custody root, with no browser open, Claude Code, the Claude and ChatGPT desktop apps and every codex MCP server closed, and no caffeinate running; the emitted t0.no_stray_keepawake source record must show the two new argv with exit 1 and empty stdout. A refusal on an earlier T-0 row is reported, not read as a census failure. G1-G4 prove the patterns; only that run proves the row."
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
  "lane": "ed_external",
  "priority": "p2_next_slice",
  "rank": 193,
  "status": "queued",
  "status_note": "2026-09-13: registered from activation 24b9d3dd after the Opus pairing refuter on cold-gate ruling 05/10 probed the browser argv live. Blocks the first pack night, not the 09-15 DIAGNOSTIC_NO_PACK equivalence night (that class never evaluates the arm-readiness census). Blocked on a ruling; not started. 2026-09-13 (activation 24b9d3dd): RULED and INSTALLED (PR #335, merge 58edfa29); the monitor class was found to share the defect (the bare token watch matched /usr/libexec/watchdogd) and is cured in the same install. OPEN in the ed_external lane pending the Ed-hands desk proof named in the acceptance (a queued external step, not agent work). Recorded limitation: the S-0 clone-proof's 'eleven-kind census PASS' (2026-08-22) established that the census kinds executed and were bound, not that this predicate passed on the current macOS; the real pgrep for this row was only ever bound by a test, never gated, and the August receipt is not on disk in any searched root. Follow-up notes (not lanes): optional -lx caffeinate so a keep-awake refusal records what it saw; the two-character agent token t3 is fragile on principle (no live exposure); Firefox's launchd-parented crashhelper no longer matches; G4's decoy list comprehension precedes its try (a spawn failure could leave one sleep 30 unreaped; delta 43 F1).",
  "stop_card": null
}
```
