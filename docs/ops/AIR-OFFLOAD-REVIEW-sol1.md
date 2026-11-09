# Air offload independent review — Sol seat 1

Date: 2026-11-08. Verdict: **HOLD**.

Reviewed `7e0c264e0..175f0c8b9` (candidate full SHA
`175f0c8b9f2da382a34b7a0249c6de34454098f6`) against
[agreement items 1–9](AIR-OFFLOAD-AGREEMENT.md), the
[runbook](AIR-OFFLOAD.md), and the lead's single-pack and terminal-closure rulings.
Review branch: `ops/2026-11-08-offload-review-sol1`.

The HOLD rests on reproducible operator/host/functional failures, including
deletion of bytes absent from either verified copy. It does not depend on a
malicious account, forged receipts, or a compromised SSH server. This is a review
of the complete candidate's safety, not a claim that every defect was introduced
by this diff: S1-01, S1-02's lifecycle gap, and S1-03 are inherited from the base;
S1-04 concerns the newly added consumed-pack/external-terminal integration.

Only [the witnesses](../../tests/test_offload_review_sol1.py) and this report
were added. Production code and lead-owned coordination state are unchanged.

## Findings

### S1-01 — HIGH: equal length is treated as proof of a duplicate before deletion

Location: `scripts/offload_window.py:1231` (`Offload._inventory`), followed by
the unlink loop at line 1296.

For `--duplicate-root`, the deletion inventory requires a regular file with the
recorded size, but checks neither its SHA-256 nor even the original mtime.
Consequently, an operator-selected old backup containing a different revision
of a fixed-size trace or output is deleted as if it were the packed revision.
Both Air/iCloud copies contain the primary record's bytes; neither contains the
different duplicate's bytes. The deletion journal freezes that mistaken
inventory, so journaling does not repair the missing identity check.

Witness: `ReviewWitnesses.test_witness_same_size_nonduplicate_is_deleted`.
A different JSONL file of exactly the original length is deleted with no
`duplicate_differs` entry. A separate control proves that a different-length
file is preserved. No receipt mutation or metadata forgery is involved.

Required fix: compare every candidate duplicate's bytes to the pinned manifest
digest before including it in the deletion inventory, and preserve/report
different files. Alternatively, disable duplicate-root deletion until that
verification exists. Do not merely add an mtime comparison.

### S1-02 — HIGH: manual release bypasses offload exclusion and dwell accounting

Locations: `scripts/offload_window.py:2324` (standalone `release`), versus
line 1422 (`run` lock/lifecycle) and line 1596 (`triage`).

The documented manual `release --state-root S --window-id K` never takes
`S/.lock` and never writes offload start/end timing receipts. Without the
optional lease it also has no deadline, transport timeout, or alarm backstop.
`triage` checks the lock and the previous `run` span, and can therefore return
`quiet_start_state_ok: true` while this release is doing receipt hashing,
network I/O, and MBP deletion. It still reports success after that release
finishes inside the 120 s margin. A simultaneous `run` is also not excluded.

Witnesses:

- `ReviewWitnesses.test_witness_standalone_release_ignores_active_offload_lock`
  holds the real state lock on another FD; the actual CLI release still deletes.
- `ReviewWitnesses.test_witness_standalone_release_is_invisible_to_triage_and_unbounded`
  calls real triage during the CLI's receipts request. Triage passes; the
  transport timeout is `None`. A simulated 200 s delay crosses the planned dwell;
  release returns 0 and the old span remains byte-identical. There is no real wait.

Required fix: give standalone release the same state-lock and timing lifecycle
as run, with a bounded deadline that ends at least 120 s before dwell. The
shared magistrate lock/lease must cover it when wired. Until then, remove the
manual release route from operational use and release only through bounded
`run`/`release_older`. A one-time process probe cannot protect an ongoing release
from a later arm transition. This finding is separate from the runbook's already
acknowledged probe-only race.

### S1-03 — MEDIUM: a failed process census is accepted as an idle machine

Location: `scripts/offload_window.py:1342` (`default_state_probe`).

Only stdout is consumed from `ps`; its exit status is ignored. If process
enumeration exits nonzero with empty stdout and no matching LaunchAgent plist
is present, the active probe reports `armed: [], measuring: []`. That is a
plausible host/census failure, especially across permissions and sandbox
boundaries; no adversary is needed. A process that fails to execute at all
raises instead; the two failure modes must not be confused.

Witness: `ReviewWitnesses.test_witness_failed_ps_census_reports_quiet` injects a
nonzero census result and proves that the resulting state passes admission.

Required fix: refuse on nonzero census status and surface a distinct diagnostic.
Keep the native census smoke and magistrate shared-lock wiring as deployment
preconditions. The observed sandbox failure in the baseline suite was an
execution `PermissionError`, not empirical evidence that this host produces
the injected exit-status failure.

### S1-04 — MEDIUM: declaring external terminal inputs does not transport them

Locations: `scripts/offload_window.py:959` (`adopt_harvest_pack`), line 1945
(`_check_harvest_binding`), and runbook §1a's outside-session terminal layout.

The consumer checks that each supplied external is bound, but does not require
the external terminal files to be supplied. A real harvest pack generated with
terminal files declared in `finalized_manifest.v2.inputs` and no corresponding
`pack(..., external=...)` is accepted. The Air verifies zero externals, iCloud
confirms the same incomplete object set, and release succeeds. The terminal
files remain on the MBP; their digests in the finalize manifest are not copies
of their bytes. The supported Air restore refuses if those MBP-only files are
absent, as they would be on an unprovisioned Air or after MBP loss.

Witnesses:

- `ConsumedPackWitnesses.test_witness_bound_external_terminal_is_absent_from_both_copies`
  proves the same payload is consumed without repacking and that neither
  verified payload contains the declared external terminal files.
- `ConsumedPackWitnesses.test_witness_native_restore_requires_omitted_external_terminal`
  uses the actual sibling lane's `finalized_manifest`, `pack`, and `unpack`.
  Offload returns 0 and release reports `two_verified_copies`; with the synthetic
  MBP-only terminal directory withheld, native unpack refuses with
  `external closure input differs`. It does not read any real custody.

The native code is pinned Git blob `d279ab46f8cb3eae288545c8265948e325b24eba`,
from local `origin/align/2026-11-08-harvest-off-fix`, file
`joulewise/align/apple/harvest_offload.py`; SHA-256
`1ba0cc107aaa8c0b63b598ed46e0b89b97d04a314d513f54f40d7b9964e28293`.
The integration witness skips if a shallow clone lacks that object; it ran here.

Required fix for the outside-session layout: the harvest lane's ONE canonical
pack must include the bound terminal evidence as externals, and the consumer
must refuse an omitted required terminal object. Do not repack in this tool.
If the lead instead provisions those files on the Air through another verified
route, document and verify that dependency before declaring this layout ready.
Whether the native layout actually uses external terminal files remains the
lead's N1 census gate; no production layout was inspected here. External files
are not deleted by this tool, so this witness establishes an incomplete backup
and restore failure, not observed deletion of terminal files.

## Coverage and nonblocking observations

The reviewed receipt chain binds the window, offload-manifest digest, record
pin, complete custody-object list, primary UUID, both receipt hashes, and a new
nonce. Gate `receipts` rehashes the compressed parts and both manifests before
answering. Dedicated controls reject replayed nonce responses, a decayed Air
part, and a replacement volume UUID, preserving the MBP files. No additional
ordinary-failure receipt replay acceptance was demonstrated.

Consumed-pack verification checks the finalize pin, namespace and entry map,
then independently re-derives the expected file/link/directory rows on the Air
and checks every streamed member. A wrong finalize pin refuses before transport.
The payload transferred by the new witnesses is byte-identical and the local
parts directory stays empty. S1-04 is about omitted external dependencies, not
a bypass of those per-member checks.

For bounded `run`, the monotonic deadline, alarm, process-group cleanup,
prediction admission, shared lease checks and default 120 s lease margin are
present. The existing focused suite exercises their synthetic cases. The
probe-only mode is explicitly heuristic, and mutual exclusion with magistrate
arm/dwell transitions remains uninstalled work; this review does not certify
the stronger statement that probe-only execution cannot overlap a window.

Store binding probes the configured mount's UUID, marker and ownership, and
checks write free space. The independent-second-disk path checks distinct
UUIDs and disjoint physical-store identifiers. I found no additional ordinary
replacement-volume acceptance in the reviewed default path. Actual diskutil
fields and volume behavior were not exercised.

Both setup scripts were read, never installed or executed. The existing suite
also parsed them with `bash -n`, which executes no script statements. Static
inspection found the dedicated non-admin account, root-owned gate/binding/key,
forced-command restrictions, disabled forwarding/PTY/user rc, and MBP host pin
with `-F /dev/null`. These remain native setup checks, not live SSH evidence.
One setup side effect merits explicit operator acknowledgement: Air setup line
66 uses recursive `chown -R` on the existing `backups` tree if its top-level UID
is 99. It changes descendant ownership, not just the directory's owner. No
actual ownership state or damage was inspected; prefer a narrowly scoped owner
repair or make that recursive metadata change explicit before installation.

The second-copy receipt is historical evidence: release does not re-download
iCloud or rehash the alternative second disk. That is the agreement's explicit
design, not a newly discovered fresh-second-copy guarantee. Restoring and
retaining those remote copies remain operational responsibilities. Deliberate
receipt resealing by a compromised account is outside this HOLD's basis.

## Verification and handoff

All tests ran one module per process with `TMPDIR=/private/tmp`, sequentially.
Synthetic payloads were about 1.2 MB per fixture. No network, SSH, sudo, model
weights, measurements, B5 analysis, or real restricted directory was accessed.
No real offload store was touched; all test stores were temporary. The existing 8-worker
analysis job was not inspected or modified. Git object reads through the allowed
alternate were used for code only. No throughput or hardware claim is made.

| Command | Result |
|---|---|
| `TMPDIR=/private/tmp python3.13 -B -m unittest -v tests.test_offload_review_sol1` | 11 tests, OK, 1.604 s; no skips. Passing `witness` tests reproduce defects; controls prove refusals. |
| `TMPDIR=/private/tmp python3.13 -B -m unittest tests.test_offload_window` | 96 tests, 95 passed, one error, 5.908 s. `test_default_probe_sees_armed_agent` cannot execute `/bin/ps` in this sandbox. No safety bypass attempted. |
| `TMPDIR=/private/tmp python3.13 -B -m unittest tests.test_offload_bench` | 1 test, OK, 0.148 s; generator only, no benchmark campaign. |
| Python 3.13 `ast.parse` on both offload Python scripts and the new witness module | Syntax OK; no bytecode artifacts written. |
| `git diff --cached --check` | Clean. |

No full suite was run, per the binding machine-load limit. No MLX code is
involved. Python 3.11 was not available on PATH; tests ran on Python 3.13.18.

Next exact step: lead dispositions S1-01–S1-04, assigns bounded production fixes
or disables the unsafe optional routes, then turns each relevant reproducer
into a safe-behavior regression and reruns these targeted modules. Preserve the
single canonical pack. Before deployment, the lead must finish N1 terminal-layout
and shared-lock/lease wiring, rerun the native process-probe test outside this
sandbox, and verify setup/host pin/volume UUID/iCloud round trip and same-path
restore using synthetic data in a clean lead-controlled session. This review
does not authorize installation or hardware work while the analysis job runs.

No coordination-state edits or kernel task registrations were made, as directed.
No subagents or external consults were invoked; final adjudication remains with
the lead. The two added files are committed locally on the review branch; there
is no push. Remaining uncertainties are the actual native terminal layout,
native SSH/volume/iCloud behavior, and the lead's disposition of inherited defects.
