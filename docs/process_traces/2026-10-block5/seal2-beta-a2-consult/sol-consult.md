```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Recurring indexing and media maintenance plausibly caused the admission-loss cluster; recommend bounded pre-workload admission waiting before attempt 3.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "0699abbb0881ce64b39c46ba07de568cc3848260",
    "head_end": "0699abbb0881ce64b39c46ba07de568cc3848260",
    "upstream_end": "0699abbb0881ce64b39c46ba07de568cc3848260",
    "branch": "lane/2026-10-10-harvest-screen-sources"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "Probable: recurring indexing and media maintenance overlapped idle admission and exhausted its retry.",
    "remediation": "Proposed: retain the physical limits and add bounded admission waiting before workload execution through a cold erratum and new seal."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nimport json,plistlib\nfrom pathlib import Path\np=Path('/Users/edr/night-custody/v5-b5-beta-a2-20261010T1756Z/hazards/monitor/contention.jsonl')\nr=[json.loads(s) for s in p.open()]\nassert len(r)==895 and sum(x['kind']=='interval' for x in r)==892\np=Path('/System/Library/LaunchAgents/com.apple.mediaanalysisd.plist')\nv=plistlib.loads(p.read_bytes())['LaunchEvents']['com.apple.bg.system.task']['com.apple.mediaanalysisd.background.scheduler']\nassert v['RepeatingTask']['Interval']==3600 and v['RequiresUserInactivity'] is True\nprint('inspection passed')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["inspection passed"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^inspection passed$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Unified-log and process-list queries were sandbox-blocked; the exact dispatched maintenance task and member-specific admission condition remain unresolved.",
      "needs": "Lead may query machine records without changing permissions."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The recommendation is a prospective design change, not an implemented or hardware-verified cure.",
      "needs": "Magistrate adjudication and the required cold erratum and seal."
    }
  ]
}
```

## Cause

**The busy cluster was indexing/intelligence work followed by media analysis, not another observed malware scan.** Its connection to the four admission aborts is probable, not individually proved.

Journal:

`/Users/edr/night-custody/v5-b5-beta-a2-20261010T1756Z/hazards/monitor/contention.jsonl`

Counting convention: assign an interval by its ending wall timestamp; “inside” is `[12:30,13:05)` PDT. Count each process name once per interval from `outside_over_limit`. That field already includes exited-process carry-forward; adding `exited_over_limit` again would duplicate entries (`joulewise/hazards/contention.py:381–385,415–421`).

The journal has **895 lines and 892 intervals**. Inside comprises lines **544–753**, **210 intervals**, of which **70** are dirty. Outside has **682 intervals**, **62** dirty.

| Journal process name | Inside | Outside |
|---|---:|---:|
| mediaanalysisd | 25 | 23 |
| spotlightknowled | 18 | 0 |
| corespotlightd | 15 | 20 |
| WeatherWidget | 7 | 6 |
| duetexpertd | 3 | 2 |
| mobileassetd | 3 | 1 |
| knowledgeconstru | 2 | 0 |
| SiriSuggestionsL | 2 | 0 |
| siriinferenced | 2 | 0 |
| mds_stores | 2 | 1 |
| modelcatalogd | 2 | 1 |
| AppleIntelligenc | 1 | 0 |
| ModelCatalogAgen | 1 | 0 |
| contactsd | 1 | 0 |
| fileproviderd | 1 | 0 |
| firefox | 1 | 0 |
| launchd | 1 | 0 |
| milod | 1 | 0 |
| plugin-container | 1 | 0 |
| PerfPowerService | 1 | 4 |
| opendirectoryd | 1 | 1 |
| runningboardd | 1 | 5 |
| spindump | 1 | 2 |
| 2.1.296 | 0 | 1 |
| ControlCenter | 0 | 1 |
| TGOnDeviceInfere | 0 | 1 |
| WallpaperAerials | 0 | 1 |
| WhatsApp | 0 | 2 |
| WindowServer | 0 | 2 |
| loginwindow | 0 | 1 |
| networkservicepr | 0 | 2 |
| passd | 0 | 1 |
| photolibraryd | 0 | 2 |
| routined | 0 | 1 |
| secd | 0 | 1 |
| syspolicyd | 0 | 1 |

Names are the journal’s accounting names, which can truncate distinct executables (`joulewise/hazards/contention.py:42–46`).

The sequence matters:

- **12:35:** `corespotlightd` at line **575**, followed by Firefox/plugin activity at **578** and another indexing interval at **580**.
- **12:53–12:57:** `corespotlightd`, `fileproviderd`, Spotlight knowledge and model-catalog activity at **685**; asset/Siri activity at **689–691**; `knowledgeconstru` at **701–702**; `milod` at **704**.
- **12:57–13:00:** newly started PID **84727**, accounting name `spotlightknowled`, appears above limit in **16 intervals**, lines **711–726**. It is distinct from resident updater PID **756**, responsible for the interval at **685**.
- **13:01–13:05:** `mediaanalysisd` is above limit in **24 consecutive intervals**, lines **730–753**. Its remaining inside interval is **706**.

The supplied abort start minutes are consistent with these overlapping phases, including work starting after the recorded start minute. They do **not** establish the exact threshold breached in each baseline.

The admission path measures a first baseline, applies one backoff and second attempt, then aborts on continued failure (`joulewise/controller.py:1945–1973,1991–2002`). CPU admission evaluates directly measured CPU-busy and combined-power thresholds (`joulewise/idle_admission.py:435–440`). Thus the monitor tally identifies competing work; it is not itself the member’s admission verdict.

For comparison, BETA-1’s permitted journal has **2,155 lines / 2,152 intervals**, including **77** over-limit intervals named `XProtectRemediat`, **76** `mediaanalysisd`, and **11** `corespotlightd`. BETA-2 has **zero** intervals named `XProtectRemediat` across its **892** intervals.

## Recurrence

**Recurring maintenance is established; the precise dispatch and next execution time are not.**

Read-only `launchctl print` shows:

- `gui/501/com.apple.spotlightknowledged`: daily repeating knowledge, journal and inference tasks with `Interval=86400`; several require external power, and one requires network connectivity. This is scheduling eligibility, not a fixed local clock appointment.
- `gui/501/com.apple.mediaanalysisd`: an hourly background scheduler, `Interval=3600`, minimum spacing `2900`, requiring user inactivity. The installed plist confirms this at `/System/Library/LaunchAgents/com.apple.mediaanalysisd.plist:15–33`. Its live record also contains separately submitted nonrepeating analysis tasks and daily maintenance tasks.
- `gui/501/com.apple.corespotlightd`: repeating two-hour and daily tasks, plus notification and IPC triggers.

`launchctl print gui/501` reports media analysis, photo analysis and Core Spotlight **disabled**, while their individual service records still report **running**. The existing disable records therefore do not demonstrate removal of the current processes.

These records support recurrence during a display-asleep, plugged-in window. They do not identify which scheduled task produced the observed burst, whether that task completed, or an interval anchored to its last successful run. `/usr/bin/log show` was sandbox-blocked; I did not bypass that restriction.

## Recommendation

**(c). Do not arm attempt 3 unchanged on the assumption that this maintenance was a one-off.**

1. Make a prospective cold erratum for **bounded reacquisition of a physically acceptable idle baseline before workload execution**, retaining the present physical thresholds.
2. Keep the committed science order and unit count. Preserve every unsuccessful admission probe and its reason. Permit another baseline only while no workload has executed for that member; never overwrite a failed bundle or retry measured science based on its outcome.
3. Bound admission waiting by a registered budget compatible with the chain’s remaining horizon. Continuing physical failure at that bound retains its failure consequence; mere recording defects remain flags.
4. Implement through the required review, new seal and new measurement clone before attempt 3.

The relevant seam is the two-attempt admission path at `joulewise/controller.py:1945–2002`. Missing-evidence-only conditions already receive flag treatment, while threshold conditions retain retry/abort behavior (`joulewise/controller.py:2101–2125`). Preserve that distinction.

This changes how long the collector waits for the physical hazard to clear. It does not relax quietness. Existing stage retry cannot repair a failed bundle: the chain explicitly preserves that limitation (`joulewise/b5/chain.py:226–234`).

I would not prescribe an untested daemon suspension or protected-service unload as a demonstrated cure. Nor does this evidence justify increasing a physical threshold.

**00:10 tonight is not better.** The recurring jobs remain eligible overnight, and a roughly six-hour chain would enter the standing 05:15–06:45 avoidance span. Afternoon remains the preferable scheduling lane once the remedy is accepted.

Separately, `/usr/bin/pmset -g log` records display-on at **13:28:09** and display-off at **13:49:27**. If the standing rule requires a full hour with the display asleep, its earliest boundary is approximately **14:49**, rather than 14:30.

## Least sure

- Which physical admission condition failed for each of the four members. Restricted member records were not opened.
- Which full executable accounts for the second short-lived `spotlightknowled` PID, and which maintenance task launched the sustained work.
- Whether the observed losses alone would have removed a completed BETA-2 window. The census stop prevented that observation; four losses among 26 science members should not be extrapolated as a constant failure rate.
- The appropriate admission-wait budget. The evidence supports changing the waiting mechanism, but does not establish a particular cap.

No files changed, tests run, network requests made, or background tasks started.