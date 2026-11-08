# Permanent SSD: B-unmount operator card

**PROVISIONAL — synthetic tests only.** Implements proposed ARM-SSD, agreement
branch `origin/align/2026-11-08-ssd-permanent-agreement`, §3.4. Adoption,
qualification and production wiring belong to the lead.

**One-time Ed setup (after the current window has terminally completed).** Keep
the drive attached at a fixed port, cable and placement. Show borrowed-drive
contents before any erase. Copy
[`configs/ssd_permanent.json`](../../../../configs/ssd_permanent.json) to a
local, internal-disk config. Also provision an internal-disk state directory,
a shared magistrate lease file, and explicit custody parents for the idle
census. Keep these off the SSD.

1. With each APFS volume mounted, use its UUID from `diskutil info -plist`.
   In `sudo vifs`, add `UUID=<VOLUME-UUID> none apfs rw,noauto` **for every APFS
   volume**, including hidden volumes. Save the original fstab.
2. On each volume, disable Spotlight (`sudo mdutil -i off <MOUNTPOINT>`) and
   exclude Time Machine (`sudo tmutil addexclusion -p <MOUNTPOINT>`). Set
   `.metadata_never_index` and `.fseventsd/no_log`. Verify settings; record AC
   sleep and disk-sleep settings.
3. In System Settings → Privacy & Security, set “Allow accessories to connect”
   to the non-prompting option that permits connection while locked (typically
   “Always”; verify labels on this macOS build). Test one locked-screen replug:
   the device must return without approval or automounting.
4. Enroll the sole external physical disk with `enroll --disk diskN
   --volume-uuid <OFFLOAD-APFS-VOLUME-UUID>`. Enrollment records serial, service
   bus path, entry ID, partition/container/volume UUIDs and disk UUID if exposed.
   Missing identity or unsupported topology refuses. Freeze policy values in
   that **one JSON file** after qualification.

**Magistrate interface.** Each invocation starts with:

```text
python3.13 -B scripts/ssd_permanent.py --config CONFIG --state-dir STATE \
  --lease LEASE --custody-parent PARENT [--custody-parent OTHER_PARENT] SUBCOMMAND
```

Supply **every** active custody root. JSON stdout and exit **0** mean success;
exit **3** means hold. Commands have timeouts; unmount initially retries once,
never forces. Supervise the copy's wall budget in addition to its CLI alarm.

**Per-window sequence (automated, zero Ed actions).**

1. After terminal completion/finalization, run `post-window --start-epoch START
   --end-epoch END` **before remounting**. It compares the saved arm entry ID,
   boot and counters and queries the span's unified log. Any matching storage
   log row (conservatively including benign rows) or indeterminate evidence sets
   `SSD_EVENT` and `HOLD.json`. Preserve receipts. The proposal loses the whole
   window (repeat W1); a second event requires requalification. Only the lead
   clears a hold.
2. The finalizer supplies a local immutable record directory containing
   `ssd-closed.json` with `schema: joulewise.ssd_closed_record.v1`, `state:
   closed`, `window_id`, and `files` mapping **every other file's relative path
   to its SHA-256**. Publish it only after all writers exit. Run `offload
   --record RECORD`. The hook checks the idle census and complete digests,
   mounts by UUID, verifies mount identity, copies through a pinned filesystem
   descriptor, fsyncs and rehashes into `joulewise-offload/<window_id>`.
   Existing/partial copies are preserved; sources remain unchanged.
3. Run `unmount`: it targets the enrolled APFS-store partition UUID with
   `diskutil unmountDisk`, verifies **all** device volumes unmounted, then
   requires two stable IORegistry samples. It saves `unmount.json` with Q's
   start at the second sample. Busy or uncertain evidence refuses; a failed
   transition invalidates the previous baseline.
4. Wait the configured Q, then `check-arm`. Require `ok: true`; retain its
   `arm.json` until post-window. `snapshot` is an optional IORegistry/boot-only
   diagnostic, not an unmount baseline. Nothing polls in-window.

**Integration gate:** all hook operations and prepare/launch/finalize must use
the **same exclusive lease**. The standalone CLI releases it at return; the
launcher must acquire it, recheck ARM-SSD through `Hooks` with an idle guard,
and retain it across the whole window. A census alone is insufficient;
uninstrumented collectors bypass this protection. Qualify
UUID resolution/all-volume unmount, driver properties/port stability, non-waking
census, log visibility/retention, the busy-file refusal and locked replug on the
target host before enabling the loop. A silent query does not prove log
coverage. DC plateau and R1 bridge qualification remain separate.
