# Cold gate BFGS-S1-SCOPE-01, erratum: the paired refuter's SF-1 to SF-6 and N-1 to N-3 against amendments 36–41

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory or skill files. **Write the contamination disclosure first.**

**Your working tree** is a detached checkout of `feat/2026-09-26-bfgs-s1-bundles` @ `24b79db3` (S1 rounds 1/1b over main `1417c0c4`). Base for "today": `git archive 1417c0c4 | tar -x -C /tmp/<dir>`.

**Why you are convened.** A cold Fable instance ruled BFGS-S1-SCOPE-01 and wrote amendments 36–41. The paired Opus contract refuter then reported no BLOCKERs, six SHOULD-FIXes and three NITs against it, and proposed two new amendments (42, 43). Every item touches ruled text or S1's ruled behaviour, so they come to a cold judge as an erratum, not to a bench fix. The magistrate has not adjudicated them.
- **SF-1:** amendment 38's R3 shortcut cannot work for the legacy-identity fixtures it names (they carry the MOCK marker, and the reader consults the historical set only when that key is absent).
- **SF-2:** R2 (switch to a digest-bound MOCK config) should be limited to fixtures that were MOCK at base, or powermetrics fixtures could silently become MOCK runs with every assertion green.
- **SF-3:** S1's `authenticate_window_members` turns evidence-missing refusals into custody failures and stops at the first bad member, against amendment 26; the ruled fix order does not repair it (proposed amendment 42).
- **SF-4:** a member's custody failure leaves the window gate without the member's label (amendment 42 has the gate attach it).
- **SF-5:** S1 adds a synthetic `idle_drift_sentinel` stage to the event log of every non-powermetrics, non-MOCK run as the battery span's end marker; no ruling authorises it (proposed amendment 43, with a wall-meter test).
- **SF-6:** amendment 37 turns S1's `test_explicit_mock_not_applicable_refuses_nonmock_config` red and must say it is rewritten.
- **N-1 to N-3:** name the base's included sources outright (floor file 50, RPT001 v2 manifest 6, fixtures 13); make the refuter's reverse sweep the builder's completeness check (it confirms 69 is exact for bundles on disk); double hashing after amendment 39 and R3's patch target.

**Packet** (absolute paths, under `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/20-bfgs-s1/40-coldgate/`):
- `00-charge.md`: the original charge and its authority texts.
- `21-coldgate-fable-ruling.md`: the ruling under review (amendments 36–41).
- `11-opus-contract-refuter.md`: section A holds its independent answers; section B holds SF-1..SF-6 and N-1..N-3 with replacement texts and proposed amendments 42 and 43. Its probe scripts are under `/tmp/opusref-*`.
- `13-astra-execution-seat.md`: an independent Astra execution seat on Q2/Q3 (context; its census is at `/tmp/bfgs-astra/`).
- `../21-triage-report.md`: the Sol triage.

**Rule.** For each of SF-1 to SF-6 and N-1 to N-3:
- UPHOLD or REJECT;
- executed evidence (reproduce the refuter's probes against the real code where you can);
- the exact text change.

Then **restate amendments 36–41 as they stand after your rulings, plus any new amendment (42 onward) you adopt, in full**, each self-contained, and **the S1 fix-round order** (which amendments land in the fix round before round 2, which in round F), so that S1's next brief quotes one self-contained text. Keep intact: custody is never a status; authentication precedes every exclusion decision; `joulewise/battery_float.py` and the S1 pin list stay byte-identical.

**Output.** End with a 5-line plain summary for Ed (technical, no project grounding; gloss every internal id).

**Protocol.**
- A single non-interactive session: no background tasks, no subagents, every probe in the foreground. Edit no repository file. Scratch under `/tmp`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/20-bfgs-s1/40-coldgate/30-erratum/21-coldgate-fable-erratum-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 45 minutes. Mark any probe you could not run as NOT EXECUTED.
