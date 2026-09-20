# Record 01 — pilot night one `qpe01-pilot-n1-20260920` harvest, uninstall, and ruling (activation 21752427, 2026-09-20 03:19–03:40 PDT)

## §1 Launch

Watchdog attempt 67 spawned activation `21752427-d48d-4016-ba0b-7aa0e250a328` at 03:19:26 PDT after the plan span closed (predecessor cf813934 exited `usage_exhausted` before REQUEST 00:32; watchdog FENCED through the span, HOLD_CENSUS 00:43:45–00:53:48 on the night's own driver pid 79018). Heartbeat written first (pid 80253). Launch email Gmail `1a0be55c9410327b` to the single address, carrying the pending notice `transition-279-hold_census`; `notice.ack` written after acceptance. No directive issues open. `standdown.request` absent at every slice boundary in this record.

## §2 Verdict (executed evidence, read at the bench 03:20 PDT from the custody root)

- `night.log`: 00:40:01.69 driver started; gate GO; chain digest verified; **00:50:04.09 verdict=ABORTED**; results pushed to `night-results/qpe01-pilot-n1-20260920` at 00:50:11 and 00:52:13; courier attempt 1 sent at 00:52:11.
- `night/result.json`: verdict `ABORTED`, `aborted_reason night_aborted_agent_present`, `chain_exit_code 2`, `census_count 21`, ONE census hit at monotonic 112165.100 (00:50:03): `79146 /usr/bin/pgrep -lf codex|claude|t3`; receipt class `DIAGNOSTIC_NO_PACK`; 22 artefacts with digests; two refusal documents.
- `night/refusal-01.json`: `night_refused_agent_present`, "agent census refused while the chain was running", evidence = the single pgrep line above. `night/refusal.json`: `night_probe_error`, "evidence chain refused: InterruptedError: evidence chain signal 15" (the chain's record of the driver's SIGTERM).
- `night/evidence_outcome.json`: outcome `refused`, `envelopes_attempted 0`, `cleanup_proven true`. `evidence_cleanup.json`: six process groups (79121 recorder, 79122 collector, 79133 power, 79142/79143/79154 probes) all absent, residue empty, no signal errors. `evidence_busy_cores.jsonl`: one row, `admits_nothing true` (top died with SIGTERM).
- `night/evidence/summary.json`: status INCONCLUSIVE, retained 0 of 12, pairs null, block two "no decision", `cutoff_authority false`. `evidence_envelopes.jsonl` does not exist (no envelope completed). Envelope 1 `session.json`: error "collector termination requested", interior partial, native samples 0, reason "clock anchor unresolved" — a consequence of the 2 s life of the envelope, not a separate anchor defect (the consult in record 03 is asked to confirm).
- `night/receipt.json` (00:40:01): C1 PASS, C2 NOT_APPLICABLE, C3 PASS (census empty, HID idle 0, AC 80 %, load 0.36), C4 PASS, C5 chain digest `570dba7e…` bound at `cd10ce9d`. Launchd streams: `launchd.night.err` EMPTY; `launchd.night.out` = the courier's closing summary (2132 bytes).
- Courier: Gmail `1a0bdccfcb6932d4` sent 00:52 to the single address; `courier.sent` records verdict ABORTED, chain exit 2, courier pid 79228. The courier's reading (census race, not a foreign agent) matches this record's §3.
- Results branch: `origin/night-results/qpe01-pilot-n1-20260920` = `cba2ea01` on `6df1d027`; all 24 files under `docs/process_traces/night-results/qpe01-pilot-n1-20260920/` are BYTE-IDENTICAL to `night/` (`cmp`, this activation, 24/24 SAME).

## §3 Root cause (magistrate's reading; consult 03 is asked to refute it)

The driver's 30 s census and the chain's per-round census worker both run the identical `pgrep -lf codex|claude|t3`. `pgrep -f` matches the full command line, and the pattern's own text contains `codex` and `claude`, so two censuses overlapping in time see each other. The settle's 21 censuses were clean because no chain census runs during settle; envelope 1's round-1 census worker (pid 79142, started 00:50:03) spawned its pgrep (pid 79146) in the same instant as the driver's 22nd census. No codex, claude or t3 process exists in any record. The abort is a self-match, not a foreign agent, and it recurs on every evidence night with probability proportional to the overlap of two millisecond-scale pgreps per 600 s round. `tests/test_gen_derivation_night.py::test_a_census_substring_anywhere_in_the_night_refuses` already documents the static form of this class (a plan id containing the words); the concurrent form was not covered.

## §4 Harvest (record 85 step 5)

`cp -Rp` of the whole night root (including `results-clone/`) to `/Users/edr/night-archive/qpe01-pilot-n1-20260920-harvest-20260920` at 03:21 PDT; `SHA256SUMS` (8,494 files) written from the copy and checked against the LIVE root: **8494 OK, 0 non-OK** (`SHA256SUMS-check-against-live-root.txt` beside it). Nothing in the night root was moved, altered or deleted. The root and the clone `/Users/edr/JouleWise-measurement-20260920-qpe01-pilot-n1` (at `cd10ce9d`, tree clean) are RETAINED: a raw powermetrics plist and the round-1 identity records exist under `evidence/envelope-01/raw/`, and the root is the primary evidence for the census defect. Retirement is a later decision, not this record's.

## §5 Uninstall (documented post-completion step)

`scripts/install_night_agent.sh --plan <night root>/night_plan.json --uninstall` run FROM the clone at 03:22:27 PDT: **rc 0** on the first invocation (silent); `launchctl list | grep -c joulewise.night` → 0; `~/Library/LaunchAgents` holds only `com.joulewise.magistrate.plist`; clone tree clean. Done 53 minutes before the 04:15 dead-man minute. **NOTHING IS ARMED.** rc preserved at `<archive>/uninstall.rc`.

## §6 Ruling (magistrate, within its authority; no process rule touched)

1. The night is a `DIAGNOSTIC_NO_PACK` abort with zero retained envelopes; there is nothing to size block two from ("no decision" stands). No quiet-admission threshold is activated.
2. The refusal cause `night_refused_agent_present` is on the NIGHT_HANDBACK cold-gate path for a same-plan retry; no same-plan retry is sought. The successor night is a NEW plan authored only after the census self-match cure merges under the normal gates (record 03 consult → implementation seat → refuters → PR with the twelve-row ledger). Re-arming on the same code would reproduce the abort.
3. Ed's standing objective (time to real windows back-to-back, mock-free rehearsals) makes the cure the critical path; the Linux fixture fix-forward (record 02) runs in parallel because it is independent.

## §7 Findings for the successor

1. The three census sites (driver, chain per-round census, t0 readiness probe) plus the watchdog's census all share the literal; the cure must cover every site or the race merely moves.
2. The watchdog relaunch cadence in the hour before t0 (three launches, three emails on 09-19) remains a cost; an activation with nothing to do should hold until ≈ t0 − 20 min (cf813934's lesson).
