# PR #804 independent executing cold re-review

Reviewed commit: `6e9208de7d7e4305ffce5d25d8ac6ab2f62cf55b`.
Original refusal: `/Volumes/JW-EXT/scratch/sol-804-review/FINAL-MESSAGE.md`, reviewing `2e8d898df8498432bb865bf0249de09930446cda`.
Seat: fresh delegated Sol review, advice only; caller owns adjudication and final/live verification.

VERDICT: REFUSE

This verdict is immutable evidence for the original pin. Any later repair receives a separate delta report.

## Findings

### COLD-804-H1 — HIGH: a legacy provider listing can still satisfy the global `.ok` gate

`joulewise/span_offload.py:712-717, 770-815, 1405, 1414-1420, 1487`.

`RcloneBackend.provider_confirmed` is unconditionally true. Its `put` accepts provider listing evidence, including size-only evidence without any provider hash. `offload` then writes `<plan>.ok` using that flag. The iCloud evidence validator is conditional on the backend already being iCloud, so it does not protect this alternate entry. An existing typed rclone `.ok` is also accepted by retry validation.

Independent reproduction: `independent_probes.py`, `test_exposes_legacy_provider_listing_can_create_copy_gate_marker`. This executes the real stage builder, real local LibreSSL encryption and real `RcloneBackend.put/_readback`; only `_run` receives in-process synthetic copy/listing responses. It produced `.ok`, `provider_confirmed: true`, four null provider hashes and **zero brctl calls**. No real or fake rclone process was needed for this reproduction.

This conflicts with the brief's global no-`.ok` rule and RL-174 D.1's observed eviction/redownload condition. The optional transport is not exempt. Gate marker creation and valid-marker retry globally on complete observed iCloud evidence; retain legacy transport results only as unconfirmed evidence. Independently noticed during source review before the lead's message; lead subsequently identified the same issue.

### COLD-804-H2 — HIGH: an existing-marker retry can succeed after a late source change

`joulewise/span_offload.py:1502-1509`.

On a typed `.ok` retry, `recheck_marker` recreates/checks the source archive, then performs a potentially slow `_wait_uploaded`. It does not compare a source census after that last status wait. A write during the wait therefore yields successful offload despite the source no longer matching the marker.

Reproduction: `retry_source_probe.py` changes one opaque synthetic source file from the final `_wait_uploaded` hook. `offload` returns the old valid record successfully, leaves `.ok` byte-identical, and the current source manifest differs from the record. This failure case was suggested by the lead and independently executed here; it is not claimed as an independently discovered finding. It extends the original refusal's source-consistency concern into the newly successful retry path.

Take a whole-tree census before the retry's source read, and compare it after the final status observation and before returning success. When raw OUT has already been deleted by close, continue to allow hash-only retry without trying to census the absent source.

### COLD-804-L1 — LOW: `ssd-copy` may report success with an invalid existing receipt

`joulewise/span_offload.py:1557-1564`.

The existing-destination path hashes every retained artifact, but validates only the receipt's `files` mapping. It does not validate schema, plan, descriptor digest or verification time. Independent probe `test_exposes_existing_ssd_receipt_schema_not_validated_on_retry` changes the existing receipt's schema; a repeated `ssd-copy` succeeds and returns that receipt. `close` correctly rejects it as `SSD_RECEIPT_INVALID`, retaining raw and the local archive. This is a liveness/reporting defect, not unsafe deletion. Use the same complete receipt validator for generation/retry/consumption, or refuse/rebuild malformed receipts through an explicit safe recovery path.

## Original refusal disposition

| Original issue | Disposition at this pin | Evidence |
|---|---|---|
| HIGH: additions and cross-file version mixing certified | New offloads fixed. Existing-marker retry still has H2 above | Whole-tree device/inode/mode/link/size/mtime/ctime census at 213-252; before/after archive and pre-publication checks. Own added-member, cross-file/restored-mtime, add/remove and post-provider mutation probes all refuse without a new `.ok` |
| MED: keygen fails with missing final directory | Fixed | `keygen` creates final directory mode 0700; own fresh-directory probe uses real LibreSSL and checks key mode 0600 |
| LOW: failed placeholder-download retry exits 5 instead of 8 | Fixed for iCloud | Own CLI probe gets 8, 8, then 0 after restoring download; no `.ok` during failure; historical unconfirmed record retained |

## RL-174 clause assessment

Ruling read from `origin/audit/2026-11-10-fable` at `05fd231609bde202def258745b8a45ce44ce43da`, `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`: marker/retry paragraph and D.1/D.2. Storage-only excerpt saved as `RULING-EXCERPT.md`.

| Requirement | Assessment |
|---|---|
| One marker/backend for offload and close | Shared library and thin close CLI; same iCloud backend and marker schema. Alternate successful `.ok` path violates global evidence rule (H1) |
| No successful gate without observed eviction/redownload and equal sha256/size for all artifacts | Selected iCloud new-offload path enforces this; corruption of each of four artifacts, command-only eviction success, absent flag observation and failed downloads cannot produce `.ok`. Global rule fails through legacy path (H1) |
| Marker retry rechecks hashes and exits 0 when valid | Four cloud artifacts rechecked; marker immutable; changed provider bytes refuse. Late source-change gap is H2 |
| Native production-key qualification | Correctly INTERIM/PROVISIONAL in runbook; not exercised or satisfied here |
| Fresh read-only pending observation before each arm | `pending` reads only status, emits current observation time, rejects tested unknown/pending/offline states. Runbook requires immediate fresh GUI-domain observation per arm/soak; actual magistrate installation remains lead work |
| `bird`, `cloudd`, `fileproviderd` permanently on maintenance line; no MBP writes while armed | Explicit operational requirements in runbook; external caller duty, not claimed installed |
| Unreleased cloud bytes encrypted | Streamed AES/RSA transport; no source payload parsing found; opaque invalid-JSON source fixtures roundtrip exactly |
| Verified pack permits raw deletion | Fresh ciphertext is decrypted/stream-read against exact per-file manifest; wrong manifest refuses. Close revalidates the materialised stage and raw source before explicit raw removal |
| Only iCloud verified retains materialised local archive, does not wait for Air | Own close/repeated-close/pull probe passes; missing or corrupt local archive refuses before raw deletion |
| iCloud AND matching SSD readback receipt required before archive eviction/removal | Own real-byte synthetic SSD readback passes; changing each receipt-bound field refuses before deletion. Corrupt SSD readback publishes no receipt. Eviction failure retains the local pack and recovers on retry. Existing receipt reporting gap L1 stays safe at close |
| <=60 decimal GB mails lead, never forced single-copy eviction | Exact boundary 60,000,000,000 exercised through mocked disk/mail. Failed mail refuses. No real mail sent |
| Close interval after pushed desk bundle and MBP desk, before next soak; failure holds arm | Explicit runbook/controller obligations, with deadline/fences in tool. No measurement/controller execution performed |
| GUI-domain only on MBP, SSH cannot qualify iCloud | Runbook explicitly requires GUI LaunchAgent/magistrate, prohibits SSH evidence, and specifies a production-key synthetic native round trip and Air unwrap/SSD checks |

## Additional bounded observations

- An injected partial `shutil.rmtree` failure preserves the verified pack and leaves a partial raw tree. The next close safely refuses `SPAN_CHANGED`; recovery needs the lead to restore/finish that raw cleanup. No data-loss or successful-retry claim is made.
- A fabricated status string containing valid positive tokens followed by `pending transfers: 1` is accepted. This shows the parser is a positive-token/negative-token filter rather than a complete grammar. No evidence establishes that invented line as native brctl output, so this is a robustness observation, not a claimed native pending-transfer bypass. The native status/flag gate remains external.
- The supplied close tests depend on host disk capacity before they mock mail. A review subprocess tripwire prevented all real mail; the lead separately identified/repairs test disk-state isolation. The review did not contact mail or another integration.

## Execution evidence and limits

All writes were confined to `/Volumes/JW-EXT/scratch/sol-804-r2/cold-review/`. No builder checkout changes, GitHub writes, commits, MBP contact, real iCloud, real custody/energy files, measurements or real service calls. No sandbox/approval bypass or delegation. No builder run report read. Baseline shared checkout was clean. Inherited restrictions were not altered.

Exported offload source, entry points, focused tests and runbook were byte-compared against the exact pin. `tree/joulewise/__init__.py` is a documented disposable package shell, avoiding unrelated schema imports; the reviewed module and CLI/test/runbook bytes are unchanged. Imported test host-command tripwires and helpers were also exported. Temp files and fake executables stayed below `cold-review/tmp`.

Environment: Python 3.14.6; `/usr/bin/openssl` LibreSSL 3.3.6. Supplied tests use the locally resolved real OpenSSL; own probes explicitly use Apple LibreSSL.

| Command / evidence | Result |
|---|---|
| Initial brctl/local subset, `focused-tests.log` | 69 tests pass; 14 rclone-related methods excluded before lead clarified fake rclone is allowed |
| `env TMPDIR=<review>/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B run_focused.py tree`, `full-focused-tests.log` | **83 tests pass**, 51.111 s; full focused module after clarification |
| `env TMPDIR=<review>/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B independent_probes.py`, `independent-probes.log` | **23 probes pass their stated assertions**, 19.533 s. Two explicitly demonstrate H1/L1; passing characterization probes are not safety admission |
| `env TMPDIR=<review>/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B retry_source_probe.py`, `retry-source-probe.log` | **1 additional probe reproduces H2**, 1.254 s |
| Initial setup attempts | Two imports failed from omitted package dependencies; repaired only disposable test packaging. An initially overstrict review guard rejected even fake bare provider names; failed run preserved as `full-focused-overstrict-guard.log`, then guard restricted commands by resolved contained fake path and the entire focused module passed |
| Canonical full repository suite | Not run, as instructed: GitHub CI/lead owned; no measurement/outcome/custody test execution |

This is synthetic software review only. Permanent operational status requires the recorded GUI-domain native MBP production-key round trip, Air unwrap/SSD receipt, and actual controller integration. Caller owns final diff review, CI, live gates and merge decision.

Next exact step: repair/adjudicate H1 and H2, disposition L1, then review the bounded final delta in this seat. Keep the native gate PROVISIONAL.

VERDICT: REFUSE
