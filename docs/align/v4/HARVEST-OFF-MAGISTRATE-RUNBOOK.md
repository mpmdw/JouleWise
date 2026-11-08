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

**1b. Write the record-bound tree manifest.** Its SHA-256 goes into record k (`finalized_manifest`, §3).

```sh
$RUN finalize-manifest --session-root "$S" --out "$OUT/finalized_manifest.json"
# prints {"finalized_manifest": ..., "sha256": H, "entries": n}
shasum -a 256 "$OUT/finalized_manifest.json"     # == H: the file is canonical bytes
```

What it binds (R17 review F1 and delta D1-D4), besides every tree entry and the restore namespace `$S`:
- **Every link is followed hop by hop as the kernel does**, with lstat, before anything is resolved.
  - `..` is never normalized lexically. An external link or declared input containing a `..` component refuses (delta2).
  - A chain with an external hop is external, even when it ends back inside `$S`; every hop's text is then bound.
  - A link whose immediate target is another link refuses, unless the chain ends inside `M` or inside `$S`; then every hop is bound.
- **Links into `M`** (the measurement view): the checkout identity of `M` (head, clean incl. untracked, interpreter and packages) plus the mirror-relative target each link selects. The Air must reproduce both exactly. `M` must be clean and identified, or finalize refuses.
- **What Git identity does NOT cover: ignored checkout content.** Every ignored path a link into `M` reaches is classified by `configs/align/v4/harvest_off_ignored_inputs.json`:
  - covered by the interpreter identity (`.venv/`);
  - a regenerated cache (`__pycache__`, `*.pyc`, `.DS_Store`);
  - inside a declared directory (`runs/`). **This is not an exemption** (delta2, lead ruling 1).
    - finalize-manifest enumerates what `harvest.resolve_inputs` selects for the plan. Every selected file outside `$S` that the identity does not cover (ignored in `M`, or outside `M`) becomes a declared input, bound by bytes and real path and re-verified on the Air. The ledger is one of them.
    - A selected directory outside `$S` that the identity does not cover refuses.
    - If the plan cannot be resolved, each declared directory is bound whole, by bytes and membership within the bounds, or finalize refuses.

  Anything else **refuses at finalize**. The declared inputs are the calibration ledger plus whatever the **native N1 census** finds. That census is a lead-owned gate and has not run yet. Until it lands, a real session that links other ignored content refuses (fail closed). This is the exact scope of the guarantee: tracked and untracked-not-ignored files by identity, declared ignored inputs by bytes, nothing else assumed.
- **The calibration ledger** the window appended (a declared input): its bytes and its real path. Its resolved parent directories must be the same on the Air immediately before it is placed, or the restore refuses (D1).
- **Byte-bound ignored directories** also bind their membership: the sorted relative names and sizes. The Air re-enumerates them, and an added or removed file refuses (delta2, lead ruling 3).
- **Any other link that leaves `$S`**: the bytes it reaches (a file, or every regular file below a directory), at most 4,096 files, 4,096 directories, 1 GiB and 256 MiB per file. The bounds apply during the walk, before the offending file is hashed, and a directory linked many times is enumerated once. A target past those bounds, an unreadable directory (D4), or one that reaches a further link, refuses. Bind it through `M` instead. Model weights are never hashed or copied.
- **A link to a missing path** stays bound as missing.
- **The name `.external-staged`** is reserved; a session containing it refuses.

**1c. Pack the verified compressed copy.** The calibration ledger the window appended travels with it. `--finalized-manifest` is required: without it, pack refuses.

```sh
$RUN pack --session-root "$S" --out "$OUT/offload" --finalized-manifest "$OUT/finalized_manifest.json"
cp "$OUT/finalized_manifest.json" "$OUT/offload/"
```

Pack re-verifies the closure on the MBP (checkout identity, ledger and other closure bytes) before it writes anything.

**1d. Offload** `$OUT/offload/` to the Air during cool-down. Use the air-offload lane's authenticated route (`ops/2026-11-08-air-offload`, under its cool-down lease). The payload is about 0.3-2.6 GB.
- The transfer must finish before the dwell starts.
- The MBP originals stay until the lane's two verified copies exist; nothing here deletes them.

## 2. Air, during the MBP cool-down

**2a. Restore** at the same path, record-bound. `H` is the digest from 1b. Both binding arguments are required:

```sh
$RUN unpack --offload "$OUT/offload" --finalized-manifest "$OUT/offload/finalized_manifest.json" \
            --finalized-sha256 "$H"
```

Nothing is published at `$S` until all of these hold:
- the chain `H` → finalized manifest → transport manifest → restored bytes;
- the Air's `M` identity equals the one in the finalized manifest;
- the closure bytes on the Air equal the MBP's;
- every external destination (the ledger) is one the finalized manifest names.

A payload member outside the manifest refuses before anything is written. Nothing is ever written through a restored link.

**2b. Run the light triage** and write the record source:

```sh
$RUN triage --session-root "$S" --window-id "$K" --out "$OUT/light_triage.json"
# add --ladder-recorded only when a U1-U3 failure's escalation step is already recorded for the next plan
```

**2c. Return** `light_triage.json` to the magistrate's desk repository by the same authenticated route.

## 3. Magistrate, the record step for window k (before the arm of k+1)

Record k is the index `records/$K/record.json` (schema `joulewise.align_v4.window_record.v1`), committed and pushed as today. The full field list is in `next_arm_packet.md` (Committed inputs). R17 changes only the following.

**Every record after R1 (R17 review F2):** the record carries the top-level field `finalized_manifest` → `{"path": "records/$K/evidence/finalized_manifest.json", "sha256": H}`, the file from 1b byte for byte. The packet builder refuses a record without it, or with a non-canonical one.

**Full desk NOT due** (the previous window is not W1, and the arm's artifact-set digest equals the last desk-passed one):
- `sources.light_triage` → `records/$K/evidence/light_triage.json`, the file from 2b, byte for byte.
- `sources.desk` → a placeholder that marks the desk as running off the MBP:

  ```sh
  $PY -c 'import json,sys; print(json.dumps({"plan_id": sys.argv[1], "status": "running_off_mbp"}, sort_keys=True))' \
      "$PLAN_ID" > "$DESK_REPO/records/$K/evidence/desk.json"
  ```
- `sources.pilot` and `sources.exclusions` are **omitted**. If they were present beside the placeholder, the record would still be provisional (R17 review F4): final means a completed harvest.
- Series ledger: `last_passed_record` stays on the last record whose desk passed (see §4).

**Full desk DUE** (previous window W1, or code/config changed since the last desk-passed state): **do not arm on the light triage.**
- Wait for the Air's `desk` and `final` (§5).
- Commit record k with its own `sources.pilot` (`$S/PILOT.json`), `sources.desk` (`$S/desk.json`) and `sources.exclusions` (`$S/archive/derived/exclusions.json`).
- These count as final only if `desk.harvest_status` is `ok` or `members_excluded`, and the desk's and PILOT's `plan_id` are this window's.
- A completed desk that did not pass is still final. It just is not a desk pass.
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
- The same evidence rule as §3 applies: `previous_final` naming a running, faulted or other-plan desk does not make k final.
- If k's desk is not finished by record k+1, commit k+1 without `previous_final`. The arm of k+1's successor then refuses (§6) until a later record carries it.
- **R17's bound:** window k must be final before the arm of k+2. This holds for **every** window in the chain, test windows included. They still contribute zero calibration.

## 5. Air, during window k+1: restore → harvest → desk → final → reduce

The Air must be otherwise quiet: no Sol seats; renice others. The desk-verdict child has a wall budget; a time-out there is a re-run, not a result.

```sh
$RUN desk  --session-root "$S" --workers auto [--sweep "$SWEEP/SWEEP.json"]   # harvest + full v4 desk
$RUN final --session-root "$S" --window-id "$K"                               # final eligibility row
$RUN reduce --session-root "$S" --out "$OUT/reduced" --workers 2              # columnar PM + per-turn tables
```

- **`desk`** writes `$S/PILOT.json`, `$S/desk.json` and `$S/archive/`.
  - `--workers auto` uses min(free cores, (free memory − 4 GiB reserve) ÷ the per-worker peak).
  - **If not even one worker fits, it refuses: postpone the desk** until memory is free. It never launches over budget.
  - Pass the sweep receipt once it exists (§7). Without it the peak defaults to 8× the window's largest raw plist.
  - A sweep receipt is used only if it records its input size and is bound to the same harvest code (D6). That code identity is the source checkout behind the measurement view: its head, a clean tree, and a usable interpreter identity. A dirty or unidentified checkout falls back to 8×. Its peak scales up with this window's largest plist and never down. A receipt for other code, or with no binding, falls back to 8×. A receipt with a failed or nonpositive run refuses.
- **`final`** applies the same finality predicate as the packet builder (`light_triage.final_adjudication_error`, delta D9). It refuses unless all of these hold:
  - the harvest completed (`harvest_status` `ok` or `members_excluded`), or the window has no capture at all;
  - PILOT.json shows a completed adjudication (`instrument_ok`/`instrument_incomplete`);
  - the desk and PILOT.json are this session's;
  - the exclusions agree.
  - Supplemental captures count as captures here (D5). Its rows must be a subset of the light triage's provisional rows. If not, stop and escalate to the lead: the proof says this cannot happen.
- **`reduced/`** is outcome-bearing (energies) and is restricted like `withheld/`. Its `MANIFEST.json` digests and row counts are structure-only. Each `<run_id>/turns.json` equals PILOT.json (`turn_table.equal_to_pilot`); check this before any analysis reads tables instead of bundles.
- Hand the three final files to the magistrate for record k+1 (§4).
- Prune the restored `$S` on the Air only after record k+1 (or k) with the final sources is pushed. The MBP originals follow the air-offload lane's retention rule.

## 6. What refuses, and when

| Where | Refusal | Meaning and action |
|---|---|---|
| `finalize-manifest`, `pack` | `terminal record absent` | Not terminal. Wait for B1 completion. |
| `finalize-manifest` | `not a clean, identified mirror source` | `M` is dirty, or has no head or `.venv`. Fix the checkout, then finalize. |
| `finalize-manifest` | `external closure ... not finite` / `over ... bytes` / `further link` / `points at a further link` / `cannot read directory` | A link leaves `$S` towards something large, linked or unreadable. Bind it through `M`, or escalate. |
| `finalize-manifest` | `reaches an undeclared ignored input` | A link into `M` reaches ignored content the declaration does not cover. Do not edit the declaration ad hoc: the N1 census decides (lead). |
| `unpack` | `declared input ... resolves to` / `external destination ... now resolves to` | The ledger's parent directories resolve differently on the Air (an alias changed). Fix the mirror path; nothing was written. |
| `unpack` | `mirror link ... selects` / `ignored mirror content ... differs` | A link into `M` now selects another file, or ignored content changed. Fix the mirror. |
| `pack`, `unpack` | `requires the record binding` | `--finalized-manifest` (and on unpack `--finalized-sha256`) missing. There is no unbound route. |
| `pack`, `unpack` | `external closure input differs` / `external link ... resolves differently` / `closure directory differs` | Bytes a link points at changed since finalize, or differ on the Air. Fix the mirror, or do not restore. |
| `unpack` | `restore namespace differs` / `external file is not bound` | The transport manifest was edited. Re-transfer. |
| `pack` | `packed tree differs from the finalized record manifest` | Something changed the session after finalize. Find it; do not repack over it. |
| `pack` | `unsupported file type` | A FIFO or device in the session. Investigate. |
| `unpack` | `measurement checkout mirror differs` | The Air checkout (head, clean incl. untracked, interpreter and packages) is not the one in the finalized manifest. Fix the mirror. |
| `unpack` | `committed digest` / `offload manifest differs` / `payload digest mismatch` / `restored tree differs` | The copy is not the finalized record. Re-transfer. |
| `unpack` | `already exists` / `differs from the recorded source root` | Byte identity needs the same, empty path. |
| `unpack` | `append-only` | The Air ledger is not a prefix of the window's. Do not restore. Escalate. |
| `triage` | `light triage refused: ...` | Registration evidence (U3 bar, WP19) is missing. The full desk would refuse too. |
| `desk` (harvest) | exit 3 `NotReady chain_process_group_alive` | The MBP chain's pgid collides with an Air process (about 1%). Re-run. |
| `desk` | `postpone the desk: no harvest worker fits` | Free memory first, or wait. The desk was not launched. |
| `desk` | `sweep run failed` / `nonpositive or missing peak` | The sweep receipt is not a measurement. Re-run the sweep, or drop `--sweep`. |
| `final` | `needs a completed harvest` / `desk and PILOT.json of this session` | The desk did not finish its harvest, or the files are another session's. |
| packet / arm | `R17: final eligibility of K must be recorded before the arm of the window after next` | k is still provisional at the arm of k+2, or its final sources record no completed, plan-bound harvest. For a test window, `member_eligibility` fails. Commit `previous_final` (§4). |
| packet / arm | `must bind the finalized tree manifest` / `not a canonical` | Record k lacks `finalized_manifest` (§3), or the file is not the canonical bytes from 1b. |
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
- `SWEEP.json` (schema `harvest_sweep.v2`) records the swept window's largest plist and the harvest code identity.
- After a code change, re-run the sweep. Until then, the desk uses the 8× fallback.
- Record the knee (the fastest count whose peak fits) in RUN_STATE.
- Keep `SWEEP.json`. It is structure only (times, bytes), with no outcome values.
- The sweep's five archives are engineering copies. Delete them after; they are never record sources.

**Optional native identity check (N2).** On a window whose harvest also ran on the MBP, compare the two archives:

```sh
$PY -c 'import sys,json; from joulewise.align.apple.harvest_offload import archive_projection as p; \
a,b=p(sys.argv[1]),p(sys.argv[2]); print(json.dumps({"equal": a==b, "differ": sorted(k for k in set(a)|set(b) if a.get(k)!=b.get(k))[:20]}))' \
  "$MBP_ARCHIVE" "$S/archive"
```

## 7a. Native checklist before the first armed window on this route

These are magistrate-owned native gates. None of them can be passed off the MBP or with synthetic data.

1. **N1 census of ignored inputs (lead ruling, R17 delta D3).** Required before the first real `finalize-manifest` can pass. Git identity does not cover ignored checkout content, so every ignored file a real harvest reads must be a declared input.
   - **Run** the native smoke's N1 profile on the MBP: a real finalize → pack → Air restore → harvest → desk. Record every ignored path under `M` that the harvest and desk open, for example with `fs_usage -w -f filesys` filtered to `M`, or the stage profile plus an audit hook.
   - **Compare** the list with `configs/align/v4/harvest_off_ignored_inputs.json`:
     - `identity_bound` (`.venv/`): covered by the interpreter and package identity.
     - `regenerated`: caches that are never read as inputs.
     - `declared_directories` (`runs/`): directories whose consumed files are exactly the declared inputs.
   - **Declare each consumed ignored file** as a finalize input. Today that is only the calibration ledger, which comes from the plan's `ledger_path`. Any other file needs a reviewed code change to `_ledger_input`'s declared set, never an ad hoc CLI flag. Add its directory to `declared_directories` if it is not there.
   - **An ignored path that is linked but not consumed** goes under `regenerated` only if it really is a cache. Otherwise keep the dependency out of the measurement view.
   - **Commit the declaration change with the census receipt**, and record it in RUN_STATE. Until then, a session whose links reach any other ignored content refuses at finalize, fail closed: `reaches an undeclared ignored input`.
   - Re-run the census after any change to the measurement view, the harvest or the desk.
2. **Time the first native finalize** (`finalize-manifest`, including the per-link `git ls-files` and closure hashing). Then time pack and the Air restore.
3. **N2:** archive identity between the MBP and the Air, §7.
4. **The native sweep:** the knee and per-worker RSS on a representative session, §7.
5. **Quiet boundary:** check the arm's dwell record on a real arm, §8.
   - `quiet_dwell.start_ns` follows every arm-side write.
   - `installer_end_ns` minus `start_ns` is the post-stamp installer interval. It is disclosed, not trimmed.

## 8. Arm-side notes

- **Light triage `thermal_escalation`** reads `status: pass` only when every U1–U3 passed. An `inconclusive` result, like a `fail`, owes the registered consequence unless `--ladder-recorded` (R17 review F6). This is what the packet builder applies.
- **The arm's Git checks and the frozen-series binding** finish before the meter probe and before `quiet_dwell.start_ns` is recorded. The arm record says so in `quiet_dwell.git_and_series_binding_before_dwell` (R17 review F7).
- **Lead ruling on R17 review open item 5:** the arm record write (`staging/v4-arm-NNN.json`), the powermode check, the W1 disk gate's reads and `disk_usage`, the `session.json` write and `staging/w1_disk_gate.json` now all run BEFORE the dwell stamp. A failing powermode check or disk gate is now recorded in the arm record as a refusal reason.
- The stamp is the arm's last step. After it come only:
  1. the in-memory probe-before-dwell order;
  2. one write of that single dwell value, `staging/v4-arm-NNN.dwell.json` (`quiet_dwell.start_ns`, `meter_probe_before_dwell`, final `admitted`);
  3. the installer handoff, or the refusal;
  4. when the installer's launchctl calls return (or it raises), the same dwell record is rewritten once with `quiet_dwell.installer_end_ns` (the same monotonic clock) and `installer_outcome`. This is a lead ruling: analysis discloses the post-stamp installer interval, and a later rule may trim it.
- The arm record's `quiet_dwell` names that file and carries `start_ns: null`. Read the dwell from the `.dwell.json` file.
- Witness: `tests.align.test_v4_next_arm_packet.ArmOrderWitness`.

## 9. Accepted disclosure: battery streak exposure (R17)

For a provisional record, the arm's `battery_window` row reads `v4_B_bar` from the light triage, that is, the desk's own battery join without the harvest's battery codes.
- A harvest-only `battery.member_span` (from the harvest's registered-threshold join) can turn that bar false once the final desk lands.
- The k+2 final then recounts the non-passing streak.
- Under ruling 9 a first non-pass resumes automatically anyway. So the exposure is **at most one window** of a battery streak counted late.
- The lead accepted this as disclosed (R17 follow-up).
