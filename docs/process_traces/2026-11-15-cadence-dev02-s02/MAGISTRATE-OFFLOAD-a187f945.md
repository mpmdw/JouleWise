# dev-02-s02 journal offload to iCloud (item 347 step 2-3 as amended by item 348), magistrate a187f945, 2026-11-15 13:12-13:15 PST

Why the fallback ran: item 348 makes the MBP's cloud offload a fallback that runs only if the lead's marker `/Users/Shared/JouleWise/desk-copy/cq-dev-02-s02-a1.ok` is still absent 30 min after the receipt's close (ended epoch 1794775365.16, 12:42:45 PST; so 13:12:45). A wait loop polled for the marker every 10 s; at 13:12:48 it was absent. **Path that wrote the marker: the MBP cloud offload (not the Air copy).**

Commands: item 347 step 2's fenced block, extracted mechanically from RUN_STATE on main into custody `offload-dev02-s02-a187f945.sh`, run with zsh 13:12:57-13:13:15 PST; output custody `offload-dev02-s02-out-a187f945.txt`. No journal file was opened: only find/shasum, tar|gzip|openssl, cp and a decrypt-and-list of the cloud copy.

- Provider: iCloud Drive, `/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-offload/cq-dev-02-s02-a1/` (the first existing folder in item 347's order).
- Stage: `/Users/edr/night-custody/offload/cq-dev-02-s02-a1/` (three files kept).
- Encrypted archive `cq-dev-02-s02-a1.tgz.enc`: 110,295,072 bytes, sha256 `bf34a938107856122de6d1e047152c4f0e3d969df489fcc917f5b28f20f01ae3` (AES-256-CBC, PBKDF2 200,000 iterations, salted). OUT is 2.9 GB on disk.
- Manifest `cq-dev-02-s02-a1.SHA256SUMS`: 226 files, sha256 `0af51efee1b638bc6c569aa886c957acf6fdf4b2a4f19533fd494ec73ab31057`. It includes `maintenance-log.txt` and `maintenance-log.err`, which item 344's Check wrote beside the journals before the offload.
- Cloud copy hash check: both files OK against `outer.sha256` (`shasum -c` in the cloud folder).
- Round trip: decrypting the cloud copy and listing the tar gave 304 entries (files plus directories).
- Key: `/Users/edr/night-custody/offload/offload.key` (created by this run, mode 600, MBP only), sha256 `6c294d1bed0b6632c26ad782b7c572d716348e6a6cb9d260471833a5c053590e`. Content never recorded.
- Upload evidence: `mdls` returns (null) here because Spotlight indexing is disabled on / and the Data volume (measurement_mode), so `brctl status com.apple.CloudDocs` was used. At 13:13:25 it listed the three files under the folder as `needs-upload`, upload active. At 13:13:54 (the first 2-minute poll) no unclean item remained under the folder; the container was `client:idle`, `caught-up`, `last-sync 2026-11-15 13:13:40`; and at 13:14:21 `needs-upload` appeared nowhere in the container. Full status saved in custody `offload-dev02-s02-brctl-a187f945.txt`; poll log `offload-dev02-s02-poll-a187f945.txt`.
- Marker written 13:14:28 PST under `test ! -e`: `cq-dev-02-s02-a1 cloud-offload Sun Nov 15 13:14:28 PST 2026 | provider .../com~apple~CloudDocs (iCloud Drive) JouleWise-offload/cq-dev-02-s02-a1 | enc sha256 bf34a938… | manifest sha256 0af51efe… files=226 | upload evidence brctl status ... 13:13:54 ...; magistrate a187f945`.

For the lead: the Air copy can come from the MBP's OUT (unchanged) or from this archive (key on the MBP only).
