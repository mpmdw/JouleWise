# 01 — Harvest record: rehearsal-20260911 (REHEARSAL_STUB) — 2026-09-11 07:08–07:12 PDT, activation 58a3bcfc

Plan `rehearsal-20260911`, class `REHEARSAL_STUB`, t0 1789120560 (2026-09-11 02:56 PDT), window_max_s 900, courier deadline 1789121760 (03:16 PDT).
Frozen triple at arm: (`rehearsal-20260911`, `/private/tmp/joulewise-rehearsal-20260911-checkout`, `57ddad20226c6921d81a87b9d78e61950c14a74f`).
Custody root `R = /Users/edr/night-custody/rehearsal-20260911`. Harvest by headless activation `58a3bcfc` (launched 07:04:26 PDT, attempt 12) — after 03:16 and outside the 02:45–03:30 belt, but AFTER 07:00 PDT 09-11, so checklist 13 §3a addendum A4 governs P3.

## Verdict: THE NIGHT DID NOT RUN

Two separate failures, both on disk and both already reported to Ed by the courier (Gmail `1a090c8424231111`, 07:03:58 PDT):

1. **02:56:00 driver crash before any census, gate or stub.** `night/launchd.night.err` (807 bytes, born 1789120560.022, sha256 `bc21aec54db914c55a09621d2255c66869bd87cd9231ecb1a9e817e3dbaadb89`):
   `run_night.py:1417` → `from joulewise import arm_readiness` → `joulewise/arm_readiness.py:26: from datetime import UTC` → `ImportError` under `/Library/Developer/CommandLineTools/.../Versions/3.9/lib/python3.9/datetime.py`. The installed plist runs `/usr/bin/env python3` with `PATH=/Users/edr/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin`, which resolves to `/usr/bin/python3` = Python 3.9.6. `night/launchd.night.out` is 0 bytes. No `chain.started`, `chain.exited`, `result.json` or `receipt.json` exists. The stub checkout has no `.venv`; `pyproject.toml` requires Python ≥ 3.11. The `datetime.UTC` import reached `arm_readiness.py` on 2026-09-08 (D-176 seats), after the 09-09 night's head — which is why the 09-09 stub ran under the same interpreter.
2. **07:00:02 dead-man refusal.** The dead-man fired past the completion epoch, ran the agent census (`night/censuses.jsonl`), found an orphaned Claude daemon tree (pid 83102 `claude daemon run --origin transient`, spawned by session pid 55645 which was already gone; children 83155/83180/83195/83220; a `codex mcp-server` 83308/83319 under it), wrote `night/refusal.json` = `REFUSED` / `night_refused_agent_present`, pushed `night-results/20260911` (5226ab7c refusal + census; 37876416 courier record), and the courier sent the email (`courier.sent`: message `1a090c8424231111`, sent_epoch 1789135462, courier pid 38007; `courier.json` attempted 1 / sent true / heartbeat_seen true).

The refusal on record is therefore the DEAD-MAN's census at 07:00, not a night-gate verdict; there is no `night gate verdict=` line in `night.log`.

## Evidence preserved (checklist 13 step 2)

- `lstat` inventory of the ORIGINAL taken 07:08:19 PDT (epoch 1789135699) before any copy: `01-harvest-evidence/lstat-inventory-original.json` (name, type, size, birth, mtime_ns, sha256).
- Byte-exact archive of the whole custody root (including `results-clone/`) OUTSIDE watchdog discovery: `/Users/edr/night-custody-archive/rehearsal-20260911-harvest-58a3bcfc` — `cp -Rp` then `diff -qr` identical.
- Repo copy of every `night/` entry plus `night.log` and `night_plan.json` under `01-harvest-evidence/` with `SHA256SUMS`.
- `night_plan.json` sha256 `a7447608c7c7dc0a3d2a3f6ab56489bd509c9206e8574746c1cf01d113c887bc` = the arm-evidence byte copy (record 123); H = 57ddad20 unchanged.
- Remote `night-results/20260911` verified with `git ls-remote`: tip `378764169bf110348a999e1b2afe8b39a36b48aa`; its six artifacts (`refusal.json`, `censuses.jsonl`, `courier.json`, `courier.sent`, `courier.attempts.jsonl`, `courier.heartbeat`) are byte-identical (`cmp`) to custody. `launchd.night.err` (the traceback) is NOT on the branch — preserved here.
- Inbox: the courier email exists in the account as message `1a090c8424231111` (read back via Gmail at 07:07 PDT); it is the same address the magistrate uses.

Inventory of `R/night/` at 07:08:19 PDT (mtime_ns → PRE-T0 means < 1789120560):

| entry | size | birth | mtime_ns | class |
|---|---|---|---|---|
| launchd.deadman.err | 0 | 1789048801.948226 (09-10 07:00:01) | 1789048801948226143 | PRE-T0, unchanged since the 09-10 firing |
| launchd.deadman.out | 2028 | 1789048801.948138 (09-10 07:00:01) | 1789135475927113682 (09-11 07:04:35) | born pre-t0 (0 bytes at record 30); moved past T0 by the 09-11 dead-man/courier transcript (A4) |
| launchd.night.out | 0 | 1789120560.022 (= t0) | 1789120560022410850 | t0 |
| launchd.night.err | 807 | 1789120560.022 (= t0) | 1789120561076940466 | t0 + 1 s — the traceback (item-6 finding) |
| censuses.jsonl | 3793 | 1789135202.268 (07:00:02) | 1789135202267914617 | post-t0 |
| refusal.json | 2786 | 1789135202.268 | 1789135202268080407 | post-t0 |
| courier.heartbeat | 24 | 1789135221.134 | 1789135221134195325 | post-t0 |
| courier.sent | 142 | 1789135462.373 | 1789135462373342931 | post-t0 |
| courier.attempts.jsonl | 101 | 1789135462.898 | 1789135462898943106 | post-t0 |
| courier.json | 85 | 1789135462.900 | 1789135462900333259 | post-t0 |

`night.log` (415 bytes): line 1 `2026-09-10T07:00:02.092553-07:00 dead-man fired before the night's completion epoch 1789121760; standing down`; line 2 `2026-09-11T07:00:02.268229-07:00 dead-man starting courier`; then `durable record pushed` ×2 and `courier attempt=1 heartbeat=True sent=True`. No entry timestamped in [F+60 s, T0).

## Acceptance disposition: NIGHT-REHEARSAL-01 items 4/5/6

**Item 5 — predicate P1–P4 (cold gate 31, ruling 10 + addendum 11; not re-litigated):**
- P1 HOLDS: exactly one matching line, timestamp 07:00:02.092553 ∈ [F, F+60 s].
- P2 HOLDS: that line precedes the refusal's own log line (`dead-man starting courier`, 09-11 07:00:02.268); no `night gate verdict=` line exists (the gate never ran); no other `dead-man` line between.
- P3 HOLDS UNDER A4: this inventory was taken after 07:00 on 09-11 and the 09-11 dead-man wrote its transcript into `launchd.deadman.out`, so P3 is evaluated on the earlier inventory — record 30 (activation 96bfeca7, 07:30 PDT 09-10: `night/` held exactly `launchd.deadman.out` and `launchd.deadman.err`, both 0 bytes, birth 07:00:01.948) — plus the absence of any pre-t0 driver record here: the only pre-t0 mtime is `launchd.deadman.err` (0 bytes, mtime_ns 1789048801948226143 exactly as predicted), and `launchd.deadman.out`'s birth 1789048801.948138 matches; no `refusal.json`, `courier.json`, `courier.sent`, `result.json` or `receipt.json` existed before t0 (all born 07:00 09-11 or later).
- P4 HOLDS: every other entry has mtime_ns ≥ T0; nothing in the ambiguous band.

> Item 5 MET on rehearsal-20260911 (cold gate 31, ruling 10 + addendum 11): agents installed 04:10:58 PDT 09-10 with `night/` baseline `[]`; the 07:00:02.092 PDT 09-10 dead-man firing wrote only the stand-down line to `night.log` (completion epoch 1789121760), which precedes the 09-11 refusal line at 2026-09-11T07:00:02.268229-07:00; the only pre-t0 entries of `night/` were launchd's two zero-byte stdio handles `launchd.deadman.out` / `.err` (birth 07:00:01.948, mtime unchanged at the record-30 inventory, 0 bytes), installer-rendered `StandardOutPath` / `StandardErrorPath` targets and not driver records; no `refusal.json`, `courier.json` or `courier.sent` existed before t0. Follow-up NIGHT-STREAM-PATHS-01 registered.

**Item 6 — NOT MET.** No green `receipt.json`/`result.json`; the chain never started. The refusal reason `night_refused_agent_present` is the one acceptable refusal, but it is the dead-man's, and it is preceded by a cause the handback says must be cured before any re-arm: the interpreter crash (non-empty `launchd.night.err` at t0). Two findings:
- F1 (BLOCKER, new lane **NIGHT-INTERPRETER-PIN-01**): the installer renders `/usr/bin/env python3` under a PATH that finds the Command Line Tools Python 3.9; the plist must launch an explicit interpreter ≥ 3.11 (the plan's `<measurement_root>/.venv/bin/python`, which the v2 chain/preflight already derive, or an explicit absolute path), and the arm-time preflight must import the driver's modules under the plist's interpreter so this class fails at arm, not at t0. Runbook/handback text that says the stub checkout needs no venv is wrong for any head at or after 2026-09-08.
- F2 (ED-EXTERNAL until an interactive session can act): the orphaned Claude daemon tree pid 83102 (+83155/83180/83195/83220 and codex 83308/83319) is still alive at 07:12 PDT; this activation's attempts to terminate it (SIGTERM; then the daemon's own CLI) were denied by the Claude Code permission classifier ("Interfere With Workloads"). It will refuse every night-gate and dead-man census and re-hold the watchdog inside any future plan span. Ed (or an interactive session) must kill 83102; the children follow.

**Item 4 — PENDING** (no new stage-1 notice exists; nothing is armed).

Never re-arm this plan on this signature. Both night agents were still loaded at harvest (`launchctl list`: `com.joulewise.night` last exit 1, `com.joulewise.night.deadman` 0); uninstall follows in record 02.
