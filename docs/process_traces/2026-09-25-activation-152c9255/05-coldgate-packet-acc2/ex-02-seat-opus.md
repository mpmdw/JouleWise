# Opus 5.5 seat: ACCEPTANCE-25G83-02

All numbers below were checked against their source files. The cadence statistics are my own recomputation from raw `powermetrics` plists, using the script `/tmp/152c9255/acc-opus/cad.py`. It parses the NUL-separated records, takes `elapsed_ns` and drops the first sample, the same method as record 01. I ran no sudo, launchctl, powermetrics or workload.

**Recomputed cadence and v3 interior miss rate.** A **per-pulse miss** is the fraction of random pulse placements whose 0.5 s interior holds no whole sample interval (`powermetrics_fiducial.py:748-763`).

| Set (context) | Intervals | Median | p99 | Max | Share > 0.25 s | v3 per-pulse miss | P(all 59 pulses pass) | v4 miss |
|---|---|---|---|---|---|---|---|---|
| 09-19 n1+n2, 24 captures (default launchd, night) | 20,581 | 248.5 ms | 277.8 | 419.1 | 47.3 % | 3.09 % | 0.157 | 0 |
| Session 2 D idle (default launchd, quiet, display on) | 700 | 243.2 | 281.1 | 296.4 | 43.4 % | 3.13 % | 0.153 | 0 |
| Session 2 I, idle + load | 3,498 | 131.5–131.8 | 136.0 | 143.9 | 0 | 0 | 1.000 | 0 |
| Session C I, idle + load | 6,134 | 131.5–131.8 | 136.4 | 140.8 | 0 | 0 | 1.000 | 0 |
| Stage-0U I, all | 5,249 | 131.3 | 135.9 | 139.5 | 0 | 0 | 1.000 | 0 |
| Session C SH, idle + load | 5,478 | 121.0–121.5 | 127.2 | 134.1 | 0 | 0 | 1.000 | 0 |

The data sit under `/Users/edr/osctx-mvp-01/{session2,sessionC1}/**/raw/*.plist` and `/Users/edr/night-archive/d079-epoch-25g83-derivation-n{1,2}-20260919-harvest-20260919/runs/instrument_validation/*/raw/powermetrics.plist`.

---

## Q1: The cure

**Choice: (A), `ProcessType=Interactive` with protocol v3 unchanged, plus two fail-closed tripwires that are already built in.**

**Which labels get the key**
- `com.joulewise.night` and `com.joulewise.night.deadman` are both rendered from one template, `configs/launchd/com.joulewise.night.plist.template`, by `joulewise/night_agent_install.py:608-629`. One edit to that template covers both.
- The dead-man does not measure anything. It gets the key anyway because it shares the template, and a job whose purpose is timeliness should not have its timers coalesced.
- `configs/launchd/com.joulewise.night-probe.plist.template` (rendered at `night_agent_install.py:965-976`) **must** get the key. Otherwise the probe certifies a context the night does not run in.
- `com.joulewise.magistrate` does **not** get it. It is drained during windows, and making it interactive would only raise its priority against the measurement.

**Does the setting reach child processes? Verified, not assumed.**
- The QoS values in record 26 (0x15, 0x11, 0x09) were read **inside the job process only**: `pthread_get_qos_class_np(pthread_self())` in the harness's `cell.py:28-39`, stored at `:192`. The CPU probe also ran in that process (`cell.py:157-161`). Neither reading says anything about children.
- Inheritance is shown instead by the one grandchild that matters. Production's idle baseline runs `sudo -n /usr/bin/powermetrics` as a child of the `joulewise run` child (`cell.py:131-145`, which uses `Popen`). In the same session with the same argv, that sampler delivered 243.2 ms under D and 131.8 ms under I (table above). So the launch policy passes through fork, exec and sudo.
- The night chain has the same spawn shape. `scripts/run_night.py` uses only `start_new_session=True` (`:552`, `:861`). That is setsid, which leaves QoS alone. A grep of `run_night.py`, `evidence_night.py`, `adapters/powermetrics.py` and `powermetrics_fiducial.py` finds no `taskpolicy`, `nice` or QoS change.
- Conclusion: yes, the setting must reach children, and on this spawn path it does. Q2 adds a measured check under the real installed label.

**v3 interior margin.** The interior is 1.0 − 2 × 0.25 = 0.5 s (`fiducial.py:63`, `:102`). The code needs at least **one** whole interval inside it (`:752-757`), which means two sample boundaries. The packet's wording, "two whole samples", overstates the requirement.
- A fit is guaranteed at every phase when every nearby interval is ≤ 0.25 s.
- **Under I:** the median of 131.8 ms uses 53 % of that bound, and the largest of about 14,900 intervals, 143.9 ms, uses 58 %. The headroom is 106 ms on the worst interval, and the observed miss rate is zero.
- The packet's stricter reading would need intervals ≤ 0.167 s. The I maximum of 143.9 ms still passes.
- **If coalescing recurs (the 237–248 ms regime):** 43–47 % of intervals exceed 0.25 s. The per-pulse miss rate is 3.1 %, so a capture passes all 59 pulses with probability about 0.155. That matches the observed 11 valid of 22 non-anchor captures within phase-model error.

**Why not (B):**
- **v4 would protect the calibration but not the science.** Production's idle baseline has its own bound, `_capture_timeout_s = max(15, 300 × 0.1 × 1.5 + 10) = 55 s` (`adapters/powermetrics.py:1468-1470`). Any median above 55/300 = 183 ms makes every science run fail closed. That is exactly what session 2 showed (record 21:25-26). So if coalescing came back, v4 would deliver an issued acceptance with no runnable science.
- Under (A) the same timeout is a free tripwire: it can fail closed, never quietly bias a result.
- **v4 touches a pinned file.** It edits `powermetrics_fiducial.py`, which is in the D-138 pin set (`decision_log.md:10363-10366`). That forces the r8 reissue and the atomic re-freeze. (A) touches no pinned file, so r7's pins stay intact and no reissue is needed.
- **At 132 ms the anchor bound B should return close to the r6 regime.** Two-second pulses buy nothing there and lengthen each capture from about 196 s to about 258 s (62 pulses × (pulse + 1.5 + vdC) + 10 s).

**Executable text:**
1. Add `<key>ProcessType</key><string>Interactive</string>` to the night and probe templates.
2. `validate_install` and `render_probe` parse the rendered bytes with `plistlib` and refuse unless `ProcessType == "Interactive"` for every rendered night, dead-man and probe label, mirroring the existing `KeepAlive` refusal (`night_agent_install.py:1090-1091`). Add unit tests.
3. No change to `powermetrics_fiducial.py`, `reduce.py`, `adapters/powermetrics.py` or `uncertainty_evidence.py`, so there is no reissue.

**Concerns**
- **MATERIAL:** without the installer refusal, a template regression would silently bring back D. The refusal is what makes the cure durable.
- **NIT:** correct the packet's "two whole samples" to "one whole sample interval".

## Q2: Is the evidence sufficient?

**Session C is sufficient to adopt the cure.** It used the same mechanism the night uses: a gui-domain launchd user agent with the `ProcessType` key, launching Python, then a subprocess, then `sudo -n powermetrics`. The night differs only in trigger (`StartCalendarInterval` rather than `RunAtLoad`) and in program. Neither is a plausible way to change `ProcessType`.

**Session C is not sufficient to spend a window without an in-place check, but that check is seconds long. No rehearsal night is needed.**
- W1 is its own rehearsal: if coalescing recurs, W1's captures fail closed, and so would the science runs. A dedicated rehearsal night would cost a window to test the same thing, with no gain in science safety.
- Smallest fixed check: a cadence phase in the night probe, which already runs under the real installed probe label via `launchd_probe` (`night_agent_install.py:994`).
- The daytime check cannot see the night-quiet regime. W1's own stop, set out in Q3 (d), covers that.

**Executable text:**
- The probe worker (`run_night.py:_probe_worker`) runs `sudo -n /usr/bin/powermetrics -b 0 -i 100 --samplers <production set> --format plist -n 60` as a child process.
- It records every interval, and the probe receipt carries `cadence_median_ms`, `cadence_max_ms` and `process_type`.
- **PASS iff median ≤ 150 ms AND max ≤ 250 ms.** This separates the regimes in both directions: I measures 126–132 ms, while D measures 171–178 ms by day and 243–248 ms when quiet (record 01:43-44; table).
- FAIL: the installer refuses to arm.

**Concerns**
- **MATERIAL:** the check runs by day with agents active, so it proves the setting was applied, not how the quiet night behaves. The W1 cadence stop is the night detector.
- **NIT:** 150 ms is record 24's R5 purpose-based threshold (`24:26-31`), reused so the program keeps one number.

## Q3: The registration

The file is `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`. On main it holds Revisions 1–3 (`:288`, `:514`). Ruling 20's "Revision 4" was never sealed, so the new text is **Revision 4 (Interactive/v3)**. Its STATUS line says it replaces ruling 20's R-ACC-2 text and quotes the D-184 addendum (`decision_log.md:12174-12175`).

| Item | Decision | Physical or statistical reason |
|---|---|---|
| (a) epoch | **CHANGE.** `pulse_protocol_id` is v3. powermetrics sha `b762e5bf…30c5` is unchanged. Add a stated condition: "captures launched by a launchd agent with ProcessType=Interactive (template at commit X)". Restate the ledger head pin at sealing. | Launch context changes the delivered cadence by about 1.9× (131.8 vs 243–248 ms), but the identity fields cannot see it, so the text must pin it. |
| (b) two 12-slot windows ≥ 6 h apart, any hour | **KEEP.** Re-pin the chain digest only if the probe change moves it. | Two separated sessions sample between-session drift. In the desk simulation, block drift makes a later level-screen refusal 99.9 % likely at n = 12 (`19-desk-simulations/README_acc_n12.md` table). One session cannot reveal that. |
| (c) n ≥ 12 with the D-126 addendum and the issuer constant (`issue_…generation.py:370`, `:1156-1167`) | **KEEP**, re-keyed to 25G83/v3/Interactive. | Yield at the historical rate: 24 × (30/38) × (17/19) = 16.95 retained (prereg `:91-94`). P(n ≥ 12) = 0.99, but P(n ≥ 19) = 0.25. t(0.995, 11) = 3.106 widens Q99 by 7.9 %, in the conservative direction. |
| (d) W3 only on count; W1 futility | **CHANGE.** Futility becomes W1 valid **< 6/12**, **plus a cadence stop**: if the median of W1's per-capture median frame lengths exceeds 150 ms, stop, run no W2, and return to council. The dry run reports this cadence alongside the counts. | The old < 8/12 rule falsely stops a healthy campaign 8.7 % of the time at p = 30/38. < 6/12 does so 0.5 % of the time. The cadence stop detects a broken instrument directly. Cadence is a diagnostic of how the instrument was run, not a B value, so reporting it does not break blindness. |
| (e) blindness | **KEEP.** | Rules before data. |
| (f) disclosed design inputs | **CHANGE.** Disclose the I/SH/D cadence data (this table; record 26), the eleven n1/n2 B values, marked as the default-launchd regime, and the r6 decimation. | Everything already seen is listed. None of it is a member. |
| (g) screen challenge | **KEEP DROPPED** (diagnostic only). | If the new and r6 distributions were identical, "≥ 2 of 12 above r6's maximum" would still happen with probability 1 − 17/29 − (12·17)/(29·28) = 0.163. A 10 % longer frame at 132 ms pushes that higher. The rule has no physical basis. |
| (h) excursion rule | **KEEP** the 0.075 s flag and 0.25 s refusal. | Restated basis: 0.25 s = `PLATEAU_INSET_S` (`fiducial.py:102`). An onset shift that large crosses the whole inset. |
| (i) S/C with zero headroom | **KEEP.** | At n = 12, Q99 exceeds the 0.010818 s floor only when the SD is above 0.00246 s. Strict S ≥ C would reject a tighter, better instrument. |
| (j) stale-number audit | **KEEP.** Salvage it from the v4 branch and re-key it. | The constants were keyed to r6's 120 ms cadence. |
| (k) simulation | **KEEP as already satisfied.** | Its B models are independent of protocol (mean 0.030 s, SD 0.002 s, which is r6-like) and it admitted 0/200 false claims in every model (README_acc_n12 table). No rerun is needed. Zero in 200 bounds the rate at about 1.5 %, and the text must say so. |
| (l) barrier basis | **KEEP**, add (d)'s cadence stop, and state the equivalence path as considered and not taken. | |
| v4-only text (v4 pins, r8, 2.0 s window) | **DROP.** | Not needed under (A). |

**The equivalence path against the r6 envelope: available, but not taken.**
- If the new captures came from exactly the same distribution as r6, the Revision 2 PASS rule (`:421-431`) would still fail often. The level condition passes with probability 17/29 = 0.587, the range condition with 0.623, and both together with **0.480**. That is my Monte Carlo of 200k trials with m = 12 against r6's 17.
- The expected cost is therefore about 1 + 0.52 × 2 ≈ 2.0 windows, against 2 for a direct derivation.
- A PASS would also carry a 120 ms envelope onto a 132 ms regime.
- Derive the acceptance from the regime actually in use.

**Already-seen captures**
- n1/n2 of 09-19: not members. They were taken in a different launch regime, already read, and Ed ruled neither counts (packet 03). They stay as disclosed diagnostics and replay evidence.
- qpe01 of 09-23: idle-energy pilot, a different protocol, default-launchd regime. Descriptive only, and not transferable to idle floors under I.

**Concerns**
- **MATERIAL:** without the (a) condition text, a later build or template change would leave the acceptance silently characterising another regime.
- **MATERIAL:** (d) as ruled has an 8.7 % false-stop rate.

## Q4: The v4 work

**Close PR `feat/…-v4-rev4` unmerged. Keep the branch, tag it `acc-v4-fallback` at `ea10e3c8`, and salvage parts.**

**Salvage:**
1. The stale-number audit (`37-acc-stale-number-audit.md`).
2. The epoch-scoped n ≥ 12 validator (`calibration_bracketing.py`, `_is_revision_four_epoch`), re-keyed to the v3 identity. The issuer constant and historical constant, and the D-126/D-125 addenda.
3. Zero headroom, C = max(predecessor C, Q99, S).
4. The valid-count field in the dry run.
5. The issuer's `_derivation_frame_cadence`. The issuer script is **not** in the D-138 pin set.

**Do not salvage now:** the `reduce.py` per-window flag. It is a pinned file and would stale r7. Put the per-window cadence flag in a pin-free harvest or check script, or defer it to the next re-freeze. The v4 protocol JSON and the r8 mechanism remain on the tag.

**Named trigger for the fallback.** Any one of these, confirmed by the council:
- W1's cadence stop fires with Interactive verified rendered;
- the probe cadence check fails twice with Interactive rendered;
- a future OS build under which Interactive delivers a median above 150 ms.

**Concerns**
- **MATERIAL:** the salvaged validator must not keep `pulse_protocol_id: v4` in its epoch key, or it will refuse the v3 corpus.

## Q5: Science risk and window conditions

**Usable and unusable data**
- Nothing measured under the launchd night agent from 09-15 onward is claim-bearing (record 21:29; scout 03).
- n1/n2 B values and qpe01 idle energy: default-launchd regime, diagnostic only.
- Under I, the "throttled" worry is answered for the tested workload. Against a contemporary shell launch, E = 0.99991 [0.99548, 1.00435] and R = 0.99471 [0.99192, 0.99751] (record 26:17-18).
- D's own bias remains unmeasured. That no longer matters, because no future data will be taken under D.

**The paper must disclose:**
- the launch-context cadence finding;
- that every calibration and claim capture runs under ProcessType=Interactive at about 132 ms, against July's shell at about 120 ms;
- the I/SH result, including that the widened interval [0.861, 1.161] crosses δ, and Astra's dissent;
- the 0.5 % R offset between I and SH, which applies to any comparison against July's shell corpus;
- the single-workload scope of the equivalence test.

**Window conditions**
- **Wispr Flow:** the agent quits it at arm and relaunches it at harvest (no sudo), and records it in the census. **This is not a gate.** It averaged 5.3–5.8 % of a core (record 26:64), yet E's SD stayed at 0.2–0.3 % with it running. It does not affect the calibration captures, where the plateau must be ≥ 10 W.
- **Display: no gate.** Record the powerd display assertion for each window. Record 01 guessed that display sleep explains the night slowdown, but session 2 had the display **on** and still delivered 237–248 ms under D (record 21:3, 26). The Q3 (d) cadence stop covers any display-asleep effect under I.
- **PR #410 (clone relocation) lands before W1.** Indexing about 2,300 files at clone time is a background load tied to the start of every window (record 29:12, 21). It is a cheap path change. If #410 is still unmerged 24 h after the registration seals, W1 proceeds under the existing census gate, and the index state of the clone is recorded.
- **Network time:** keep the existing pause (`scripts/joulewise-network-time.sudoers`). It is not a new gate: a clock step already invalidates the capture it lands in (n1 d07 failed on wall minus monotonic time > 5 ms, packet 03).

**Concerns**
- **MATERIAL:** the I/SH equivalence rests on one prompt, one model and 512 tokens. Every E/R claim must say that it was measured under I, not that it is launch-independent.

## Q6: Order of steps and authority

This replaces R-ACC-6:
1. **Launch-context PR:** the template key for night, dead-man and probe; the installer and probe refusal; the probe cadence phase; tests. Full-tier review with the gate record. No pinned file changes, so no reissue.
2. **Registration PR:** Revision 4 (Interactive/v3) per Q3; the D-126 cl. 2 and D-125 dated addenda; the salvaged validator and issuer code; the stale-number audit. Seal the digests of Revision 4 and `protocol_v3.json` into the registration (ruling 20 §7). Cold Fable gate, then merge.
3. PR #410 merged, per Q5.
4. Arm W1: the notice goes out with Ed's no-objection window, and the probe cadence check must PASS. Then W1 runs.
5. The count-and-cadence dry run, then the Q3 (d) stops. If they clear, W2 runs at least 6 h after W1; W3 runs only on count.
6. prepare-candidate, derivation, cold science gate, and successor issuance.
7. Regenerate the G2-a bindings with the rung check. At 0.132 s, five overlapping records need about 0.66 s of prefill (ruling 20 had 1.2 s at 0.245 s).
8. G2-a arm, then the calibration night per COUNCIL-407-01.

**Ed's part:** nothing in this path needs Ed except the notice NO and the after-the-fact summary email. The passwordless powermetrics sudo already exists (record 01).

**R-ACC-5 stands, as a request rather than a precondition.**
- A build change voids the epoch and fails closed, so this protects yield, not science.
- A read-only `defaults read /Library/Preferences/com.apple.SoftwareUpdate` shows `AutomaticDownload = 1` and no `AutomaticallyInstallMacOSUpdates` key, so it is not verifiably off.
- The toggle needs an admin login, so it is Ed's settings item. It does not block W1. The arm notice records `os_build`.

**Concerns**
- **BLOCKER:** step 2 must not merge before step 1. Otherwise the registration's epoch condition names a context that is not installed.

## Q7: What would prove this path wrong, and which step detects it

| Failure | Detector |
|---|---|
| Interactive is not applied, or does not reach the sudo child, in the real chain | Probe cadence check (step 4). W1 cadence stop. |
| Interactive still coalesces on a quiet night | W1 cadence stop (step 5). Production's 55 s bound fails closed for science. |
| B at 132 ms is not r6-like (frequent excursions, drift) | `excursion_limited` label, the 0.25 s refusal, and the S/C rules at issuance (step 6). Later level-screen refusal rates in the first G2-a windows (step 8). |
| I biases E/R relative to a shell launch for other workloads | Not detected. It is disclosed as scope (Q5). Claims are made only within I. |
| n = 12 is too small under between-window drift | Early level-screen refusals in G2-a (step 8). Fails closed and returns to council for W3 or more windows. |

## Where I expect the other seats to be wrong
- Choosing (B) for safety. v4 protects only the calibration; production fails closed above a 183 ms median no matter what, and v4 costs a reissue and a re-freeze.
- Citing record 26's QoS values as proof that children inherit the setting. Those were read in the job process only (`cell.py:28-39,192`). The proof is the grandchild's cadence.
- Reviving the equivalence path. Its PASS probability is about 0.48 even when nothing changed, so it saves nothing.
- Requiring a rehearsal night, or keeping the 8/12 futility rule. W1 already fails closed, and 8/12 false-stops 8.7 % of healthy campaigns.
- Blaming display sleep. Session 2 had the display on and still showed 243 ms under the default launch.

## Plain summary for Ed
1. The slow sampling was never the new macOS. The overnight job was started with the scheduler's default low-priority setting, which lets the OS delay the sampler's wake-ups.
2. With the job marked "Interactive", sampling runs at about 132 ms, close to July's 120 ms. The old 1-second calibration pulses then pass with a wide margin, so the 2-second redesign isn't needed.
3. If the slowdown ever came back, both the calibration and the science runs would stop and report failure rather than produce bad numbers.
4. A short sampling check runs every time a night is set up, and the first calibration window stops itself if sampling is slow.
5. Calibration becomes two windows of 12 captures at least 6 hours apart, needing 12 good captures. Three old rules that failed often by chance are dropped or loosened.
6. The paper will state that all data were taken under this launch setting, and that it matched a normal terminal launch within 0.5 % on the tested workload.
7. The only thing asked of you: please turn off automatic macOS updates when convenient. It isn't a blocker.
