# Revision 6 per-window records: the shared interface (orchestrator ruling, session ff50b201, 2026-09-30)

Two JSON records per Revision 6 window connect the producers (the derivation driver, the harvest command) to the consumer (the issuer). Each is write-once, UTF-8, canonical JSON (sorted keys, no trailing spaces), and lives in the window's custody root. Paths inside a record are relative to that custody root. Every digest is the lowercase hex sha256 of the referenced file's bytes. No record carries a B value or any B-derived number (cap council rule R11).

**Locator.** The issuer receives, per session, the path of the window's automated harvest record (`harvest_window.py` output, WI-16). The harvest record names the window's custody root and the two records below by relative path and sha256. The issuer authenticates each record against the harvest record's digest before reading it.

## 1. Start-condition record — `night/start_conditions.json` (producer: `scripts/run_night.py`, derivation path, before the chain-start claim)

```json
{
  "schema": "joulewise.revision6.start_conditions.v1",
  "session_id": "<derivation session id>",
  "plan_id": "<plan id>",
  "result": "admitted | refused",
  "refusal_reason": null,
  "evidence": {
    "a_prior_session_manifest":  {"path": "night/start_conditions_manifest.json", "sha256": "..."},
    "b_network_time_off_receipt":{"path": "night/network_time_off.json", "sha256": "...", "settled_seconds": 612.4},
    "c_agent_census":            {"path": "<gate record>", "sha256": "..."},
    "d_thermal":                 {"path": "<gate record>", "sha256": "..."},
    "e_battery_float":           {"path": "<gate record>", "sha256": "..."},
    "f_launch_context":          {"path": "<launchd probe receipt>", "sha256": "..."},
    "g_clean_dwell":             {"path": "night/prewindow_check.out", "sha256": "...", "script_sha256": "...",
                                   "exit": 0, "passed_epoch_s": 0.0, "deadline_epoch_s": 0.0}
  },
  "written_epoch_s": 0.0,
  "written_monotonic_s": 0.0,
  "boot_id": "<lowercase kern.bootsessionuuid>"
}
```

The letters (a)–(g) follow Revision 6 §6.2 as sealed. If §6.2 names evidence differently for a letter, §6.2 wins and the producer maps its existing file to that letter; a letter with no evidence file makes the record `refused`. A `refused` record means no capture ran: the session is a null session (Revision 6 §0), not a counting window. `a_prior_session_manifest` for the first Revision 6 window points at a manifest with `"prior_revision6_session": null` and a reason.

## 2. Cap-evidence record (rule R9) — `harvest/r9_window.json` (producer: `scripts/harvest_window.py`, using `scripts/cap_replay_harness.py` REPORT mode on each capture)

```json
{
  "schema": "joulewise.revision6.r9_window.v1",
  "session_id": "<derivation session id>",
  "slots": 12,
  "captures": [
    {"slot": 1, "capture_id": "<bundle id>", "content_id": "<sha256 content id>",
     "has_recording": true, "cells": 0, "median_frame_ms": 0.0, "ratio": 0.0,
     "disposition": "<production disposition>", "cap_trigger": null,
     "median_frame_reported": true, "counted": true}
  ],
  "counted": 0,
  "valid": 0,
  "harness_sha256": "<scripts/cap_replay_harness.py sha256>",
  "rule_ref": "CAP-COUNCIL-25G83-01 R9 as amended; Revision 6 §4"
}
```

`counted`, `valid` and every per-capture field are defined by Revision 6 §4 and §7 as sealed; where the sealed text defines a field, it wins over this sketch. `median_frame_reported: false` on any capture triggers STOP-R9-FRAME (Revision 6 erratum F3). The issuer recomputes `counted` and `valid` from `captures` and refuses on disagreement.

## 3. Consumer (issuer, WI-13)

For a Revision 6 campaign the issuer: authenticates both records per session through the harvest record; treats a `refused` start-condition record as a null session; refuses any counting window whose start-condition record is missing, malformed or `refused` while captures exist; applies the count rule and stop lines of the JSON declaration to the sequence of R9 records; never reads B before the last counting window is terminal (Revision 6 §4).

## 4. Amendment T (2026-09-30, orchestrator ruling on WI-13's timing question): explicit window timing evidence

Record-write time never stands in for window timing. Producers supply authenticated timestamps on both clocks:
- **Start** — the start-condition record gains `"chain_start_admitted": {"epoch_s": <float>, "monotonic_s": <float>}`: the instant the driver admits the chain start (after the settle and the dwell both passed), written in the same write-once record. A `refused` record carries `null`.
- **End** — the harvest record gains `"window_end": {"epoch_s": <float>, "monotonic_s": <float>, "source": {"path": "night/chain.exited", "sha256": "..."}}`, read from the chain's exit record (the driver's existing `chain.exited` write), authenticated by digest.
- The issuer computes start times, intervals between windows and gaps only from these fields, same-boot where both clocks are compared (the records carry `boot_id`); across a reboot it uses the wall clock and says so.
