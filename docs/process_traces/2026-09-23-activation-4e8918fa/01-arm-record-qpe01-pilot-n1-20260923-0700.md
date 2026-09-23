# Activation 4e8918fa — arm record for qpe01-pilot-n1-20260923-0700 (2026-09-23, ARMED)

Headless magistrate activation `4e8918fa-0d77-4628-a452-d21ab50ead19`, on Opus 5.5. The watchdog spawned it at
05:34:23 PDT (attempt 87) after activation 4158e658 exited under D-183: 4158e658's resident supervisor (pid
2913, started 04:24) was older than H, which reached the canonical checkout at 05:13, so `check` would have
refused it. This activation ran the successor procedure in
`docs/process_traces/2026-09-23-activation-4158e658/01-activation-record.md` §3, steps 0–7, between 05:34 and
05:38 PDT; step 8 is this record and the exit. The machine-readable outputs are the staging `lifecycle/` records, whose digests are listed below.

## Authority

- Arm gate on the staged bytes, run by 4158e658 (records 05–08 of that activation): cold Fable 5.1 **ARM**
  (record 06), Opus 5.5 ARM (07), and Sol 6.0 ARM AFTER CURES (08). Sol's dissent is recorded there and became
  lane NOTICE-SUMMARY-V3-TEXT-01 (A276). Fable's verdict prevails (topology line, Ed 09-23). The stand-in for
  the notice cure is the ONE appended correction line below.
- The RUN_STATE top block on main `9e816173`, together with record 01 §3.
- Ed's NO on any thread overrides at every step. None was observed. Gmail inbound for the last day holds only
  Ed's 01:06 reply, which was already processed by 7a0f14bd. The owner directive list (`gh issue list … --label
  directive --author mpmdw`) returned `[]` at 05:35 and again at 05:37. There was no `standdown.request` and
  no `STOP`, and nothing was written to `$STAGE/lifecycle/NO`.

## Frozen triple

| Field | Value |
|---|---|
| plan_id | `qpe01-pilot-n1-20260923-0700`. This is attempt 3 of pilot night one; the tool's notice counter says attempt 1 for this date. |
| repo_head = measurement_head = H | `26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15` |
| measurement_root (clone) | `/Users/edr/JouleWise-measurement-20260923-0700-1790172000-26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15-qpe01-pilot-n1`. HEAD was verified to equal H at 05:39, with `git status --porcelain` empty. |
| custody root | `/Users/edr/night-custody/qpe01-pilot-n1-20260923-0700-20260923-0700-1790172000-26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15` |
| staging ($STAGE) | `/Users/edr/night-plan-staging/qpe01-pilot-n1-20260923-0700-20260923-0700-1790172000-26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15` |
| registration | `pilot_protocol_v3.json` sha256 `69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616` |
| plan sha256 | `6193c6b6e90ea1655b960866054c1c4bac0964e98673f8e749ff20eceb61b566` |
| t0 | 2026-09-23 07:00:00 PDT = epoch 1790172000; `window_max_s` 9000 |
| install close (excluded) / REQUEST / TERM / KILL | 06:50:00 / 06:52:00 / 06:54:00 / 06:55:00 PDT |
| window end / courier deadline / daily dead-man | 09:30:00 / 09:35:00 / 10:35:00 PDT |

## Executed steps

All steps ran from `/Users/edr/code/JouleWise` as `python3 -B -m joulewise.evidence_night …`.

| # | Step | Result |
|---|---|---|
| 0 | heartbeat | written at 05:34:34: `14978 4e8918fa-… 1790166874` |
| 0 | launch email to Ed | Gmail `1a0ce432c738b78d`, then `notice.ack` was written |
| 0 | `env \| grep EVIDENCE_POWER_RECORDER` | printed nothing (rc 1) |
| 0 | `launchctl list \| grep joulewise` before the arm | only `com.joulewise.magistrate`; no night plist on disk |
| 0 | canonical HEAD | `9e816173`, which contains H (`merge-base --is-ancestor` rc 0). Reflog: fast-forwards at 05:13:10 (to H) and 05:26:40 (to `9e816173`), both before this supervisor started. |
| 1 | staged bytes against record 09 | `shasum -a 256 night_plan.json prepare.json render/*.plist`: all five digests equal `09-staging-sha256.txt`. There was no re-prepare. `publish-install` later moved `night_plan.json` to the custody root; its digest is unchanged. |
| 2 | terminate own MCP helpers | ROOT is 14978 (`claude -p`). TERM went to 14993 (`npm exec @openai/codex@0.153.3 mcp-server -c model="gpt-5.6-sol" -c model_reasoning_effort="high" -c mcp_servers.claude.enabled=false`) and its descendants 15022 (`node …/.bin/codex mcp-server …`) and 15023 (the vendor `codex mcp-server` binary). The descendant scan was empty after one poll. Nothing outside ROOT's subtree was touched. 14996 and 15011 are the pdf MCP server, not a Codex helper; they were left alone, and the census classifies them as own descendants. See divergence 1. |
| 3 | `check --candidate $STAGE` | rc 0, `armable: true`, `fake_launchctl: false`. All nine checks pass: `sealed`, `night_agents`, `canonical` (fast_forward null), `supervisor` (pid 14974 started 1790166863, after H arrived at 1790165590), `machine_quiet` (bar 0.5 busy cores over a 30.4 s interval; the top consumer was this session at 0.019 cores), `courier`, `retained_roots`, `census` (foreign_pids [], diagnostics []), `retry`. Check id `70c510f35ef9`; the check ran 05:35:52 → 05:36:24. |
| 4 | `notice --candidate $STAGE` | rc 0. `lifecycle/notice.txt` is 5,719 bytes, sha256 `f29633d1b72dcd2b0a1455613abd042fae8c897a8774f90238ff1d3a5f2cb696`. |
| 4 | send notice | Gmail `1a0ce4522dbdbf03` accepted at 05:37:12 PDT, to one recipient (`claude2.glaring610@passmail.net`), no cc. The subject is the tool's (`NIGHT NOTICE — qpe01-pilot-n1-20260923-0700 (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 1`). The body is `notice.txt` verbatim plus exactly the one line below. The exact intended body is kept at `/Users/edr/night-custody/magistrate/intended-arm-notice-4e8918fa.txt` (6,348 bytes, sha256 `0c0550bb…c8c8`). The sent message was read back through Gmail (`get_thread`, plain text) and compared line by line against it. |
| 5 | `veto --candidate $STAGE` | rc 0, `clear: true`, `production: true`. NO, STOP, standdown and directives were all clear, `non_owner_directives: []` (05:37:23). |
| 6 | `publish-install --candidate $STAGE --notice-accepted 1a0ce4522dbdbf03` | rc 0, `outcome: installed`, `phase: complete`. Published at 05:37:32, 72 min before install close. `plan_sha256` = `6193c6b6…b566`; probe receipt sha256 `c21f9ed9…bdc4`; launchd probe ok. `lifecycle/arm-attempts/000001/` holds `plan.json`, `baseline.json`, `install.json` and `veto-at-publication.json`. `notice_verified: false` is the tool's standing statement that it cannot compare sent bytes; the ca45291d arm record says the same. |
| 7 | `verify --candidate $STAGE` | rc 0. `com.joulewise.night` is LOADED, its plist sha256 equals the render sha256 `0604c357…5d65`, and its calendar is Month 9 Day 23 Hour 7 Minute 0. `com.joulewise.night.deadman` is LOADED at `d6cd89ff…1a85`, calendar Hour 10 Minute 35. Baseline drift is false. |
| 7 | `launchctl list \| grep joulewise` after the arm | `com.joulewise.night`, `com.joulewise.magistrate` and `com.joulewise.night.deadman`, all status 0 and not running |

Lifecycle record digests (sha256): `check.json` `70c510f3…6f17`, `veto.json` `fb438855…34ef`, `install.json`
`90e7940c…4d9c`, and the verify stdout `7b5ffabb…5d3e`. The verify stdout was not written to `lifecycle/`; it
is kept as `02-verify-stdout.json` in this directory (sha256 `7b5ffabb…5d3e`) and summarised in step 7.

## The one appended line (record 01 §3 of 4158e658), pasted exactly as sent

```
Correction appended by the magistrate (arm gate of activation 4158e658, Sol 6.0 finding F1; the generated text is being fixed in lane NOTICE-SUMMARY-V3-TEXT-01): under registration v3 busy cores are not only descriptive — a process outside the measurement apparatus at or above 0.5 busy cores at the arm check or at t0 refuses the night, one that uses 30 or more core-seconds inside an envelope excludes that envelope, and two such envelopes in a row end the night; the programmed span is 8,020 s (600 s settle + 11 × 620 s slot pitch + 600 s), not 7,800 s; this is attempt 3 of pilot night one, not the first evidence night.
```

The line was extracted mechanically from the record at `9e816173`, by the first line that, after leading
whitespace, begins `Correction appended by the magistrate`.

## Divergences recorded, not cured

1. **The helper-termination recipe in NIGHT_HANDBACK §Purpose missed this session's helper.** The recipe greps
   the session root's direct children for the literal `codex mcp-server`. Here the direct child's command line
   was `npm exec @openai/codex@0.153.3 mcp-server …`, which the pinned `.mcp.json` launch produces, so the
   grep matched nothing and the recipe TERMed nobody. The recipe's own confirmation scan (descendants at every
   depth) still showed 15022 and 15023. The magistrate therefore applied the recipe's stated intent to the one
   direct child whose command line runs the Codex MCP server, and TERMed it with all of its descendants. The
   census would not have misreported either way: it classifies such processes as own descendants, never foreign,
   and its standing instruction is that owned agents and helpers must be gone before REQUEST, which this
   activation's exit satisfies. This is a doc defect to lane: the recipe should match `codex(@[^ ]+)?
   mcp-server`. It is not cured here, because docs at H are frozen for this night.
2. The F1 notice prose and the F2 `summary.md` sentence stand as ruled in 4158e658 record 01 §2. The harvest
   record must name F2.
3. The tool's notice counter says "Arm attempt 1; prior candidates for this date: none". It counts candidates
   for the calendar date, and the two earlier pilot attempts were dated 09-22. The correction line states the
   true count.

## What happens next (successor)

- The machine stays untouched and agent-free from 06:52 to 09:35 PDT. This activation exits before 06:52,
  after pushing this record. The LaunchAgent is the wake source.
- After `night/courier.sent` appears in the custody root: harvest byte-exact to
  `/Users/edr/night-archive/qpe01-pilot-n1-20260923-0700-harvest-<date>`, verify `SHA256SUMS`, then run
  `python3 -B -m joulewise.evidence_night uninstall --candidate $STAGE` from the clone and record the rc
  (`launchctl list | grep -c joulewise.night` → 0). A clean night is expected to stop with the pre-registered
  cause `observer_floor_above_smallest_holdable_share` (synthesis 35). The harvest record names F2's false
  `summary.md` sentence.
- Then, per 4158e658 record 01 §4: THROUGHPUT-01 item 1(b) A234+A212, then 1(c) A271, with the headline path
  in parallel. After those come NOTICE-SUMMARY-V3-TEXT-01 (A276), where the helper-recipe grep (divergence 1)
  can ride as a doc fix, BLOCK-TWO-DESIGN-01 once the pilot result is in, and A270.
