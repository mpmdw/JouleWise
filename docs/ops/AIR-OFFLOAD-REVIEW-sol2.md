# Air offload independent review — Sol seat 2

**Verdict: HOLD.** Release can delete local bytes that neither verified remote
copy contains. The standalone release command also bypasses the activity lock
and timing evidence used to enforce the 120-second pre-dwell margin. These are
plausible operator/functional failures, without an adversary or forged receipt.

- Date: 2026-11-08.
- Reviewed range: `7e0c264e0..175f0c8b9`; checkout HEAD was `175f0c8b9`.
- Review branch: `ops/2026-11-08-offload-review-sol2` (already present and clean
  at intake). Local commit only; no push.
- Authority: `AIR-OFFLOAD-AGREEMENT.md` items 1–9, `AIR-OFFLOAD.md`, and the
  brief's one-pack and terminal-closure rulings. Repository preflight found no
  active stop card. This explicit review brief owns the task; coordination
  state was not edited or regenerated.
- Review artifacts only: this report and `tests/test_offload_review_sol2.py`.
  No production fixes were made. No further agents or consults were used.

## Findings requiring disposition

### F1 — HIGH: same-size duplicate files are deleted without proving identity

Location: `scripts/offload_window.py:1217`, particularly lines 1231–1239;
the journal's second pass at lines 1278–1281 does not repair the omission.

`--duplicate-root` is treated as a second tree of the same record. For these
roots, `_inventory` requires a regular file of the expected size, but ignores
both the expected digest and the source mtime. It journals the duplicate's
current mtime, so the later journal check proves only that these unverified
bytes have stayed unchanged since inventory.

Witness: `test_witness_different_same_size_duplicate_is_deleted`. A copied
record has one JSONL file replaced with different bytes of the same length.
The normal record is offloaded and the synthetic second copy confirmed.
Release returns `two_verified_copies`, reports no skipped entry, and deletes
the different file too. The verified Air tree contains the original bytes.
Neither receipt authorizes deletion of the unique duplicate bytes.

This needs only an operator selecting the wrong duplicate tree, or a duplicate
containing a same-size stale/revised file. It does not depend on preserving an
mtime or modifying a manifest. The size-only behavior existed at the review
base and survives in the newly introduced inventory/journal implementation;
this is an inherited defect, not a newly introduced regression.

Required correction: prove each duplicate file's digest against the bound
record before adding it to the deletion inventory, or disable duplicate-root
deletion. Preserve mismatches. Test both first release and journal resume.

### F2 — HIGH: release unconditionally deletes a replacement harvest pack

Location: `scripts/offload_window.py:1205`–1211; adoption records the external
`local_parts_dir` at line 989.

After checking receipts for window A, release unlinks the payload and extra
objects currently at A's remembered local pack path. It never checks their
current size, digest, or identity against A's sealed manifest, and these
objects are outside the raw-deletion journal. The consumed harvest pack is
caller-owned and may live outside the per-window offload state directory.

Witness: `test_witness_reused_harvest_pack_is_deleted_without_identity_check`.
After A is verified and its synthetic second copy confirmed, replace its
local `payload.tar.zst` and `MANIFEST.json` with different bytes, representing
a later window using the same harvest output directory. Releasing A deletes
both replacement objects and removes that directory. A's receipts prove
nothing about those bytes. The analogous legacy-parts witness also passes.

The new consumed-pack path expands the older unconditional parts cleanup to
an external harvest directory. Reusing an output directory while A waits for
its asynchronous second copy is a plausible operator/workflow mistake.
The witness proves deletion of unrelated bytes; it does not claim that a
particular production workflow has already reused this directory or lost its
new window's raw tree.

Required correction: bind local pack cleanup to the sealed object identities,
check every candidate before the first deletion, and preserve changed packs.
Include payload and transport-manifest cleanup in resumable deletion evidence.
An enforced unique, immutable pack directory per window is another possible
part of the correction; the current caller-supplied path has no such guard.

### F3 — MEDIUM: standalone release bypasses triage and the dwell margin

Location: `scripts/offload_window.py:2324`–2335, compared with the `run` wrapper
at lines 1422–1464 and `triage` at lines 1596–1616.

The runbook explicitly permits `release --state-root S --window-id K` by hand.
This command takes no `S/.lock`, writes no new start/span receipt, and has no
deadline when the optional lease is absent. `triage` therefore examines the
old `run` span and can approve a quiet start during or immediately after this
fresh receipt recheck and deletion activity.

Witness: `test_witness_cli_release_is_invisible_to_triage` invokes the actual
public CLI with only transport and host probe replaced by synthetic fakes.
The original run ended 600 seconds earlier; planned dwell is now 60 seconds
away. Triage passes inside the release transport callback, release succeeds,
the old span remains byte-identical, and triage still passes afterwards.
This is a sequential margin failure as well as a concurrent visibility gap.

`test_witness_arm_after_receipt_request_does_not_stop_deletion` additionally
shows the probe-only race: arming after the initial probe but during the
receipt call does not stop the subsequent unlinks. The runbook acknowledges
that the active probe is heuristic and the shared magistrate lock is not yet
wired. The race is supporting evidence, not a separate newly discovered
mutual-exclusion guarantee. The bare-release visibility gap is inherited;
the merged deadline/lease work leaves that supported command unprotected.

Required correction: put standalone release under the same activity lock,
start/end evidence and bounded deadline as run, with the 120-second margin.
Wire the shared loop lock/lease before claiming exclusion across arm/dwell
transitions; additional probe checks alone do not close the race.

## Other reviewed requirements

- **Receipts:** the normal release binds the fresh nonce, offload manifest,
  original Air receipt, second receipt and exact custody-object inventory.
  A replayed fresh response is refused before any raw deletion. Corrupted
  primary parts are rehashed at release and refused. No ordinary stale/replay
  acceptance bypass was found within the specified receipt protocol.
- **Second copy:** both workers hash copied objects; iCloud requires an
  evict/download/hash sequence, and the second-disk path checks separate UUIDs
  and disjoint physical stores. Release intentionally rereads the second
  receipt, without redownloading the cloud copy. Continued cloud retention
  after confirmation remains an operational assumption, not a new live check.
- **Volume binding:** setup installs the binding and marker as root-owned;
  `hello`, `stat`, `verify` and `receipts` re-probe the volume UUID. The new
  witness switches the fake UUID immediately before release and gets
  `store_volume_uuid_mismatch`, with all raw files kept. Put/commit use the
  lighter mounted/marker checks, but deletion still requires the full receipts
  check. No accidental replacement-volume deletion path was demonstrated.
- **Consumed pack:** v2 refuses legacy repacking. Adoption checks the finalize
  pin, namespace, entries and declared transported externals. The Air derives
  the expected session entries from the pinned finalize manifest and checks
  every archive member. A new control prohibits calling `Offload.pack` and
  proves payload and `MANIFEST.json` reach the fake Air byte-for-byte unchanged.
  Payload corruption is refused. Existing v2 controls also cover another
  finalize pin, unbound externals, unexpected members and terminal closure.
- **Terminal evidence:** relative terminal files must belong to the envelope;
  absolute evidence must be byte-bound closure inputs. Missing, changed or
  unbound external markers refuse. Closure inputs outside the session are
  deliberately retained by this tool. I did not infer that every external
  closure file must be transported; the runbook permits some to remain out of
  the pack, and the actual harvest restore has additional host-closure checks.
- **Deadline in `run`:** monotonic budget, admission prediction, lease minimum
  minus 120 seconds, alarm interruption, process-group kill, and triage's
  overlap/crash checks passed focused synthetic tests. This does not validate
  real MBP rates, remote process teardown, or cooling behavior.
- **Confinement scripts, read only:** the Air script uses a dedicated
  non-admin account, root-owned gate/key/config, forced command, forwarding
  restrictions and no user rc. The MBP script pins the host fingerprint and
  retains an existing key; the transport ignores user SSH configuration.
  Neither setup script was executed, including syntax-only shell invocation.
  LOW documentation/scope discrepancy: Air setup lines 62–66 recursively
  chown `backups/` when its owner is uid 99; the runbook describes changing
  only that directory's owner. Review that metadata footprint before setup.
  Deliberate privileged modification of confinement files is outside the
  functional HOLD bound and is not an additional blocker here.

## Verification and limits

All records and stores were synthetic temporary trees. Transport and volume
identities were faked, except the existing LocalTransport control: it runs the
gate as a local subprocess and verifies refusal of an unmounted temporary
store. There was no SSH, sudo, network, model download, measurement,
analysis pipeline, real offload store access or real restricted-directory
access. Absolute study paths in source were treated as text. The only writes
under the SSD mount were the requested clone artifacts and its Git metadata.

Commands and observed results:

```text
python3.13 -B -m unittest -v tests.test_offload_review_sol2
  9 tests, OK, 1.774 s (final witness run; no skips)

python3.13 -B -m unittest tests.test_offload_window.HappyPath tests.test_offload_window.Envelope tests.test_offload_window.FinalizedManifestV2 tests.test_offload_window.Terminal tests.test_offload_window.Interlock tests.test_offload_window.StoreBinding tests.test_offload_window.Deadline tests.test_offload_window.TwoCopyRule tests.test_offload_window.DeletionJournal tests.test_offload_window.SecondDisk tests.test_offload_window.LocalTransport
  80 tests, OK, 6.643 s

python3.13 -B -m unittest tests.test_offload_bench
  1 test, OK, 0.059 s (generator shape only; no benchmark run)

python3.13 -B -c 'from pathlib import Path; p = Path("tests/test_offload_review_sol2.py"); compile(p.read_bytes(), str(p), "exec"); print("review witness compile: OK")'
  review witness compile: OK

git diff --cached --check
  OK
```

Tests ran one module per process. The full repository suite was deliberately
not run under the brief's machine-load restriction. The existing operator
script test was excluded so no setup script would be invoked; the existing
default host-probe test was not run against the user's home/process census.
The witness module's passing `test_witness_*` cases reproduce defects and
must be inverted into preservation/refusal checks after repair. They are not
safety passes. Targeted test runs took well under one minute in total.

Unverified native gates remain with the lead: reviewed setup installation,
the actual forced-command SSH permissions and host pin, real JW-EXT UUID and
ownership failure handling, one genuine iCloud placeholder round trip, and
magistrate lease/loop-lock/triage integration including standalone release.
No MLX code changed and no MLX test was required. None of these native checks
was attempted on the busy machine during this review.

Next exact step: the lead should disposition F1–F3, repair or explicitly remove
the affected deletion/release paths, and rerun these witnesses as safety
regressions plus the focused offload checks before an operational admission.
No scope expansion or contract ruling was needed to complete this review.
