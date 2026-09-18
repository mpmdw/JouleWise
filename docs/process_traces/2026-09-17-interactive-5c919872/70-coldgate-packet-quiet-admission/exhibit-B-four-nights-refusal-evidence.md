# Exhibit B — the four consecutive nights that produced zero data (receipt and record excerpts)

Assembled mechanically. Every block below is a verbatim excerpt from a tracked
file in this checkout at commit `a90ab4e8`; the heading above each block gives
the file path and the exact line range. Nothing inside a fence is paraphrased.
Excerpt-completeness note for the judge: the night receipts (`result.json`,
`refusal.json`) are machine-written primary artifacts; the harvest records are
the activation's own reading of those artifacts and are quoted only where the
receipt field itself is the object of the question.

## B1 — 2026-09-13: `night_refused_agent_present`

`docs/process_traces/2026-09-13-activation-c5048879/01-evidence/result.json`,
lines 1–2 and 21–33 (the complete file is 33 lines):

```
{
  "aborted_reason": "night_refused_agent_present",
...
  "census_count": 0,
  "census_hits": [],
  "chain_exit_code": null,
  "chain_sha256": null,
  "ended_epoch_s": 1789293362.595586,
  "ended_monotonic_ns": 718555987103833,
  "plan_id": "d079-epoch-25g83-derivation-n1-20260913",
  "receipt_class": "DIAGNOSTIC_NO_PACK",
  "schema": "joulewise.unattended_night_result.v1",
  "started_epoch_s": 1789293362.5070379,
  "started_monotonic_ns": 718555898556666,
  "verdict": "REFUSED"
}
```

`docs/process_traces/2026-09-13-activation-c5048879/01-equivalence-night-20260913-harvest-record.md`,
lines 24 and 31–32:

```
  `02:56:02.595 night gate verdict=REFUSED reason=night_refused_agent_present
...
  night_refused_agent_present`, `chain_exit_code null`, `chain_sha256 null`,
  `census_count 0`, started 1789293362.507 / ended 1789293362.5956 (89 ms).
```

Elapsed from driver start to refusal: 89 ms. No chain, no capture.

## B2 — 2026-09-15: `night_refused_not_quiet` on the load average

`docs/process_traces/2026-09-15-activation-1acf2aee/01-evidence/result.json`,
lines 1–2 and 21–33:

```
{
  "aborted_reason": "night_refused_not_quiet",
...
  "census_count": 0,
  "census_hits": [],
  "chain_exit_code": null,
  "chain_sha256": null,
  "ended_epoch_s": 1789466163.733711,
  "ended_monotonic_ns": 891357338023500,
  "plan_id": "d079-epoch-25g83-derivation-n1-20260915",
  "receipt_class": "DIAGNOSTIC_NO_PACK",
  "schema": "joulewise.unattended_night_result.v1",
  "started_epoch_s": 1789466163.527894,
  "started_monotonic_ns": 891357132207416,
  "verdict": "REFUSED"
}
```

`docs/process_traces/2026-09-15-activation-1acf2aee/01-equivalence-night-20260915-harvest-record.md`,
lines 23–24, 42–43 and 47:

```
  verdict=REFUSED reason=night_refused_not_quiet detail=load_average predicate
  failed (maximum 2.0)`; `02:56:03.738698 night gate refused`; `02:56:22
...
  vm.loadavg` `{ 2.55 2.57 2.54 }` → `load_1m` 2.55 > `LOAD_MAX` 2.0
  (`joulewise/night_gate.py:1206`). C4 FAIL after refusal. **C5 PASS**:
...
- `night/censuses.jsonl`: one census record, exit 1, empty stdout, no refusal.
```

Observed `load_1m` 2.55 against the fixed maximum 2.0; the agent census was
clean (exit 1, empty stdout). Elapsed: 206 ms.

Lines 115 and 121–122 of the same record (the activation's own cause note):

```
- **F1 (machine, not a defect; not an agent).** The refusal was caused by
...
  refuse); Spotlight `mds_stores` and Time Machine are idle. Until the load is
  below 2.0 at t0 any successor plan refuses on the same predicate, so the
```

## B3 — 2026-09-16: the gate said GO and the night still produced no data

`docs/process_traces/2026-09-16-interactive-5239df1e/01-night-reserve-hang-root-cause.md`,
lines 9–25 (the complete "The stall in one paragraph" section; quoted whole so
it cannot be read selectively). This record is an interactive session's
root-cause write-up; it is quoted here only because the sequence GATE GO ->
reservation -> settle -> capture is the object of question 1 and of the
consult's first missed blocker, and no machine-written artifact states the
eleven-hour interval in one place:

```
## The stall in one paragraph

The night chain of `d079-epoch-25g83-derivation-n1-20260916` started at 09:45:02 PDT and
entered the reservation step (`scripts/reserve_calibration_window_bracket.py --execute`).
Inside the ledger writer lease (lock file born 09:45:02), the readiness pass verifies the
custody of every historical calibration observation by reading and hashing its governed
artifacts. Thirty-eight of the fifty custody locators in the clone's ledger live under
iCloud Drive (`~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/...`), 190
files, 3,333,856,927 bytes. The reads are not time-bounded: `probe_custody` bounds only the
`exists`/`is_dir` probe to two seconds and then runs the inspect callback synchronously and
unbounded on the caller (its own docstring records this as an accepted race). The Python
that performed the reads was spawned by launchd, not by a terminal. macOS gates file access
under iCloud Drive with a Files-and-Folders consent; a process without a stored decision
blocks inside the open call until a person answers the dialog. Nobody was at the machine.
The user consent database changed at 20:52:04; the readiness pass completed and the ledger
rows 77/78 were written at 20:52:06; Ed's interactive `claude` entered the census at
20:52:13 and the driver terminated the chain at 20:52:19.
```

## B4 — 2026-09-17: `night_refused_not_quiet`, `load_1m` 3.66, census EMPTY

`docs/process_traces/2026-09-17-activation-8789ee70/01-n1-20260917-harvest-record.md`,
lines 17–19 (what the driver logged and what the refusal receipt recorded):

```
- `night.log` (556 bytes, copied to `01-harvest-evidence/night.log`): `15:30:01.732 night driver started`; `15:30:01.837 night gate verdict=REFUSED reason=night_refused_not_quiet detail=load_average predicate failed (maximum 2.0)`; `night gate refused`; `durable record pushed` (15:30:10 and 15:32:29); `courier attempt=1 heartbeat=True sent=True`. No dead-man line (19:05 never reached before the uninstall).
- `night/result.json`: verdict `REFUSED`, `aborted_reason night_refused_not_quiet`, `chain_exit_code null`, `chain_sha256 null`, `census_count 0`, `calibration_refusal null`, started 1789684201.7325 / ended 1789684201.8377 (105 ms); `receipt_class DIAGNOSTIC_NO_PACK`; artifacts `night.log` `7f67054f…`, `receipt.json` = `refusal.json` `478fb0bd…` (byte-identical), `censuses.jsonl` `2ac654b6…`.
- `night/refusal.json`: C1 FAIL (not evaluated after refusal); C2 `NOT_APPLICABLE` / `no_pack_by_design`; **C3 FAIL — `load_1m` 3.66 (raw `{ 3.66 3.87 4.06 }`) against the fixed maximum 2.0**; agent census `pgrep -lf codex|claude|t3` exit 1, stdout EMPTY (no agent present); AC attached (battery 85%); HID idle 0; C4 FAIL after refusal; C5 measured `chain_sha256` `f36010d6…` = wrapper digest, `measurement HEAD` at H.
```

Line 25 of the same record — the courier's 15:32 attribution sample and this
session's 18:1x observation, quoted whole to its sentence boundaries:

```
- Load cause (courier sample at 15:32, not part of the gate record): `mediaanalysisd` 114% CPU, `fseventsd` 77%, five `mdworker_shared`; load 4.57 / 4.96 / 4.54. This activation at 18:10–18:19: load 1.29–1.50; `fseventsd` (pid 101) at 85–100% CPU continuously, 1152 CPU-minutes since the 09-15 19:55 boot (≈41% of one core averaged over 46 h), RSS only 24 MB; `mediaanalysisd` and Spotlight idle; `/System/Volumes/Data/.fseventsd` link count 65535 (entry count saturated), directory 11.7 MB, mtime 18:17:44; no user-space files modified in the preceding 2–3 minutes under `/private/tmp`, `$TMPDIR`, `~/code`, `~/night-custody`, `~/Library`, `~/.claude`, `~/.codex`, `/private/var/folders`, `/private/var/db`; zero orphan `fake vllm` fixtures. Root cause is NOT established: attribution needs root (`sudo fs_usage -w -f filesys`, `sudo ls /System/Volumes/Data/.fseventsd | wc -l`, `sudo du -sh` of it) — an Ed action.
```

Line 47 — the activation's registered finding (labelled by its own author
"Findings for the successor (registration, not rulings)"):

```
1. **Machine not quiet for science even below the load gate**: `fseventsd` burning ~0.9 of a core continuously would contaminate every floor of an equivalence night whose tolerances are ~5 J, and the 2.0 load predicate would NOT refuse it (load 1.3–1.5 now). Do not arm until the churn is attributed and cleared (Ed: the three root commands above; the 09-15 restart cleared it for under two days). Candidate lane NIGHT-GATE-LOAD-ATTRIBUTION-01: the not-quiet refusal and the arm desk block should record the top CPU consumers (`ps -Ao pid,pcpu,command -r | head`) so a refusal names its cause; any per-process quietness rule goes to the cold gate.
```

## B5 — what the four nights have in common, stated only as the receipts state it

| Night | `aborted_reason` | Observation in the receipt | Capture |
|---|---|---|---|
| 2026-09-13 | `night_refused_agent_present` | census non-empty | none (`chain_sha256 null`) |
| 2026-09-15 | `night_refused_not_quiet` | `load_1m` 2.55 vs max 2.0; census empty | none (`chain_sha256 null`) |
| 2026-09-16 | (no refusal; verdict GO) | reservation blocked on file-consent | none |
| 2026-09-17 | `night_refused_not_quiet` | `load_1m` 3.66 vs max 2.0; census empty | none (`chain_sha256 null`) |

Contrary evidence the judge should weigh: two of the four nights (09-13 and
09-16) were NOT lost to the load predicate. 09-13 was a census refusal, which
the consult's proposition 6 would keep terminal; 09-16 was a custody-read hang
already cured by PR #350 and unrelated to admission. Only 09-15 and 09-17 are
load-average losses.
