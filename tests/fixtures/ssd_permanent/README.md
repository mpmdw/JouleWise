# Synthetic macOS storage fixtures

These values were authored by hand, not captured from this Mac or any study
device. UUIDs, serials, paths, entry IDs and counters are invented. XML was
serialized with Python's standard `plistlib`; the fixtures model the documented
plist/NDJSON output interfaces of the macOS `diskutil(8)`, `ioreg(8)`, `mount(8)`
and `log(1)` commands (local man-page names are format references, not a claim
that native commands were run here).

`list.plist` models a GPT external physical store and its synthesized APFS
container, including two APFS volumes. `info-*.plist` model `diskutil info
-plist` for each node. A whole GPT disk need not expose `DiskUUID`; the enrolled
identity also pins its partition, container and volume UUIDs. `ioreg.plist`
models the recursive driver-class archive; `ioreg-service.plist` models the
full IOService tree fallback needed when serial/port ancestry is absent from
the driver-rooted archive. The latter's service ancestry is the bus path.
`mount.txt` includes APFS system mounts and mount-point escaping; the enrolled
device is unmounted. `events.ndjson` includes Disk Arbitration and kernel
storage events. `quiet.ndjson` is deliberately empty.

These establish parser behavior only. Property availability, APFS topology,
UUID command resolution, log visibility/retention and stable port ancestry
remain native qualification gates on the measurement host.
