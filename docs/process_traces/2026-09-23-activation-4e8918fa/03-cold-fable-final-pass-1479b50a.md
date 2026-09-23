APPROVE WITH CURES

Cold Fable 5.1 final pass on `docs/2026-09-23-4e8918fa-arm` head 1479b50a vs main 9e816173. Run 05:40–05:46 PDT, read-only, foreground only. No blocker. Every load-bearing claim in the diff checks out against primary evidence; the cures below are wording/precision fixes and one durability fix, all safe to apply on the bookkeeping branch before push.

Verified (evidence executed this session):
- `launchctl list | grep joulewise` → `com.joulewise.night`, `com.joulewise.magistrate`, `com.joulewise.night.deadman`, all status 0, none running.
- Installed plist sha256: night `0604c357…5d65`, deadman `d6cd89ff…1a85`; both equal `render/` and record 09.
- Staging: `prepare.json` `39b9382f…f067` and the three render plists equal record 09. `night_plan.json` is no longer in `$STAGE`: `publish-install` moves it to the custody root (`evidence_night.py:1316`); custody copy and `lifecycle/arm-attempts/000001/plan.json` both hash `6193c6b6…b566` = record 09.
- `lifecycle/check.json` sha `70c510f3…6f17` (check id = prefix), armable true, fake_launchctl false, all nine checks pass; started 05:35:52, finished 05:36:24; machine_quiet top consumer 0.0188 cores over 30.36 s; supervisor pid 14974 started 1790166863 after H at 1790165590; census foreign_pids [], descendants 14996/15011 (pdf MCP) own.
- `veto.json` sha `fb438855…34ef`, clear true, production true, directives `[]`, finished 05:37:23.
- `install.json` sha `90e7940c…4d9c`, outcome installed, phase complete, published 05:37:32, notice_accepted `1a0ce4522dbdbf03`, notice_verified false, probe receipt `c21f9ed9…bdc4` = sha of custody `night_probe_receipt.json`.
- Verify stdout found at `/private/tmp/verify-4e8918fa.json`, sha `7b5ffabb…5d3e` as recorded; both labels LOADED, calendar 9/23 07:00 and 10:35, baseline drift false.
- `notice.txt` 5,719 bytes sha `f29633d1…b696`. Intended body file sha `0c0550bb…c8c8`; `diff` shows it is notice.txt plus exactly the one correction line. That line is byte-equal (629 bytes) in record 01 at 9e816173, the arm record, and the intended file.
- Gmail `1a0ce4522dbdbf03` read back (PLAIN_TEXT): sent 12:37:12Z, to `claude2.glaring610@passmail.net` only, subject as recorded, body = notice.txt + the correction line.
- Canonical root HEAD 9e816173, porcelain clean; reflog fast-forwards 05:13:10 (→26fb4280) and 05:26:40 (→9e816173), both before the supervisor start 05:34:23.
- Heartbeat line `14978 4e8918fa-… 1790166874` (05:34:34) per record; `notice_acknowledged` event at 05:35:14 in events.jsonl.
- Divergence 1 confirmed: NIGHT_HANDBACK.md:733 greps the literal `codex mcp-server` on direct children; the direct child was `npm exec @openai/codex@0.153.3 mcp-server`, which does not contain that literal. Proposed regex matches it.
- Successor ordering (harvest → uninstall → harvest record → canonical fast-forward under D-183) matches the a022aecc precedent at NIGHT_HANDBACK.md:970 and record 01 §3 step 8 ("must not move after the arm"). The canonical root is correctly told to stay at 9e816173 until uninstall. Stop cause string exists at `quiet_predicate_campaign.py:1130`; F2 sentence at `:1441`; A276 registered in TASK_QUEUE.md:894.

NOT EXECUTED: Gmail read of the launch email `1a0ce432c738b78d` (auto-mode classifier denied the read). Corroborated only by the notice_acknowledged event.

Findings:

1. should-fix — `docs/process_traces/2026-09-23-activation-4e8918fa/01-arm-record-qpe01-pilot-n1-20260923-0700.md:60` (verify stdout "held in /tmp"). The file exists now at `/private/tmp/verify-4e8918fa.json` with the recorded sha, but /tmp is volatile and the digest becomes unverifiable after reboot. Cure: copy it into the trace dir before push and cite it: `cp /tmp/verify-4e8918fa.json docs/process_traces/2026-09-23-activation-4e8918fa/02-verify-stdout.json`; replace "it was held in `/tmp` and is summarised in step 7" with "it is kept as `02-verify-stdout.json` in this directory (sha256 `7b5ffabb…5d3e`) and summarised in step 7".

2. nit — arm record line 47 (step 4, send notice): "6,345 bytes" is wrong. Evidence: `wc -c` → 6348. Cure: "6,348 bytes".

3. nit — arm record line 49 (step 6) and the "Frozen triple" staging row: `arm-attempts/000001/` lives under `lifecycle/`. Cure: "`lifecycle/arm-attempts/000001/` holds …". Optionally add to line 44 (step 1): "`night_plan.json` was moved to the custody root by `publish-install`; its digest is unchanged."

4. nit — `RUN_STATE.md:13`: "Ran 4158e658 record 01 §3 steps 0–8 verbatim between 05:34 and 05:38." Step 8 (arm record, commit, push, exit) is still in progress at 05:46. Cure: "steps 0–7 verbatim between 05:34 and 05:38; step 8 is this record and the exit".

5. nit (first-use, RUN_STATE.md:13) — "F2's false `summary.md` sentence" is used before any gloss in the 4e8918fa block; the definition sits in the 4158e658 block below. Cure: "…and name Sol's finding F2, the false `summary.md` sentence 'Busy cores are recorded covariates and never an exclusion input'."

6. nit — arm record line 71: "extracted mechanically … by the first line beginning `Correction appended by the magistrate`". In record 01 the line is indented three spaces inside a code fence; it begins with whitespace. Content is byte-equal after stripping. Cure: "…by the first line that, after leading whitespace, begins `Correction appended by the magistrate`".

7. informational — a Codex MCP helper tree (pids 15955/15984/15985, started 05:40:34) is alive now; it belongs to THIS cold judge session (parent 15939), not to the magistrate. It ends when this session ends. Before its own exit the magistrate should re-run `pgrep -lf '[c]odex|[c]laude|[t]3'` and confirm nothing but its own tree remains, then exit before 06:52 as recorded. No text change required.

Nothing in the diff instructs the canonical root to move while armed; the (A)/(B)/(C) successor sequence is correct and safe.
