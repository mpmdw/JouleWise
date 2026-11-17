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
seconds before the next soak, within the close interval. The command holds the
desk fence lock, refuses an existing fence or runner, and supervises the worker
and provider children to the deadline. The magistrate serializes Check, close and
arm. Run from the GUI session or GUI LaunchAgent, never over SSH.

For a separately rooted Check OUT, such as F2, add `--plan "$PLAN"` from the
Check. The basename must equal PLAN or PLAN followed by its UTC timestamp. If
that controller uses a different top-level completion record, also pass its
declared basename with `--require-file`. Close verifies its presence and
archives its bytes without parsing them. Such an OUT is outside the GAP roots
and can retire once its pack and cloud round trip are verified. Keep any raw
copy designated for a pending registered look.

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
  interval to process all eligible older outputs. The lead and magistrate keep
  unfinished work and projections still needed by a desk outside the retirement
  set. Newest outputs preserve their receipt bytes and timestamps.
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

The backend rechecks cloud hashes and requires the SSD receipt's plan, descriptor
and artifact hashes/sizes to match before eviction. Keep the SSD receipt with the
retained artifacts. Supply `--plan "$PLAN"` for a separately rooted OUT.
This later cleanup is outside the after-Check arm path.
