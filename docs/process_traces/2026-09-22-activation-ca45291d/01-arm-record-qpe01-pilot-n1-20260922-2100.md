# Activation ca45291d — arm record for qpe01-pilot-n1-20260922-2100 (2026-09-22, ARMED)

Headless magistrate activation `ca45291d-5492-447a-896e-d9155965b8cd`, spawned by the
watchdog at 20:08:07 PDT (attempt 80) after activation 59857fe5 exited at 20:05 under
D-183 (its resident supervisor pre-dated the arm head). Every step below was executed by
this activation between 20:08 and 20:13 PDT; command outputs are under
`/tmp/*-ca45291d.out` for this boot and, durably, in the staging `lifecycle/` records.

## Authority

- Cold ruling 21 (bounded round 2 of cold gate #3, sealed in packet 08 of activation
  59857fe5): the arm may proceed on the raw replay rows; conditions C1 (addendum 24b,
  done by 59857fe5), C2 (notice links, discharged below), C3 (driver amendment PR after
  the arm, still owed).
- RUN_STATE top block on main `48842569` (successor's exact arm procedure, steps 0–9).
- Ed's NO on any thread overrides at every step; none observed (Gmail search of the
  last day for NO/stop/stand down/directive/NIGHT returned nothing inbound; no owner
  directive issue open; no `standdown.request`, no `STOP`).

## Frozen triple

| Field | Value |
|---|---|
| plan_id | `qpe01-pilot-n1-20260922-2100` (attempt 2 for this date; prior candidate `qpe01-pilot-n1-20260922-0217`) |
| repo_head = measurement_head = H | `dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432` |
| measurement_root (clone) | `/Users/edr/JouleWise-measurement-20260922-2100-1790136000-dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432-qpe01-pilot-n1` (HEAD verified = H) |
| custody root | `/Users/edr/night-custody/qpe01-pilot-n1-20260922-2100-20260922-2100-1790136000-dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432` |
| staging | `/Users/edr/night-plan-staging/qpe01-pilot-n1-20260922-2100-20260922-2100-1790136000-dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432` |
| t0 | 2026-09-22 21:00:00 PDT = epoch 1790136000 |
| install close (excluded) / REQUEST | 20:50:00 / 20:52:00 PDT |
| TERM / KILL | 20:54:00 / 20:55:00 PDT |
| window end / courier deadline | 23:30:00 / 23:35:00 PDT (window_max_s 9000) |
| daily dead-man | 2026-09-23 00:35:00 PDT |
| registration | `pilot_protocol_v2.json` sha256 `2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1` |
| plan sha256 | `280c811fbc27369b5c4219d3eece2e1b47f423e5d51fa4c36b9566d87e34939b` |
| code frozen since | replay merge `4f8bc36d`: `git diff --stat 4f8bc36d..dbd5cd59 -- joulewise scripts configs` prints nothing (run 20:14 PDT in this worktree) |

## Executed steps (all from `/Users/edr/code/JouleWise`, `python3 -B -m joulewise.evidence_night …`)

| # | Step | Result |
|---|---|---|
| 0 | heartbeat; `env | grep EVIDENCE_POWER_RECORDER` | heartbeat written (pid 15976); env grep empty (rc 1) |
| 0 | `launchctl list | grep joulewise` before | only `com.joulewise.magistrate`; no night plist on disk |
| 0 | launch email to Ed | Gmail `1a0cc3d69e48eec4` (20:09); `notice.ack` written |
| 1 | staged plan reuse | time 20:09 < 20:45 → the 59857fe5 staging (prepare sha256 `f97788d6…`) checked as-is; no re-prepare |
| 2 | terminate own MCP helpers | ROOT 15976 (`claude -p`); TERM 15991 (`node /opt/homebrew/bin/codex mcp-server -c model="gpt-5.6-sol" -c model_reasoning_effort="high" -c mcp_servers.claude.enabled=false`) and its descendant 15993 (vendor `codex mcp-server` binary); descendant scan for `codex mcp-server` empty afterwards. Nothing outside ROOT's subtree touched. |
| 3 | `check --candidate $STAGE` | rc 0, `armable: true`, `fake_launchctl: false`, eight checks pass (`sealed`, `night_agents`, `canonical` [fast_forward null — canonical `48842569` already contains H], `supervisor` [pid 15972 started 1790132887 > H arrival 1790132149], `courier`, `retained_roots`, `census`, `retry`); check id `3f8ccb3136fd` at 20:10:35 |
| 4 | `notice --candidate $STAGE` | rc 0; body == `lifecycle/notice.txt` (5743 bytes, sha256 `859aaf9f8fbfb2086a92abc7a63c50e94fe3b04131a4497947c78b04f576c843`) |
| 5 | send notice | Gmail `1a0cc3fa26b13a44` accepted ≈20:11:30, one recipient `claude2.glaring610@passmail.net`, no cc; subject and body VERBATIM from `notice.txt` plus exactly one appended line (below) |
| 6 | `veto --candidate $STAGE` | rc 0, `clear: true`, `production: true`; NO / STOP / standdown / directives all clear; `non_owner_directives: []` (20:12:12) |
| 7 | `publish-install --candidate $STAGE --notice-accepted 1a0cc3fa26b13a44` | rc 0, `outcome: installed`, `installed: true`, `phase: complete`, published 20:12:28 (epoch 1790133147.9), 22 min before install close; pre-publication both labels ABSENT; probe receipt sha256 `e1457eac…`; `arm-attempts/000001/` holds `plan.json`, `baseline.json`, `install.json`, `veto-at-publication.json`; `notice_verified: false` is the tool's standing statement that it cannot compare sent bytes (it verifies only id-unused + notice newer than sealed artefacts) |
| 8 | `verify --candidate $STAGE` | rc 0: `com.joulewise.night` LOADED, plist sha256 == render sha256 `f2d6c9e8…`, calendar Month 9 Day 22 Hour 21 Minute 0; `com.joulewise.night.deadman` LOADED, `14b5c767…`, calendar Hour 0 Minute 35; baseline drift false (20:12:53) |
| 9 | `launchctl list | grep joulewise` | `com.joulewise.night`, `com.joulewise.magistrate`, `com.joulewise.night.deadman` (all status 0, not running) |

Attempt numbering note: the notice says "Arm attempt 2" (second candidate for the date)
while the staging directory numbers this plan's own first publication
`arm-attempts/000001`; both are the tool's own counters.

## The one appended line (ruling 21 C2), pasted exactly as sent

```
Ruled pre-arm bench replay (cold gate #3 ruling 10 §Q7, cold ruling 21): docs/process_traces/2026-09-22-activation-59857fe5/24-bench-replay-start-drift.md sha256 609d302ebda1dbd59237211fb2231b6fd8f1a52869b7b567a3be29fb0e2108bb + 24-bench-replay.json sha256 1882e92b3053eedcedf7437e2113a38b787a390f9022eac5b96ae00f7c6b0a58 + 24b-bench-replay-addendum-ruling-21.md + 08-coldgate-packet-a267-merge-transaction/21-coldgate-fable-replay-verdict-ruling.md at main dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432 — twelve chain-level start_drift_s, max 0.352 s ≤ 0.5 s; replay executed at merge 4f8bc36d, D-138 transaction 7eb53eff is its ancestor (P7.3).
```

All four files are tracked at `dbd5cd59` (verified with `git cat-file -e`); the two sha256
values were computed at the bench at 20:10 PDT. The addendum's sha256 is
`2b8b37682c9f1e8709543d02ced1c0bcf3c7debcb1d739f970253fa953fb8107` and ruling 21's is
`52f33f60311b0b521f48fe40eaf9cb90ae92996e8702f2d406a32c40ba21f175` (not in the sent line).

## Divergences recorded, not cured (docs frozen at H)

1. `docs/process/NIGHT_HANDBACK.md` §"Where the results are" / §"Next lane" name the
   custody suffix `qpe01-pilot-n1-20260922-2030` (the runbook's planned t0); the night
   that ran is `…-2100`. The Executed block for this plan id, not those sections, names
   the night; the courier reads the handback from the clone at H, so the mismatch is a
   reporting matter only. Same shape as the dc2237d5 arm.
2. The generated notice says "The 7,800-second program fits inside 9,000 seconds"; the
   runbook and handback §"Purpose" derive 8,020 s (600 settle + 11 × 620 pitch + 600).
   The notice text is generated by `render_notice`, sent verbatim by rule; the plan's
   `window_max_s` 9000 bounds either figure. Lane for the successor: reconcile the notice
   template's span arithmetic (docs/template only, never the frozen chain).
3. Notice `notice_verified: false` (see step 7).

## What happens next (successor)

- Machine untouched and agent-free from 20:52 to 23:35 PDT; this activation exits before
  20:52 after pushing this record. The LaunchAgent is the wake source.
- After `night/courier.sent` in the custody root: harvest byte-exact to
  `/Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-<date>`, verify
  `SHA256SUMS`, then `python3 -B -m joulewise.evidence_night uninstall --candidate $STAGE`
  from the clone (record rc; `launchctl list | grep -c joulewise.night` → 0).
- Then the driver-amendment PR (ruling 21 C3: re-run `verdict()` on `24-bench-replay.json`
  to PASS before any later artifact), the notice-span reconciliation lane, and the
  handback per-night sections for the next plan. A268 waits on Ed. No Codex seats
  (quota until ≈ 09-24 03:00 PDT).
