# R17 harvest-off review — Sol seat 1

Date: 2026-11-08. Candidate: `720398640` (`origin/align/2026-11-08-harvest-off-merged`).
Review branch: `harvest-off-review`. Authority: the task brief, R17 in
`origin/main:RUN_STATE.md` item 228, `HARVEST-OFF-MERGED.md`,
`HARVEST-OFF-AGREEMENT.md`, and `origin/main:docs/perf/SPEED-TOOLBOX.md`.

**Verdict: HOLD for the production route.** Preserve the off-MBP design and its
measured speed work. The reasons for HOLD are custody and an executable R17
finality bypass, not a demand for more performance evidence or process gates.
Product fixes remain with the integration lead; this branch changes witnesses
and this report only.

## Findings requiring disposition

**F1 — HIGH: record-bound transport authenticates link text, not external input
bytes.** `joulewise/align/apple/harvest_offload.py:70` inventories links with
`os.readlink`; pack/unpack/verify never authenticate their target content. The
witness finalizes a synthetic session with an absolute directory link, packs it,
changes an external journal from `MBP bytes` to `Air bytes`, and restores using
the original finalized digest. Both unpack and `verify_tree` succeed, while a
consumer reads the changed bytes. This directly limits the advertised manifest
closure. It is not a demonstration that tracked code can defeat the CLI's Git
mirror checks. The real measurement view intentionally links code, `.venv`,
`runs`, and kit inputs (`scripts/bytes_h_session.py:113`); Git identity alone does
not inventory ignored runtime/data content or historical custody dependencies.

Fix: retain literal links, but bind the finite set of required external input
bytes to finalize and verify their Air copies, or authenticate each dependency
through a separately bound mirror inventory. Refuse dependencies outside that
closure. Do not indiscriminately traverse links or copy model weights.

**F2 — HIGH at the production boundary: record binding is optional.**
`scripts/align_v4_harvest_off.py:300` and `:303` make all finalized-manifest
arguments optional; `harvest_offload.unpack:243` skips the committed-digest
branch when both are absent. A CLI witness, with a matching synthetic checkout
identity, successfully packs and restores without any record-bound manifest.
The documented command with all arguments does verify regular-file content;
the operational boundary also accepts the unsafe omission. The new manifest
digest is not a required field in `WindowRecord` either. Fix the production CLI
and record writer to require the committed binding; a separately named
synthetic/legacy library seam can remain optional.

**F3 — HIGH: the k+2 finality deadline excludes test windows.**
`scripts/align_v4_next_arm_packet.py:735` calls `eligibility()` only for
calibration history. At `:780`, every other history row is assigned
`status: final` without checking for a final desk. The witness creates eight
completed calibration windows with 7/7 eligible counts each, then T1 and T2,
both provisional and with no T1 `previous_final`. The actual frozen-series
binder accepts the T3 packet with a digest-bound threshold-freeze receipt;
the arm's packet rebuild and cadence evaluation also admit it. T1 is printed as final in
`series_history`, although its committed record lacks PILOT and exclusions.
This violates R17's unqualified window-k deadline and its at-most-one unfinished
window bound. Fix finality validation for every applicable window in the hash
chain; preserve zero calibration contribution from test windows.

**F4 — HIGH: the presence of files is accepted as completed final adjudication.**
`WindowRecord.is_final()` at `scripts/align_v4_next_arm_packet.py:177` checks
only for `pilot` and `exclusions` source names (or any `final_from`). An older
C1 with those sources but a desk explicitly marked `running_off_mbp` is counted
as final, and the C2-to-C3 packet admits. The focused witness keeps W1 as the
honest last-passed desk, confirms that C1 releases C2, and passes both actual
series binders before exposing the C3 admission. This is a stale-output/partial-record
case, not a forged packet. `cmd_final` already refuses an unfinished harvest,
but the packet builder does not require evidence that went through that gate.
Require a completed, window/plan-bound harvest and final adjudication for own
sources and successor `previous_final` sources. A completed non-passing desk
must still be representable; this is not a request to impose full-desk PASS at
every arm.

**F5 — MEDIUM: auto sizing does not enforce its memory bound.**
`auto_workers` at `scripts/align_v4_harvest_off.py:198` clamps the memory limit
to at least one worker. For the documented 1 GiB member / 8 GiB peak and only
2 GiB available, it launches one worker requiring 12 GiB including reserve.
`_sweep_peak:214` also accepts a failed run reporting a 1 MiB child peak, with
no schema, exit, input-size, session, or code binding. A stale tiny sweep can
therefore replace the 8x fallback for a large window. Refuse/postpone when no
worker fits, reject failed/nonpositive sweep measurements, and bind or
conservatively scale a sweep to the current input size and code. No 1 GiB
allocation or native memory stress was run here. Darwin descendant-RSS
accounting, purgeable-page accounting, and the real memory ratio remain native
checks, not facts established by these integer witnesses.

**F6 — LOW, not an arm bypass: light triage labels inconclusive thermal evidence
as pass.** `light_triage.thermal_escalation:59` only looks for literal `fail`.
Three `inconclusive` statuses produce `status: pass` and
`escalation_required: false`, while all three booleans in `checks` are false.
The packet builder correctly treats non-pass U statuses as requiring the
registered consequence, so this does not independently authorize an arm.
Align the diagnostic status with that consumer. The light/full U1–U3 equality
itself passed adversarial record and raw-journal checks (see below).

**F7 — MEDIUM, inherited integration issue: the recorded dwell begins before
Git work ends.** `scripts/align_v4_session.py:568` records `dwell_start_ns`, then
`:587` calls `_commit_exists` and `_record_bound` (four Git subprocesses in
total). The new witness records the order as `dwell`, `git commit check`,
`git record binding`, with the arm admitted. `_arm_and_install` subsequently
does series binding, record writes and the disk gate. Existing meter tests prove
that its probe ends before this marker; they do not prove a quiet interval.
Finish disruptive checks before starting the actual R16 dwell, or restart the
quiet clock after that work. This witness addresses the recorded boundary;
it does not establish the timing of a live installed dwell. No live MBP check
was performed.

**F8 — MEDIUM, required before reduced artifacts become analysis inputs: the
turn table omits clock-evidence metadata from its input binding.**
`turn_table.INPUT_FILES` omits `metadata.json`, although
`workload.read_episode_bundle:898` reads it to construct clock mappings and
trace uncertainty for both desk energy readers. The synthetic real-desk
end-to-end comparison proves table equality, then the witness fails because
the table does not bind that input. Include every input used by the energy
projection, starting with metadata. Also note that `reduce` does not itself
call `equal_to_pilot`; the downstream switch still needs the agreement's
equivalence gate. I did not demonstrate a divergent numeric result from a
metadata mutation, or inspect any live analysis output.

## What passed

- **177-file equality independently repeated:** a synthetic six-member window,
  finalized manifest bound by digest, verified restore at the identical absolute
  path, serial MBP path with memo disabled, Air path with three member workers,
  memo enabled and two I/O threads. Every archive file's bytes and the entire
  `harvest.json` result matched. Clocks, boot and checkout provenance were pinned;
  historical external custody probes were fenced to absence on both sides.
  This is a software replay proof, not a cross-host/live N2 receipt.
- Changed regular-file content fails packing against finalize. Relocation is
  refused; byte-exact same-path restore succeeds.
- A stale provisional **calibration** record fails the k+2 gate. A previous
  provisional record fails when a code/config change makes the full desk due.
  A finally excluded old C1 member retained in the pool is refused.
- The content-SHA memo handles changed bytes, nested member scopes, mutable
  returned objects, and consecutive member scopes correctly. Repeated parse
  refusals reparse and never enter the memo. No stale hit or cross-member leak
  was found. The memo's parsed-content exception is expressly authorized by R17;
  no decision cache or measured-episode batching was introduced.
- Light and full U1–U3 and `thermal_escalation` match with harvest battery/clock/
  strict-invalid codes, thermal timeouts, dead collectors and nonnominal flags.
  Raw-journal cases include empty journals, duplicate gate-exit samples, wrong
  release temperatures and sparse coverage, using the actual member builder.
- Real desk PILOT per-turn tables equal the reduce-once tables on three tiny
  fake-native bundles, including thermal owned energy and per-channel segments.
  The stock altered-PILOT comparison also detects a changed per-turn value.

## Verification and execution limits

All commands are local; no network, model download, live pipeline, live
measurement command, or production-job control was requested. Python 3.13,
`-B`, realpath `TMPDIR=/private/tmp`, `JW_WP22_FULL=1`, and
`JW_B5_SYNTHETIC_ONLY=1` were used. No full suite was run, per the brief.
The new witnesses deliberately assert required properties and remain failing
on the reviewed product code; they are not marked expected-failure.

Commands/results (environment above; one module per process):

| Command / selection | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_v4_next_arm_packet` | 34 OK, 148.548 s |
| `python3.13 -B -m unittest -v tests.align.test_harvest_off_review_sol1` | 17 run, 8 pass / 9 contract-witness failures, zero errors, 68.809 s |
| Same module, selection `EligibilityWitnesses.test_final_sources_must_prove_a_completed_harvest` after adding honest last-passed/binder controls | 1 contract-witness failure, zero errors, 4.226 s |
| Stock `tests.align.test_harvest_off`, with custody fence below | 30 OK, 75.906 s |
| `tests.test_harvest_off_io`, using the same guarded driver | 4 OK, 12.274 s |
| Parse the new witness with `ast.parse` | OK |
| `git diff --check` and staged diff check | OK |

The nine failures map to F1, F2, F3, F4, two F5 cases, F6, F7 and F8. The F3
failure occurs **after** the actual series binder accepts the rebuilt packet.
The 177-file equality and raw-journal equality tests pass. During witness
development I corrected two test-fixture errors (sensor-key enumeration and
the threshold receipt's absolute path/JSON pointer); the final run has no
fixture errors. Earlier development runs are not substituted for this result.

The safe, spawn-compatible stock-module command is:

```sh
TMPDIR=/private/tmp JW_B5_SYNTHETIC_ONLY=1 JW_WP22_FULL=1 \
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 python3.13 -B \
  /private/tmp/harvest-off-review-sol1-guarded.py tests.align.test_harvest_off
```

The scratch driver imports `synthetic_custody_only` from the committed witness
module, and under `if __name__ == '__main__'` runs
`unittest.main(module=sys.argv[1], argv=[sys.argv[0], *sys.argv[2:]])` inside
that context. It inserts the clone's working directory in `sys.path`. The
first guarded attempt used stdin as `__main__`, which Python's spawn workers
cannot reopen; its two failures/two errors are launch artifacts and that run
is superseded by the named-driver rerun.

The complete witness log is `/private/tmp/harvest-off-review-sol1-witness-verified.log`;
the later F4 control rerun is `/private/tmp/harvest-off-review-sol1-finality-verified.log`;
the guarded stock log is `/private/tmp/harvest-off-review-sol1-baseline-verified.log`.
These scratch logs contain synthetic witness output and are not custody
evidence. Local commit receipts are in the final handoff.
Aggregate unittest runtime, including development and superseded launches, was
about 11.5 minutes (under the 20-minute limit).

**Safety/process limitation:** the first stock `tests.align.test_harvest_off`
run was started with `JW_B5_SYNTHETIC_ONLY=1`, before I recognized that its
historical-custody code still probes the fixture ledger's absolute locators.
That environment flag only disables the optional native decorators. I cannot
attest that the initial run made zero forbidden filesystem probes, and do not
use it as blinded custody evidence. No real outcomes were surfaced in its
output. The independent 177-file witness and subsequent fixture reruns use
`synthetic_custody_only()` to return no candidate paths before any external
`/Users/edr` custody probe. I also briefly overlapped the first two targeted
module processes; subsequent test processes were sequential. These are review
execution deviations, not properties of R17.

## Handoff

The lead's next step is to fix F1–F4 and rerun these witnesses on the merged
candidate; resolve F5/F7 before native scheduling relies on them, and F8 before
switching analysis to reduced artifacts. F6 is diagnostic and need not hold the
offload design. Keep the existing native smoke/N1/N2 and appropriately sized Air
RSS sweep/N4/N5 gates, N6's pack/quiet-boundary check, and N9's reduced-result
equivalence before the analysis switch. Establish host routing and an actually quiet dwell there;
the standalone CLI is manually routed and does not enforce an Air host identity.
No native MLX/Metal, live byte comparison, 1 GiB-member memory measurement,
MBP-minutes saving, or quiet-window scheduling was validated in this sandbox.

Only `tests/align/test_harvest_off_review_sol1.py` and this report are changed.
Coordination state, sealed evidence, product code, registration and kernel tasks
are untouched. No commit was pushed.
