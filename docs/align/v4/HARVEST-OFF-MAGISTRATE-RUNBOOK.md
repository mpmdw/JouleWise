# Harvest off the MBP: magistrate runbook (R17)

- **Authority:** RUN_STATE 228, lead ruling R17.
- **Design:** `docs/align/v4/HARVEST-OFF-MERGED.md`.
- **Record and packet contract:** `docs/align/next_arm_packet.md`.

This runbook covers one window k, from terminal completion to the arm of k+1. It also covers what record k+1 must carry for k, and the first-time native sweep.

**Never** pack, hash, transfer, triage, harvest or run a desk on the MBP while a window measures, or during the display/quiet dwell. Every MBP step below ends before the dwell starts. The quiet observation's `active_work` must be `[]`, and the arm refuses otherwise (`quiet_start_state`).

## 0. Names used below

| Name | Meaning |
|---|---|
| `K` | the attempt id of the window just finished, exactly as in its record (`C3`, `C3#2`, `T1`, ...) |
| `S` | the window's session root, an absolute path. It must be **the same path on the MBP and on the Air** |
| `M` | the measurement checkout, at the same absolute path, commit and `.venv` on both machines |
| `PY` | `$M/.venv/bin/python -B` |
| `RUN` | `$PY $M/scripts/align_v4_harvest_off.py` (every subcommand prints one JSON line; exit 1 = refusal) |
| `DESK_REPO` | the records repository (`records/<K>/...`, `series/state.json`), pushed to `refs/remotes/origin/records` |
| `OUT` | an empty per-window staging directory, e.g. `~/code/CapstoneProject/jw-wt/offload/$K` |

## 1. MBP, right after terminal completion and finalize (before cool-down counts as quiet)

**1a. Finalize as today** (custody hashes, record artifacts). Unchanged.

**1b. Write the record-bound tree manifest.** Its SHA-256 goes into record k.

```sh
$RUN finalize-manifest --session-root "$S" --out "$OUT/finalized_manifest.json"
# prints {"finalized_manifest": ..., "sha256": H, "entries": n}
shasum -a 256 "$OUT/finalized_manifest.json"     # == H: the file is canonical bytes
```

**1c. Pack the verified compressed copy.** The calibration ledger the window appended travels with it.

```sh
$RUN pack --session-root "$S" --out "$OUT/offload" --finalized-manifest "$OUT/finalized_manifest.json"
cp "$OUT/finalized_manifest.json" "$OUT/offload/"
```

**1d. Offload** `$OUT/offload/` to the Air during cool-down. Use the air-offload lane's authenticated route (`ops/2026-11-08-air-offload`, under its cool-down lease). The payload is about 0.3-2.6 GB.
- The transfer must finish before the dwell starts.
- The MBP originals stay until the lane's two verified copies exist; nothing here deletes them.

## 2. Air, during the MBP cool-down

**2a. Restore** at the same path, record-bound. `H` is the digest from 1b:

```sh
$RUN unpack --offload "$OUT/offload" --finalized-manifest "$OUT/offload/finalized_manifest.json" \
            --finalized-sha256 "$H"
```

**2b. Run the light triage** and write the record source:

```sh
$RUN triage --session-root "$S" --window-id "$K" --out "$OUT/light_triage.json"
# add --ladder-recorded only when a U1-U3 failure's escalation step is already recorded for the next plan
```

**2c. Return** `light_triage.json` to the magistrate's desk repository by the same authenticated route.

## 3. Magistrate, the record step for window k (before the arm of k+1)

Record k is the index `records/$K/record.json` (schema `joulewise.align_v4.window_record.v1`), committed and pushed as today. The full field list is in `next_arm_packet.md` (Committed inputs). R17 changes only the following.

**Full desk NOT due** (the previous window is not W1, and the arm's artifact-set digest equals the last desk-passed one):
- `sources.light_triage` → `records/$K/evidence/light_triage.json`, the file from 2b, byte for byte.
- `sources.desk` → a placeholder that marks the desk as running off the MBP:

  ```sh
  $PY -c 'import json,sys; print(json.dumps({"plan_id": sys.argv[1], "status": "running_off_mbp"}, sort_keys=True))' \
      "$PLAN_ID" > "$DESK_REPO/records/$K/evidence/desk.json"
  ```
- `sources.pilot` and `sources.exclusions` are **omitted**.
- Add `records/$K/evidence/finalized_manifest.json` (from 1b) to `raw_evidence`, as `{"path": ..., "sha256": H}`.
- Series ledger: `last_passed_record` stays on the last record whose desk passed (see §4).

**Full desk DUE** (previous window W1, or code/config changed since the last desk-passed state): **do not arm on the light triage.**
- Wait for the Air's `desk` and `final` (§5).
- Commit record k with its own `sources.pilot` (`$S/PILOT.json`), `sources.desk` (`$S/desk.json`) and `sources.exclusions` (`$S/archive/derived/exclusions.json`).
- `light_triage` is optional in that case.

Then build the packet as today:

```sh
$PY $M/scripts/align_v4_next_arm_packet.py --repo "$DESK_REPO" \
  --record-commit "$RECORD_K_COMMIT" --record-path "records/$K/record.json" \
  --series-commit "$SERIES_COMMIT" --series-path series/state.json \
  --pushed-ref refs/remotes/origin/records --output "$OUT/next-arm.json"
```

- `checks.member_eligibility.basis` starts `R17 provisional`.
- `checks.full_desk_gate.status` is `deferred`.
- The last `calibration_windows` row is `provisional`.

## 4. Record k+1 carries k's final sources

When the Air's full desk for k has finished (§5), record **k+1** gets `previous_final`:

```json
"previous_final": {
  "record_sha256": "<sha256 of records/K/record.json, i.e. record k's index bytes>",
  "sources": {
    "pilot":      {"path": "records/K1/previous-final/pilot.json",      "sha256": "..."},
    "desk":       {"path": "records/K1/previous-final/desk.json",       "sha256": "..."},
    "exclusions": {"path": "records/K1/previous-final/exclusions.json", "sha256": "..."}
  }
}
```

- The files are `$S/PILOT.json`, `$S/desk.json` and `$S/archive/derived/exclusions.json` from the Air desk on window k, byte for byte.
- If k's desk passed, the series ledger's `last_passed_record` becomes `{commit, path, sha256}` of record k plus `"final_record": {commit, path, sha256}` of record k+1.
- If k's desk is not finished by record k+1, commit k+1 without `previous_final`. The arm of k+1's successor then refuses (§6) until a later record carries it. **R17's bound:** window k must be final before the arm of k+2.

## 5. Air, during window k+1: restore → harvest → desk → final → reduce

The Air must be otherwise quiet: no Sol seats; renice others. The desk-verdict child has a wall budget; a time-out there is a re-run, not a result.

```sh
$RUN desk  --session-root "$S" --workers auto [--sweep "$SWEEP/SWEEP.json"]   # harvest + full v4 desk
$RUN final --session-root "$S" --window-id "$K"                               # final eligibility row
$RUN reduce --session-root "$S" --out "$OUT/reduced" --workers 2              # columnar PM + per-turn tables
```

- **`desk`** writes `$S/PILOT.json`, `$S/desk.json` and `$S/archive/`.
  - `--workers auto` uses min(free cores, free memory ÷ the measured per-worker peak).
  - Pass the sweep receipt once it exists (§7). Without it the peak defaults to 8× the window's largest raw plist.
- **`final`** refuses unless the harvest completed. Its rows must be a subset of the light triage's provisional rows. If not, stop and escalate to the lead: the proof says this cannot happen.
- **`reduced/`** is outcome-bearing (energies) and is restricted like `withheld/`. Its `MANIFEST.json` digests and row counts are structure-only. Each `<run_id>/turns.json` equals PILOT.json (`turn_table.equal_to_pilot`); check this before any analysis reads tables instead of bundles.
- Hand the three final files to the magistrate for record k+1 (§4).
- Prune the restored `$S` on the Air only after record k+1 (or k) with the final sources is pushed. The MBP originals follow the air-offload lane's retention rule.

## 6. What refuses, and when

| Where | Refusal | Meaning and action |
|---|---|---|
| `finalize-manifest`, `pack` | `terminal record absent` | Not terminal. Wait for B1 completion. |
| `pack` | `packed tree differs from the finalized record manifest` | Something changed the session after finalize. Find it; do not repack over it. |
| `pack` | `unsupported file type` | A FIFO or device in the session. Investigate. |
| `unpack` | `measurement checkout mirror differs` | The Air checkout (head, clean incl. untracked, interpreter and packages) is not the MBP's. Fix the mirror. |
| `unpack` | `committed digest` / `offload manifest differs` / `payload digest mismatch` / `restored tree differs` | The copy is not the finalized record. Re-transfer. |
| `unpack` | `already exists` / `differs from the recorded source root` | Byte identity needs the same, empty path. |
| `unpack` | `append-only` | The Air ledger is not a prefix of the window's. Do not restore. Escalate. |
| `triage` | `light triage refused: ...` | Registration evidence (U3 bar, WP19) is missing. The full desk would refuse too. |
| `desk` (harvest) | exit 3 `NotReady chain_process_group_alive` | The MBP chain's pgid collides with an Air process (about 1%). Re-run. |
| `final` | `needs a completed harvest` | The desk did not finish its harvest. |
| packet / arm | `R17: final eligibility of K must be recorded before the arm of the window after next` | k is still provisional at the arm of k+2. Commit `previous_final` (§4). |
| packet / arm | `member_eligibility` failed with no final sources | The full desk is due (after W1 or a code/config change). Wait for §5 and commit the final sources in record k. |
| packet / arm | `previous_final must name this record ...` | `record_sha256` or the source set is wrong. |
| packet / arm | `a finally excluded member of K is in the pool` | Correct `pool_members` in the series ledger. |
| packet / arm | `light triage source missing or for another window` | `light_triage.json` names another attempt id. Use `--window-id "$K"` exactly. |
| packet / arm | `committed desk provisional counts (series_desk_row) missing` | The light triage or PILOT lacks the series desk row. Re-run triage on the series session. |
| series binder | `R17: window k final eligibility must be recorded before the arm of k+2` | Same rule, applied to the series history. |
| `calibration_stop` | `pending_final_eligibility` | Eight counted windows with one still provisional. The test arm waits for the final row. |

## 7. Native `sweep` on the first real restored window (once)

Run it on the Air with the restored `$S`, during a window, with the Air otherwise quiet. It needs disk for 5 separate archives on top of the restore. The sources are cloned with `cp -c`, so mainly `withheld/` and `derived/`. Check `df` first: there is 49 GB free now, and a window is 18.6-26.4 GB.

```sh
$RUN sweep --session-root "$S" --out "$OUT/sweep" --workers 2,4,6,8,10
# SWEEP.json: per worker count: exit, wall_s, peak_child_rss_bytes (the per-worker peak); profile.jsonl per run
```

Then use it for every later desk: `--workers auto --sweep "$OUT/sweep/SWEEP.json"`.
- Record the knee (the fastest count whose peak fits) in RUN_STATE.
- Keep `SWEEP.json`. It is structure only (times, bytes), with no outcome values.
- The sweep's five archives are engineering copies. Delete them after; they are never record sources.

**Optional native identity check (N2).** On a window whose harvest also ran on the MBP, compare the two archives:

```sh
$PY -c 'import sys,json; from joulewise.align.apple.harvest_offload import archive_projection as p; \
a,b=p(sys.argv[1]),p(sys.argv[2]); print(json.dumps({"equal": a==b, "differ": sorted(k for k in set(a)|set(b) if a.get(k)!=b.get(k))[:20]}))' \
  "$MBP_ARCHIVE" "$S/archive"
```

## 8. Accepted disclosure: battery streak exposure (R17)

For a provisional record, the arm's `battery_window` row reads `v4_B_bar` from the light triage, that is, the desk's own battery join without the harvest's battery codes.
- A harvest-only `battery.member_span` (from the harvest's registered-threshold join) can turn that bar false once the final desk lands.
- The k+2 final then recounts the non-passing streak.
- Under ruling 9 a first non-pass resumes automatically anyway. So the exposure is **at most one window** of a battery streak counted late.
- The lead accepted this as disclosed (R17 follow-up).
