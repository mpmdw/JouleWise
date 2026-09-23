APPROVE WITH CURES

Cold Fable 5.1 final pass on `docs/2026-09-23-4e8918fa-arm` head 1479b50a vs main 9e816173. Run 05:40–05:46 PDT, read-only, foreground only. No blocker. Every load-bearing claim in the diff matches primary evidence; the cures are precision/wording fixes plus one durability fix, safe to apply on the bookkeeping branch before push.

Verified (executed this session):
- `launchctl list | grep joulewise` → night, magistrate, night.deadman; all status 0, none running.
- Installed plist sha256: night `0604c357…5d65`, deadman `d6cd89ff…1a85` = `render/` = record 09.
- Staging: `prepare.json` `39b9382f…f067` and the three render plists equal record 09. `night_plan.json` is no longer in `$STAGE`: `publish-install` moves it to the custody root (`evidence_night.py:1316`); the custody copy and `lifecycle/arm-attempts/000001/plan.json` both hash `6193c6b6…b566`.
- `check.json` sha `70c510f3…6f17` (check id = prefix), armable true, nine checks pass, 05:35:52→05:36:24, top consumer 0.0188 cores over 30.36 s, supervisor 14974 started 1790166863 after H at 1790165590, census foreign_pids [], 14996/15011 classified own.
- `veto.json` sha `fb438855…34ef`, clear/production true, directives `[]`, 05:37:23.
- `install.json` sha `90e7940c…4d9c`, installed/complete, published 05:37:32, notice_accepted `1a0ce4522dbdbf03`, notice_verified false, probe receipt `c21f9ed9…bdc4` = sha of custody `night_probe_receipt.json`.
- Verify stdout exists at `/private/tmp/verify-4e8918fa.json`, sha `7b5ffabb…5d3e`; both labels LOADED, calendars 9/23 07:00 and 10:35, drift false.
- `notice.txt` 5,719 bytes sha `f29633d1…b696`; intended body sha `0c0550bb…c8c8` = notice.txt + exactly the one correction line; that line is byte-equal (629 bytes) in record 01 at 9e816173, the arm record and the intended file.
- Gmail `1a0ce4522dbdbf03` read back: 12:37:12Z, one recipient, subject as recorded, body = notice.txt + the line.
- Canonical HEAD 9e816173, clean; reflog fast-forwards 05:13:10 and 05:26:40, both before 05:34:23.
- Heartbeat epoch 1790166874 (05:34:34); `notice_acknowledged` event 05:35:14 in events.jsonl.
- Divergence 1 confirmed: NIGHT_HANDBACK.md:733 greps the literal `codex mcp-server`; the direct child was `npm exec @openai/codex@0.153.3 mcp-server`. The proposed regex matches it.
- Successor order harvest → uninstall → harvest record → canonical fast-forward (D-183) matches the a022aecc precedent (NIGHT_HANDBACK.md:970) and record 01 §3 step 8. The canonical root is correctly held at 9e816173 until uninstall. Stop cause string at `quiet_predicate_campaign.py:1130`; F2 sentence at `:1441`; A276 in TASK_QUEUE.md:894.

NOT EXECUTED: Gmail read of launch email `1a0ce432c738b78d` (classifier denied). Corroborated only by the notice_acknowledged event.

Findings:

1. should-fix — `docs/process_traces/2026-09-23-activation-4e8918fa/01-arm-record-qpe01-pilot-n1-20260923-0700.md:60`. The verify stdout digest points at a volatile /tmp file. Cure: `cp /tmp/verify-4e8918fa.json docs/process_traces/2026-09-23-activation-4e8918fa/02-verify-stdout.json` before push, and replace "it was held in `/tmp` and is summarised in step 7" with "it is kept as `02-verify-stdout.json` in this directory (sha256 `7b5ffabb…5d3e`) and summarised in step 7".

2. nit — arm record line 47: "6,345 bytes" is wrong; `wc -c` → 6348. Cure: "6,348 bytes".

3. nit — arm record line 49 and the staging row: `arm-attempts/000001/` is under `lifecycle/`. Cure: "`lifecycle/arm-attempts/000001/` holds …". Optionally add at line 44: "`night_plan.json` was moved to the custody root by `publish-install`; digest unchanged."

4. nit — `RUN_STATE.md:13`: "steps 0–8 verbatim between 05:34 and 05:38". Step 8 (record, push, exit) is still in progress. Cure: "steps 0–7 verbatim between 05:34 and 05:38; step 8 is this record and the exit".

5. nit (first-use, `RUN_STATE.md:13`) — "F2's false `summary.md` sentence" precedes its gloss (which sits in the 4158e658 block). Cure: "…and name Sol's finding F2, the false `summary.md` sentence 'Busy cores are recorded covariates and never an exclusion input'".

6. nit — arm record line 71: in record 01 the correction line is indented inside a code fence, so it does not literally "begin" with the phrase. Cure: "…the first line that, after leading whitespace, begins `Correction appended by the magistrate`".

7. informational — a Codex MCP helper tree (pids 15955/15984/15985, 05:40:34) is alive now and belongs to THIS judge session (parent 15939), not the magistrate; it ends with this session. Before exiting, the magistrate should re-run the census pgrep and confirm only its own tree remains, then exit before 06:52. No text change.

Nothing in the diff moves the canonical root while armed; the (A)/(B)/(C) successor sequence is correct and safe.
