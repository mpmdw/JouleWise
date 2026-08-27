# PART 1 — HOW TO LAND IT

Here, **privileged scope** means the exact commands D-127 permits an ordinary
user to run as root through `sudo`; a **scope closure** freezes that existing
two-command set and adds nothing. At repository HEAD
`2fd7c920314333535ea2631bec887a19b964f834`, edit
`docs/decision_log.md` as follows:

1. Insert the fenced text in Part 2 after D-127 item 5, whose last line is
   `docs/decision_log.md:8218`, and before the `## D-128:` heading at
   `docs/decision_log.md:8220`.
2. Use the proposed `### D-127 amendment — 2026-08-26: ...` heading exactly.
   The log writes full decisions as `## D-NNN: ...` with a dated status line
   (`docs/decision_log.md:8182-8185`) but writes later changes as level-three,
   date-stamped amendment headings (`docs/decision_log.md:4173-4178`,
   `docs/decision_log.md:8707-8715`). The command
   `rg -n '^## D-[0-9]{3}\.[0-9]+:|^### D-[0-9]{3}\.[0-9]+' docs/decision_log.md`
   returned no matches at this HEAD, so the log has no `D-NNN.1` body-heading
   precedent. The chosen heading preserves the requested D-127.1 meaning in
   the shape the log already parses.
3. Do not add an index row and do not change another repository file in the
   landing commit. This is an amendment under D-127, not a new `## D-NNN:`
   decision body. The existing D-127 index row is at
   `docs/decision_log.md:152`; amendments elsewhere remain under their parent
   without a second decision ID, as shown by the D-124 body and its amendments
   (`docs/decision_log.md:7963`, `docs/decision_log.md:8002`,
   `docs/decision_log.md:8057`).

The test grep found these consumers of the real decision-log text. None pins a
SHA-256 content fingerprint of `docs/decision_log.md`, and only the first one
compares the index's decision IDs with the body-heading decision IDs:

| Check | What it reads or counts | Consequence for this landing |
|---|---|---|
| `tests/test_docs_freshness.py:175-184` | Extracts index `D-NNN` rows and `## D-NNN:` bodies, rejects duplicates, and requires the two ordered lists to match. It counts the extracted lists but pins no numeric total and no fingerprint. | A `### D-127 amendment` creates no body ID, so the index must remain unchanged. |
| `tests/test_build_site_parsers.py:653-687` with `scripts/build_site.py:43-44,406-444` | Parses real `## D-NNN:` bodies, treats `###` as an oversized-body split point, and checks the real D-078 entry renders once. It pins neither the real-log entry count nor a fingerprint. | The amendment stays inside D-127 and needs no companion file. |
| `tests/test_whole_window_selection.py:105-139` | Reads two named D-078 clauses and checks required failure-name membership. It counts neither decisions nor a fingerprint. | Unaffected. |
| `tests/test_d078_reason_registry.py:21-28,31-74,109-122` | Splits from named D-078 amendment markers, requires one selected marker, and checks required failure-name membership. It counts selected markers only, not decision entries, and pins no fingerprint. | Do not repeat a D-078 marker or a registered failure name in the amendment. Part 2 does neither. |
| `tests/test_identity_pins.py:1095-1105` | Requires one named D-078 identity-pin amendment marker and checks five names after it. It counts that marker only and pins no fingerprint. | Unaffected. |
| `tests/test_capture_t0_step.py:624-631` | Requires each of the twelve capture-failure names to occur exactly once in the whole log. It counts those names, not decision entries, and pins no fingerprint. | Part 2 deliberately repeats none of those twelve names (`docs/decision_log.md:9571-9588`). |
| `tests/test_gen_state.py:521-532,678-686` | Reads the log and checks one P2-006 retirement sentence. It counts neither decisions nor a fingerprint. | Unaffected. |

For completeness, the remaining `decision_log.md` test grep hits do not parse
the real log: `tests/test_arm_readiness_evidence_author.py:121-144` copies it
into a dynamically hashed fixture without pinning its bytes;
`tests/test_quiet_guard.py:58-69` treats its filename as a forbidden quiet-run
write target; `tests/test_claims_lint.py:672-680` excludes it in a synthetic
fixture; and `tests/test_pack_capsule.py:524-551` uses synthetic rendered-page
names. Therefore no index row, generated page, count constant, or digest file
must change for these checks to remain green.

# PART 2 — THE AMENDMENT TEXT ITSELF

```markdown
### D-127 amendment — 2026-08-26: privileged scope closure for unattended T-0

**Date:** 2026-08-26. **Status:** PROPOSED (awaiting Ed's ratification).

**Decision.** D-127's privileged scope — the commands permitted to run as root through `sudo` — is unchanged and now final for T0-UNATTENDED-01. The only authorized commands remain `/usr/sbin/systemsetup -setusingnetworktime off` and `/usr/sbin/systemsetup -setusingnetworktime on`, quoted from `Cmnd_Alias JOULEWISE_NETWORK_TIME = /usr/sbin/systemsetup -setusingnetworktime off, /usr/sbin/systemsetup -setusingnetworktime on` in `scripts/joulewise-network-time.sudoers:2`. The four-line fragment, final newline included, has SHA-256 `7dfe980be89a7912d69c6e72b5582649fc4c50db88bf709bcfbb4a1c34e4406d`, recomputed by `shasum -a 256 scripts/joulewise-network-time.sudoers`. Unattended T-0 requires no new privileged command. Its six-hour evidence-validity horizon — the period during which an issued T-0 record may remain usable — is unchanged (`docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md:73-83`).

**Options considered.** Adding `/usr/sbin/systemsetup -getusingnetworktime` to sudoers is rejected; retiring that read from window T-0 is adopted. The `get` remains observability-only — available to report state to an operator but unable to make T-0 pass or fail — in the separate operator tool (`scripts/quiet_window_clock.sh:47-55`), and is RETIRED for window T-0, not deferred.

**Considerations.** Removing the read removes no pass/fail coverage — no ability to catch a bad window — because the evidence producer, the code that writes the fact, sets `prior_systemsetup_state_captured` to constant `True` (`joulewise/arm_readiness_evidence_t0.py:875-880`), while the consumer, the code that admits the fact, requires that same constant (`joulewise/arm_readiness.py:802-806,5891-5899,5916-5941`); the observed-state field `prior_network_time` is written at `joulewise/arm_readiness_evidence_t0.py:879` and a HEAD search finds no reader. Restore remains controlled independently by `clock.restore_recipe.v1`, the named pass/fail predicate, defined at `joulewise/arm_readiness.py:811-815`.

**Revisit.** Any future proposal to add a privileged `get` is a new decision, not authority implied by D-127 or this amendment.
```

The no-reader statement above was verified at HEAD, not copied from either
design seat. This command:

```sh
rg -n 'prior_network_time|prior_systemsetup_state_captured' joulewise scripts tests
```

returned only
`joulewise/arm_readiness.py:805`,
`joulewise/arm_readiness_evidence_t0.py:877`, and
`joulewise/arm_readiness_evidence_t0.py:879`. The reader-form search

```sh
rg -n '\["prior_network_time"\]|\.get\("prior_network_time"|\.pop\("prior_network_time"' joulewise scripts tests
```

returned no matches (exit 1). The Opus input reports the same sudoers SHA-256
at `docs/process_traces/2026-08-23-t22/t0-unattended/seat-opus-design.md:371-373`;
the recomputed value matches it exactly.

# PART 3 — THE EVIDENCE TABLE

In this table, **privilege required** asks whether the operation needs root via
`sudo`; **already granted** means the tracked D-127 fragment names the exact
command, not that its live installation was assumed; **none needed** means the
ordinary `edr` account can issue the operation; and **not used** means the ruled
T-0 sequence does not execute it. R0 is the reference sample before network
time is disabled, and R1 is the fresh reference during evidence authoring. In
this part, `MAGISTRATE-RULING-T0-UNATTENDED.md` abbreviates
`docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md`;
R0 and R1 are defined at its lines 47-59. The **anchor** is the difference
between the adjustable wall clock and the raw monotonic clock, sampled at two
endpoints so a change over the T-0 sequence is detectable
(`MAGISTRATE-RULING-T0-UNATTENDED.md:61-70`). The table enumerates every
operating-system command and clock read newly named by the ruling, the existing
capture/authoring command group the ruling keeps in the sequence, and the
restore and supervised-rehearsal operations. In-process arithmetic and local
JSON/file handling are grouped in the last row because none enters sudoers.

| Operation | Privilege required | Status | Proof |
|---|---|---|---|
| R0: `/usr/bin/sntp -t 2 time.apple.com` | No | none needed; live network result **NEEDS-ED** | The ruled fixed roster and one invocation per hostname are at `MAGISTRATE-RULING-T0-UNATTENDED.md:47-55`. `/usr/bin/sntp` is world-executable in the draft-time `stat` transcript below. Network access was forbidden, so hostname reachability and Darwin output were not exercised. |
| R0: `/usr/bin/sntp -t 2 pool.ntp.org` | No | none needed; live network result **NEEDS-ED** | Same ruled roster and invocation rule: `MAGISTRATE-RULING-T0-UNATTENDED.md:47-55`; same sandbox limitation. |
| R0: `/usr/bin/sntp -t 2 time.nist.gov` | No | none needed; live network result **NEEDS-ED** | Same ruled roster and invocation rule: `MAGISTRATE-RULING-T0-UNATTENDED.md:47-55`; same sandbox limitation. |
| R1: `/usr/bin/sntp -t 2 time.apple.com` | No | none needed; live network result **NEEDS-ED** | R1 is live at authoring and precedes the fresh censuses (`MAGISTRATE-RULING-T0-UNATTENDED.md:55-59`); same sandbox limitation. |
| R1: `/usr/bin/sntp -t 2 pool.ntp.org` | No | none needed; live network result **NEEDS-ED** | R1 ordering and the fixed roster are at `MAGISTRATE-RULING-T0-UNATTENDED.md:47-59`; same sandbox limitation. |
| R1: `/usr/bin/sntp -t 2 time.nist.gov` | No | none needed; live network result **NEEDS-ED** | R1 ordering and the fixed roster are at `MAGISTRATE-RULING-T0-UNATTENDED.md:47-59`; same sandbox limitation. |
| `clock_gettime(CLOCK_REALTIME)` reads for both T-0 anchor endpoints and the later arm-side re-sample | No | none needed | The ruled endpoints and later re-sample are at `MAGISTRATE-RULING-T0-UNATTENDED.md:61-70`. The draft-time Python probe below succeeded as ordinary user `edr` (`euid=501`). |
| `clock_gettime(CLOCK_MONOTONIC_RAW)` reads for both T-0 anchor endpoints and the later arm-side re-sample | No | none needed | The ruling requires this sleep-immune clock explicitly (`MAGISTRATE-RULING-T0-UNATTENDED.md:61-69`). The draft-time Python probe below succeeded as `euid=501`. |
| `/usr/sbin/sysctl -n kern.bootsessionuuid` before/after capture and during authoring | No sudo in the exact argv | none needed by design; sandbox execution **NEEDS-ED** | The existing author executes the exact command and fails closed on error (`joulewise/arm_readiness_evidence_t0.py:437-452`); the capture wrapper reuses the same reader before and after each command (`scripts/capture_t0_step.py:269-275,913-930`). The sandbox command failed `Operation not permitted`, recorded below, so the bench route remains unverified here. |
| First `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` during capture | Yes | already granted in the tracked fragment; live install/output **NEEDS-ED** | The capture wrapper's exact argv is `scripts/capture_t0_step.py:611-623`; the grant is `scripts/joulewise-network-time.sudoers:2`. No sudo command was attempted in this sandbox. |
| Second `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` during evidence authoring | Yes | already granted in the tracked fragment; exact stdout **NEEDS-ED** | The author re-executes the exact argv at `joulewise/arm_readiness_evidence_t0.py:891-908`; the ruling requires two active executions, exit 0, and exact `setUsingNetworkTime: Off` output at `MAGISTRATE-RULING-T0-UNATTENDED.md:85-89`. The exact output under sudo is an Ed bench check, not a sandbox claim. |
| `/usr/sbin/systemsetup -getusingnetworktime` in window T-0 | Yes if it were run | not used — RETIRED, not deferred | The ruling finds its evidence mechanically dead and closes rather than enlarges scope (`MAGISTRATE-RULING-T0-UNATTENDED.md:12-18`). The source search `rg -n -- '-getusingnetworktime' scripts/capture_t0_step.py joulewise/arm_readiness_evidence_t0.py scripts/prewindow_check.sh` returned no matches (exit 1); `tests/test_capture_t0_step.py:516-525` pins that absence. Its failure-tolerant operator-tool observation remains at `scripts/quiet_window_clock.sh:47-55`. |
| `/usr/sbin/ioreg -c IOHIDSystem`, strict numeric `HIDIdleTime` read for the rehearsal's no-local-input witness | No | none needed | The rehearsal requires `HIDIdleTime` at least the T-0 span and refuses absent output (`MAGISTRATE-RULING-T0-UNATTENDED.md:91-103`). Existing code executes `ioreg -c IOHIDSystem` and strictly extracts digits (`joulewise/environment.py:349-356,669-673`). The ordinary-user draft-time command below exited 0 and returned a numeric field. |
| Fresh maintenance census: `/usr/bin/pgrep -lf 'XProtect\|mds_stores\|mdworker\|mdbulkimport\|backupd\|photoanalysisd\|softwareupdated\|Spotlight\|mediaanalysisd'` | No | none needed | Existing author command and absent-process refusal: `joulewise/arm_readiness_evidence_t0.py:985-1015`; the ruling orders R1 before this census (`MAGISTRATE-RULING-T0-UNATTENDED.md:55-58`). |
| Fresh process census: `/usr/bin/pgrep -x caffeinate` and three `/usr/bin/pgrep -lf ...` classes for agents, browsers, and monitors | No | none needed | Exact commands and absent-process refusal are at `joulewise/arm_readiness_evidence_t0.py:1393-1409`; the ruling keeps `caffeinate` absent and orders R1 before the census (`MAGISTRATE-RULING-T0-UNATTENDED.md:21-24,55-58`). |
| `/bin/bash scripts/quiet_mac_prep.sh`, including its application census/quit requests, CPU/process reports, display sleep request, screensaver reads, and pre/post HID reads | No new D-127 privilege; the nested powermetrics probe uses its separate existing grant | none needed for the unprivileged commands; nested powermetrics **NEEDS-ED** | The capture wrapper executes the reviewed script (`scripts/capture_t0_step.py:624-625`), whose commands are enumerated at `scripts/quiet_mac_prep.sh:10-123`; the author requires its three success lines at `joulewise/arm_readiness_evidence_t0.py:1055-1068`. |
| `/usr/bin/sudo -n /usr/bin/powermetrics -i 200 -n 1`, once inside quiet preparation and once as the author's fresh probe | Yes, under D-004 rather than D-127 | already granted by the separate design; live result **NEEDS-ED** | D-004 selects the exact powermetrics-only sudoers rule (`docs/decision_log.md:316-345`). The script call is `scripts/quiet_mac_prep.sh:46-51`; the fresh author call and exit-zero check are `joulewise/arm_readiness_evidence_t0.py:1472-1490`. D-127's fragment names only the two network-time commands (`scripts/joulewise-network-time.sudoers:2`), so this existing privilege is not added or inherited here. No sudo command was attempted. |
| `/usr/bin/pmset -g therm` | No | none needed | Exact author probe and refusal are at `joulewise/arm_readiness_evidence_t0.py:1037-1051`. |
| `/usr/bin/pmset -g batt`, `/usr/bin/pmset -g custom`, and `/usr/sbin/system_profiler SPPowerDataType -json` | No | none needed | Exact power probes and checks are at `joulewise/arm_readiness_evidence_t0.py:1506-1532`. |
| The launch-manifest-selected prewindow command, followed by `.venv/bin/python scripts/recover_calibration_ledger.py readiness ...` and `.venv/bin/python scripts/reserve_calibration_window_bracket.py ... --execute` | No new D-127 privilege | none needed beyond whatever the reviewed prewindow command itself declares | The capture wrapper takes the prewindow argv from the authenticated launch manifest and spells both Python commands at `scripts/capture_t0_step.py:626-683`; the author requires the captured prewindow command to equal the manifest command and prove the ten-minute idle at `joulewise/arm_readiness_evidence_t0.py:970-982`. No command in these three wrapper rows enlarges D-127. |
| Open `/dev/null` as stdin for every rehearsal subprocess | No | none needed | The first rehearsal condition is noninteractive stdin, with any surviving prompt causing refusal (`MAGISTRATE-RULING-T0-UNATTENDED.md:91-94`). |
| `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on` after the verdict and both backups | Yes | already granted in the tracked fragment; live execution **NEEDS-ED** | The exact restore command and ordering are at `docs/phase_2/window_runbook.md:630-648`; the grant is `scripts/joulewise-network-time.sudoers:2`. The separate restore predicate is `clock.restore_recipe.v1` at `joulewise/arm_readiness.py:811-815`. |
| Intentional privileged clock adjustment for the anchor positive control — a deliberately caused change that proves the detector refuses — outside T-0 and adjacent to the supervised rehearsal | Yes | not used in T-0; control execution **NEEDS-ED** | The ruling requires this adjacent control and says it is not a T-0 intervention (`MAGISTRATE-RULING-T0-UNATTENDED.md:101-105,120-126`). It does not publish an exact adjustment command; this draft does not invent one. |
| Local Git and file reads, receipt construction, numeric comparisons, the D-149 C1-C5 checks, rehearsal/production separation, backups, and restore-order verification | No additional root command | none needed beyond the exact `on` restore above | The ruled ten-condition rehearsal includes these operations and the complete lifecycle (`MAGISTRATE-RULING-T0-UNATTENDED.md:91-105`). No additional privileged command is named there, and the scope is closed to the sudoers pair at `scripts/joulewise-network-time.sudoers:2`. |

Draft-time read-only command evidence:

```text
$ shasum -a 256 scripts/joulewise-network-time.sudoers
7dfe980be89a7912d69c6e72b5582649fc4c50db88bf709bcfbb4a1c34e4406d  scripts/joulewise-network-time.sudoers

$ stat -f '%Sp %Su:%Sg %N' /usr/bin/sntp /usr/sbin/ioreg /usr/sbin/sysctl /usr/sbin/systemsetup
-rwxr-xr-x root:wheel /usr/bin/sntp
-rwxr-xr-x root:wheel /usr/sbin/ioreg
-rwxr-xr-x root:wheel /usr/sbin/sysctl
-rwxr-xr-x root:wheel /usr/sbin/systemsetup

$ /Users/edr/code/JouleWise/.venv/bin/python -c 'import os,time; print(f"euid={os.geteuid()}"); print(f"CLOCK_REALTIME={time.clock_gettime_ns(time.CLOCK_REALTIME)}"); print(f"CLOCK_MONOTONIC_RAW={time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)}")'
euid=501
CLOCK_REALTIME=1787792537988724000
CLOCK_MONOTONIC_RAW=237175918033333

$ /usr/sbin/ioreg -c IOHIDSystem | /usr/bin/awk -F'= ' '/"HIDIdleTime"/{gsub(/[^0-9]/, "", $2); print "HIDIdleTime=" $2; found=1; exit} END{if (!found) exit 1}'
HIDIdleTime=1745600690125
exit=0

$ /usr/sbin/sysctl -n kern.bootsessionuuid
sysctl: sysctl fmt -1 1024 1: Operation not permitted
exit=1
```

No SNTP network request and no `sudo` command was attempted. The ruled roster's
live reachability, the installed sudoers state, both exact `off` results, the
`on` restore, the positive control, and the exact `setUsingNetworkTime: Off`
line therefore remain **NEEDS-ED**.

# PART 4 — ED-HANDS ITEMS

An **Ed-hands item** is a physical-machine or approval step reserved to Ed; an
agent may prepare its text or inspect repository evidence but may not perform
the step. All four items below come from the ruling's complete list at
`MAGISTRATE-RULING-T0-UNATTENDED.md:120-131`.

| Item | What Ed must physically do | Why an agent cannot do it | What it blocks | Rough time |
|---|---|---|---|---|
| 1. Pre-existing D-127 install and cold-credential exercise | Authenticate and install the SHA-256-matched four-line fragment as `/etc/sudoers.d/joulewise-network-time`; then clear cached credentials with `/usr/bin/sudo -k`, run the exact `off` and `on` commands with `sudo -n`, and finish restored to `on` (`docs/phase_2/window_runbook.md:557-584`). | D-127 reserves the single install command to Ed (`docs/decision_log.md:8198-8206`), and this sandbox was forbidden to run sudo or treat the live sudo policy as qualified. | Every attended or unattended window if the capability is absent or no longer qualified (`MAGISTRATE-RULING-T0-UNATTENDED.md:120-123`). | About 5 minutes, a drafting estimate based on the one install plus three-command exercise at `window_runbook.md:568-584`. |
| 2. Privileged anchor positive control | At the bench, outside T-0 but adjacent to the supervised rehearsal, intentionally cause a privileged clock adjustment while the collector samples and confirm the 5 ms anchor rule refuses (`MAGISTRATE-RULING-T0-UNATTENDED.md:101-105,124-126`). | It requires a real privileged clock adjustment on the physical Mac; the sandbox cannot perform it, and doing it inside T-0 would invalidate the rehearsal (`MAGISTRATE-RULING-T0-UNATTENDED.md:103-105`). | Evidence that the anchor detector is coupled to a real platform clock adjustment rather than only to injected test numbers (`MAGISTRATE-RULING-T0-UNATTENDED.md:124-126`). | About 2 minutes, as ruled at `MAGISTRATE-RULING-T0-UNATTENDED.md:124-126`. |
| 3. Ratify the closure and retained six-hour horizon | Approve or reject the proposed D-127 amendment and explicitly retain the six-hour T-0 evidence lifetime (`MAGISTRATE-RULING-T0-UNATTENDED.md:73-83,127-129`). | `proposed` means awaiting Ed's approval under the log's status vocabulary (`docs/decision_log.md:14-16`); an implementation agent cannot convert its own draft into Ed's decision. | Adoption of this amendment and any window relying on the amended scope (`docs/process/state_kernel.json:3744-3756`). | Under 5 minutes, a drafting estimate for one approval decision over the pasted text. |
| 4. Verify the exact Off stdout under sudo | Before the strengthened check is enabled, run the exact privileged `off` command at the bench, capture stdout, prove that its one accepted line is byte-for-byte `setUsingNetworkTime: Off`, then restore `on` (`MAGISTRATE-RULING-T0-UNATTENDED.md:85-89`; restore command at `window_runbook.md:630-648`). | Only Ed can exercise the live installed sudo capability; the sandbox was expressly barred from privileged commands. | Enabling the exact-output postcondition: an unverified or wrong literal would refuse every window (`MAGISTRATE-RULING-T0-UNATTENDED.md:85-89,130-131`). | About 2 minutes, a drafting estimate for one `off` capture plus the exact `on` restore. |

The amendment creates **no new Ed-hands item** because it adds no privileged
command (`MAGISTRATE-RULING-T0-UNATTENDED.md:127-129`). There is one status
record to reconcile rather than silently assume: a historical sitting report
says the write commands were installed and exercised
(`docs/process_traces/2026-08-20-go-session/readiness-sitting/seat-L8.md:225-228`),
while the tracked runbook still shows both installation and exercise unchecked
(`docs/phase_2/window_runbook.md:568-584`) and the later ruling retains the item
as Ed-hands (`MAGISTRATE-RULING-T0-UNATTENDED.md:120-123`). Until Ed or the
magistrate reconciles those records against the live machine, item 1 remains
**NEEDS-ED** in this draft.

# PART 5 — WHAT THIS AMENDMENT DOES NOT DO

- It does not authorize unattended launch or relaunch. That work, including
  D-127 clause 4 and the E-10 change, belongs to the separate blocked
  `UNATTENDED-LAUNCH-01` row; production windows require both rows
  (`docs/process/state_kernel.json:3955-4001`).
- It does not change the six-hour T-0 evidence lifetime or hide a shorter
  lifetime inside a later evidence-age check
  (`MAGISTRATE-RULING-T0-UNATTENDED.md:73-83`).
- It does not amend D-078's twelve capture-refusal names, meaning the
  machine-readable reasons the acquisition wrapper can emit
  (`docs/decision_log.md:9571-9588`).
- It does not rename `clock.correct_and_prior_state.v1`, change the evidence
  kind, or alter the row registry, the table that binds fact rows to evidence
  kinds. Those changes are expressly deferred to the
  post-`_v4` `T0-CLOCK-ROW-RENAME-01` row
  (`MAGISTRATE-RULING-T0-UNATTENDED.md:35-45`;
  `docs/process/state_kernel.json:3725-3741`).
- It does not relax or rewrite historical attended receipts; the ruled
  `OPERATOR_ATTESTATION` branch remains byte-identical
  (`MAGISTRATE-RULING-T0-UNATTENDED.md:35-40`).
- It does not delete the failure-tolerant `get` from the separate operator
  status tool. It retires that read only from window T-0, consistent with the
  r4-6 observation-only fence (`scripts/quiet_window_clock.sh:47-55`;
  `docs/process_traces/2026-08-20-go-session/v4-plan-ruling-r4draft.md:203-213`;
  `docs/process/state_kernel.json:3772-3778`).
- It does not claim that the sudoers fragment is installed now, that any live
  SNTP leg succeeds, that the exact Off line has been observed, or that the
  supervised rehearsal has passed. Those are the **NEEDS-ED** checks in Parts
  3 and 4 (`MAGISTRATE-RULING-T0-UNATTENDED.md:85-105,120-131`).
- It does not relax the rule that no agent runs during capture or make a
  supervised rehearsal eligible as production evidence
  (`MAGISTRATE-RULING-T0-UNATTENDED.md:91-103`; D-127's unchanged capture rule
  at `docs/decision_log.md:8193-8197`).
