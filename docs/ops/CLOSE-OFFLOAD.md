# Automatic close offload

**PROVISIONAL.** The lead owns the RL-174 D blind check, the native MBP
production-key round trip, the close-interval floor recheck and standing-item issue.
[SPAN-OFFLOAD.md](SPAN-OFFLOAD.md) covers installation, the private iCloud directory,
the pinned public key, and the typed copy and SSD receipts.

## After every Check, including F0

After Check, the desk-bundle push and the MBP desk, run this synchronously in the
magistrate's **signed-in GUI domain**. A one-shot LaunchAgent in the user's GUI
domain can run the same argv. In that case wait for its exit and collect the
status and output before proceeding. MBP iCloud access requires the GUI domain.

```sh
"$PY" -B "$REPO/scripts/close_offload.py" after-check --config "$MBP_CONFIG" \
  --span-dir "$OUT" --deadline-epoch "$CLOSE_DEADLINE_EPOCH"
```

Use absolute paths. OUT is the exact checked output. The deadline is epoch
seconds before the next soak, within the close interval. For a manual close, the
desk fence must be absent. The command holds the desk fence lock, checks the
runner census and supervises the worker and provider children to the deadline.
The magistrate serializes Check, close and arm. Run from the GUI session or GUI
LaunchAgent, never over SSH.

### Controller-owned close (PR #800)

After the controller holds or renews its standing fence for the close, pass
the exact purpose, owner PID and stored lease deadline from that operation.
Use the same fence path and a close deadline within both the close interval
and the standing lease. The controller waits for the close subprocess with
the standing fence in place and leaves the lock available for the subprocess.

```sh
"$PY" -B "$REPO/scripts/close_offload.py" after-check --config "$MBP_CONFIG" \
  --span-dir "$OUT" --deadline-epoch "$CLOSE_DEADLINE_EPOCH" \
  --fence "$DESK_FENCE" --controller-fence-purpose "$STANDING_PURPOSE" \
  --controller-fence-pid "$CONTROLLER_PID" \
  --controller-fence-deadline-epoch "$STANDING_LEASE_DEADLINE_EPOCH"
```

Pass all three controller flags together. The purpose is the full
`cadence-controller:<token>` string. Use the controller's own expected lease
tuple, with the deadline as stored and the PID of the controller process.
Close verifies the exact tuple under `.desk-fence.lock`, keeps the runner
census, and holds the lock through the final transfer check. It leaves the
fence in place. The exact verified fence path may remain in `forbid_paths`.
Other configured fences still apply. A changed or missing tuple, an expired
or insufficient lease, a busy lock or a live runner holds close.

### OUT and result

For a separately rooted Check OUT, such as F2, add `--plan "$PLAN"` from the
Check. The basename must equal PLAN or PLAN followed by its UTC timestamp. If
that controller uses a different top-level completion record, also pass its
declared basename with `--require-file`. Close verifies its presence and
archives its bytes without parsing them. Such an OUT is outside the GAP roots
and can retire once its pack and cloud round trip are verified. Pass
`--keep-raw` to retain a separate OUT for this invocation. Record a designated
raw copy in the durable allowlist before it can enter rotation.

Require exit zero, `CLOSE_OK`, the exact OUT's verified marker, and `pending.clear`
true. Nonzero, timeout, missing or unverified output holds the next arm, including
F0. A retry repeats the same Check OUT and rechecks any typed marker's hashes.
Immediately before every arm and soak, from the same GUI domain, require a fresh
exit zero and `ICLOUD_CLEAR` from:

```sh
"$PY" -B "$REPO/scripts/span_offload.py" pending --config "$MBP_CONFIG"
```

Record the close output and fresh transfer observation in the appropriate private
records. No iCloud writes from the MBP while armed. Include `bird`, `cloudd` and
`fileproviderd` in the maintenance line.

## GAP and archive retention

- The exact checked OUT is encrypted and cloud-verified on every Check. In the
  managed GAP roots, its raw files stay, as do the newest output and all ties.
  The selection reads receipt presence and mtime only. Campaign plans use OUT's
  basename without its UTC timestamp. Part C/F0 plans use the complete OUT basename.
- The command rotates the most recent eligible older output of each kind from
  `/Users/edr/campaign-out/<kit>/<plan>-<stamp>` and
  `/Users/edr/code/jw-wt/<tree>/.desk/r1-partc-*`. Use `--catch-up` in a close
  interval to process all eligible older outputs. Newest outputs preserve their
  receipt bytes and timestamps.
- In the private MBP config, set `raw_retention_paths` to a JSON array of exact
  absolute OUT paths. An empty array is valid. The lead or magistrate records
  designated raw copies before rotation and updates the same config atomically
  between close invocations. Use the original OUT path even if retirement
  has already renamed it. Rotation and catch-up skip allowlisted paths,
  including interrupted retirements, and leave surviving files in place.
  Release a path only after the owning retention decision allows it.
- The shared backend verifies the encrypted pack's per-file manifest and the
  iCloud evict, re-download and hash round trip before removing older raw
  directories. Interrupted removal is retried using a same-parent renamed
  directory, a private stage retirement record and the verified archive.
  Changed or new surviving entries hold close for lead review.
- **AIR FALLBACK (item 388).** A verified cloud round trip and fresh transfer
  CLEAR let the MBP arm while the Air is absent. The MBP keeps the materialized
  ciphertext. It never waits for an SSD or an Air marker, and uses the pinned
  public key even while the Air is away.
- At 60 decimal GB free or less, the shared backend mails the configured lead.
  Low disk never substitutes for verified SSD custody.

The backend handles source bytes for hashing and archiving. It parses its own
records and transport metadata. Expanding unreleased custody requires a registered
look.

## Later SSD copy and reclaim

The Air independently runs the shared `span_offload.py ssd-copy` command on the
typed marker. Once the receipt is delivered and OUT has been retired from the
GAP set, the MBP can reclaim the stage ciphertext in a subsequent GUI close
interval:

```sh
"$PY" -B "$REPO/scripts/close_offload.py" reclaim --config "$MBP_CONFIG" \
  --span-dir "$OLD_OUT" --ssd-receipt "$SSD_RECEIPT" --deadline-epoch "$CLOSE_DEADLINE_EPOCH"
```

The backend streams all four cloud objects through SHA-256 and byte counting
without a second copy on the stage filesystem. Eviction requires matching cloud
hashes and sizes and a matching SSD receipt. Keep the SSD receipt with the retained
artifacts. Supply `--plan "$PLAN"` for a separately rooted OUT.
This later cleanup is outside the after-Check arm path.
